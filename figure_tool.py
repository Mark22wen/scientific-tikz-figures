"""Standalone TikZ/PDF checks. Exit: 0 mechanical pass, 1 fail, 2 review.
Science and visual layout require review.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

def issue(level, code, message, **extra):
    return dict(level=level, code=code, message=message, **extra)

def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Expected positive finite number.")
    return number

def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Expected integer >= 0.")
    return number

def positive_int(value):
    number = nonnegative_int(value)
    if number == 0:
        raise argparse.ArgumentTypeError("Expected integer > 0.")
    return number

def raster_dpi(value):
    number = int(value)
    if not 72 <= number <= 1200:
        raise argparse.ArgumentTypeError("DPI range: 72..1200.")
    return number

def recorder_inputs(path, cwd):
    inputs = set()
    if not path.is_file():
        return inputs
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("INPUT "):
            name = line[6:].strip().strip('"')
            candidate = Path(name)
            if not candidate.is_absolute():
                candidate = Path(cwd) / candidate
            if candidate.is_file():
                inputs.add(str(candidate.resolve()))
    return inputs

def uncomment(text):
    return re.sub(r"(?<!\\)%[^\n]*", "", text)

def source_checks(source):
    files, findings, seen, texts = [], [], set(), []
    compile_directory = Path(source).resolve().parent

    def read(path, depth=0):
        path = path.resolve()
        if path in seen or depth > 8:
            return
        seen.add(path)
        file_info = dict(path=str(path), sha256=None)
        files.append(file_info)
        try:
            data = path.read_bytes()
            file_info["sha256"] = hashlib.sha256(data).hexdigest()
            raw = data.decode("utf-8-sig")
        except (OSError, UnicodeError) as exc:
            findings.append(issue("error", "source-read-failed", str(exc), file=str(path)))
            return ""
        text = uncomment(raw)
        if '\ufffd' in text:
            findings.append(issue("error", "replacement-character", "U+FFFD in source; restore the intended character.", file=str(path)))
        texts.append(text)
        pattern = r"\\(?:node|coordinate)\s*(?:\[[^\]]*\]\s*)?\(([^()]+)\)"
        for match in re.finditer(pattern, text):
            name = match.group(1).strip()
            if re.search(r"[.,:]", name):
                findings.append(issue("error", "ambiguous-node-name",
                    f"Ambiguous node '{name}'; avoid coordinate punctuation.",
                    file=str(path), line=text[:match.start()].count("\n") + 1))
        for match in re.finditer(r"\\(?:input|include)\b\s*(?:\{([^{}\n]+)\}|([^\s%{}]+))", text):
            name = match.group(1) or match.group(2)
            if any(char in name for char in "\\#$"):
                continue
            target = compile_directory / name
            if not target.suffix:
                target = target.with_suffix(".tex")
            if target.is_file():
                read(target, depth + 1)
        return text

    root = read(Path(source))
    all_text = "\n".join(texts)
    if "unicode-math" in all_text and re.search(r"\\(?:boldsymbol|bm)\b", all_text):
        findings.append(issue("review", "legacy-bold-with-unicode-math",
            "Review boldsymbol/bm with unicode-math. Preserve notation; use symbfup/symbfit for appropriate symbols."))
    if root is not None and "\\documentclass" not in root:
        findings.append(issue("note", "fragment", "Fragment: supply a complete document before compilation."))
    return dict(files=files, findings=findings,
                scope="Literal node/coordinate definitions and local inputs only; no macro expansion or full TeX parsing.")

def log_checks(logtext):
    findings = []
    rules = [
        ("error", "missing-glyph", r"Missing character:[^\n]*"),
        ("review", "undefined-font-shape", r"Font shape[^\n]*(?:\n[^\n]*){0,2}?undefined[^\n]*"),
        ("review", "font-shape-substitution", r"Some font shapes were not available[^\n]*"),
        ("review", "overfull-box", r"Overfull \\[hv]box[^\n]*"),
        ("review", "unresolved-reference", r"(?:Reference|Citation) [^\n]*undefined[^\n]*|There were undefined (?:references|citations)[^\n]*"),
        ("review", "rerun-required", r"Rerun to get [^\n]*right[^\n]*|Please \(re\)run (?:Biber|BibTeX)[^\n]*"),
        ("note", "font-fallback", r"[^\n]*(?:fallback|Requested math font unavailable)[^\n]*"),
        ("error", "tex-error", r"^! (?:LaTeX|Package|Undefined|Emergency|Fatal)[^\n]*"),
    ]
    for level, code, pattern in rules:
        for match in re.finditer(pattern, logtext, re.MULTILINE | re.IGNORECASE):
            findings.append(issue(level, code, re.sub(r"\s+", " ", match.group(0)).strip()))
    declared = re.findall(r"^FIGURE-(CJK|LATIN|MATH)-FONT:\s*(.*)$", logtext, re.MULTILINE)
    return dict(findings=findings, declared_fonts=dict(declared))

def inspect_pdf(path, args, output_dir=None):
    findings = []
    try:
        import ctypes
        import pypdfium2 as pdfium
        import pypdfium2.raw as raw
    except ImportError:
        return dict(available=False, findings=[issue("review", "pdf-check-unavailable",
                    "pypdfium2 missing; PDF/PNG unverified.")])
    pdf = pdfium.PdfDocument(path)
    pages, font_items, previews, extracted = [], {}, [], []
    if args.expected_pages and len(pdf) != args.expected_pages:
        findings.append(issue("error", "page-count", f"Expected {args.expected_pages} pages; got {len(pdf)}."))
    for index in range(len(pdf)):
        number, page = index + 1, pdf[index]
        width_pt, height_pt = page.get_size()
        width, height = width_pt * 25.4 / 72, height_pt * 25.4 / 72
        for key, value, limit in [("width", width, args.max_width_mm), ("height", height, args.max_height_mm)]:
            if limit is not None and value > limit + 0.1:
                findings.append(issue("error", "canvas-limit", f"Page {number} {key} {value:.3f} mm > {limit} mm + 0.1 tolerance."))
        sizes, outside = [], []
        bounds = page.get_bbox()
        with closing(page.get_textpage()) as textpage:
            extracted.append(textpage.get_text_range(errors="replace"))
            for char_index in range(textpage.count_chars()):
                codepoint = raw.FPDFText_GetUnicode(textpage, char_index)
                if not codepoint or chr(codepoint).isspace():
                    continue
                size = raw.FPDFText_GetFontSize(textpage, char_index)
                if size > 0:
                    sizes.append(size)
                box = textpage.get_charbox(char_index)
                if box[0] < bounds[0]-1 or box[1] < bounds[1]-1 or box[2] > bounds[2]+1 or box[3] > bounds[3]+1:
                    if len(outside) < 20:
                        outside.append(dict(character=chr(codepoint), bbox=list(box)))
        if outside:
            findings.append(issue("review", "text-bounds", f"Page {number}: text beyond page bounds; review cropping.", spans=outside))
        if args.min_text_pt is not None and sizes and min(sizes) * 72.27 / 72 < args.min_text_pt - 0.05:
            findings.append(issue("review", "small-text", f"Page {number}: minimum text {min(sizes)*72.27/72:.2f} TeX pt; review math scripts."))
        images, paths = 0, 0
        for obj in page.get_objects(max_depth=15):
            images += obj.type == raw.FPDF_PAGEOBJ_IMAGE
            paths += obj.type == raw.FPDF_PAGEOBJ_PATH
            if obj.type == raw.FPDF_PAGEOBJ_FORM and obj.level >= 14:
                findings.append(issue("review", "object-depth-limit", "Deep form: object counts incomplete."))
            if obj.type != raw.FPDF_PAGEOBJ_TEXT:
                continue
            font = raw.FPDFTextObj_GetFont(obj)
            length = raw.FPDFFont_GetBaseFontName(font, None, 0)
            buffer = ctypes.create_string_buffer(length or 1)
            raw.FPDFFont_GetBaseFontName(font, buffer, len(buffer))
            name = buffer.value.decode("utf-8", errors="replace") or "unknown"
            embedded = raw.FPDFFont_GetIsEmbedded(font)
            key = (name, embedded)
            if key not in font_items:
                font_items[key] = dict(name=name, embedded=embedded == 1, embedding_flag=embedded)
                if embedded != 1:
                    findings.append(issue("review", "font-not-embedded", f"Font {name}: embedding flag {embedded}."))
        pages.append(dict(page=number, width_mm=round(width, 4), height_mm=round(height, 4), rotation=page.get_rotation(),
                          minimum_text_tex_pt=round(min(sizes)*72.27/72, 3) if sizes else None,
                          raster_image_count=images, vector_path_count=paths))
        if args.render and output_dir and number <= 8:
            preview = Path(output_dir) / f"page-{number:02d}.png"
            dpi = args.render_dpi
            pixels = math.ceil(width_pt*dpi/72)*math.ceil(height_pt*dpi/72)
            if pixels > 40_000_000:
                findings.append(issue("error", "raster-budget", f"Page {number}: exceeds 40 megapixels; reduce DPI/canvas."))
            else:
                try:
                    from PIL import Image
                    with closing(page.render(scale=dpi/72)) as bitmap:
                        with bitmap.to_pil() as png:
                            png.save(preview, dpi=(dpi, dpi))
                    previews.append(str(preview))
                except ImportError:
                    findings.append(issue("review", "png-unavailable", "Pillow unavailable; PNG not rendered."))
        page.close()
    if args.render and len(pdf) > 8:
        findings.append(issue("review", "preview-page-limit", "Only eight pages rendered."))
    names = "\n".join(f["name"] for f in font_items.values()).casefold()
    for required in args.require_font:
        if required.casefold() not in names:
            findings.append(issue("error", "required-font-absent", f"Required font substring absent: {required}."))
    text_content = "\n".join(extracted)
    han_count = sum(1 for ch in text_content if '\u3400' <= ch <= '\u4dbf' or '\u4e00' <= ch <= '\u9fff' or '\U00020000' <= ch <= '\U0003134f')
    latin_count = len(re.findall(r"[A-Za-z]", text_content))
    language = args.language
    if language:
        if not text_content.strip():
            findings.append(issue("review", "language-unverifiable", "No extractable text; language unverified."))
        elif language == "en" and han_count:
            findings.append(issue("error", "unexpected-cjk", f"English-only PDF contains {han_count} Han characters."))
        elif language in ("zh", "bi") and not han_count:
            findings.append(issue("error", "expected-cjk-absent", "No Han characters in extracted text."))
        if language == "bi" and text_content.strip() and not latin_count:
            findings.append(issue("review", "bilingual-latin-absent", "Review missing Latin labels."))
    if '\ufffd' in text_content:
        findings.append(issue("review", "text-decoding-uncertain", "Text decoding uncertain; review glyphs and language."))
    pdf.close()
    return dict(available=True, pages=pages, fonts=list(font_items.values()), findings=findings,
                previews=previews, visual_review_required=True,
                language_screen=dict(expected=language, han_characters=han_count, latin_characters=latin_count,
                                     scope="Character screen; review translations visually."),
                backend="pypdfium2", limitations="Depth 15; embedding flags only. Review science/layout and patterns/annotations.")

def run_directory(base):
    base = Path(base).resolve()
    base.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("run-%Y%m%d-%H%M%S-")
    return Path(tempfile.mkdtemp(prefix=stamp, dir=str(base)))

def local_environment(run):
    env = os.environ.copy()
    scratch = (run / "temp").resolve()
    scratch.mkdir(exist_ok=True)
    for key in ("TMPDIR", "TEMP", "TMP"):
        env[key] = str(scratch)
    env["PYTHONIOENCODING"] = "utf-8"
    return env

def execute(command, cwd, run, timeout, output_name="process-output.txt"):
    try:
        process = subprocess.run(command, cwd=cwd, env=local_environment(run),
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=timeout, shell=False)
        output = process.stdout.decode("utf-8", errors="replace")
        status = dict(command=command, returncode=process.returncode, timeout=False)
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode("utf-8", errors="replace")
        status = dict(command=command, returncode=None, timeout=True)
    (run / output_name).write_text(output, encoding="utf-8")
    return status

def finalize(report, target):
    findings = list(report.get("findings", []))
    for key in ("source", "log", "pdf"):
        findings.extend(report.get(key, {}).get("findings", []))
    report["status"] = ("failed" if any(f["level"] == "error" for f in findings) else
                        "review-required" if any(f["level"] == "review" for f in findings) else "mechanical-checks-passed")
    report["visual_review_required"] = True
    target = Path(target).resolve()
    protected = {Path(p).resolve() for p in report.get("protected_inputs", [])}
    protected.update(Path(f["path"]).resolve() for f in report.get("source", {}).get("files", []))
    protected.update(Path(p).resolve() for p in report.pop("_runtime_inputs", []))
    protected.add(Path(__file__).resolve())
    same_input = target in protected
    if not same_input and target.exists():
        for input_path in protected:
            try:
                if input_path.exists() and target.samefile(input_path):
                    same_input = True
                    break
            except OSError:
                continue
    if same_input:
        print(json.dumps(dict(status="failed", report=None, code="input-output-collision",
                              message=f"Report would overwrite input; refused: {target}"),
                         ensure_ascii=True))
        return 1
    temp_report = None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                         prefix=".figure-report-", suffix=".tmp", delete=False) as stream:
            temp_report = Path(stream.name)
            stream.write(json.dumps(report, ensure_ascii=False, indent=2))
        os.replace(temp_report, target)
    except OSError as exc:
        if temp_report and temp_report.exists():
            temp_report.unlink()
        print(json.dumps(dict(status="failed", report=None, code="report-write-failed", message=str(exc)), ensure_ascii=True))
        return 1
    print(json.dumps(dict(status=report["status"], report=str(target), findings=len(findings)), ensure_ascii=True))
    return {"failed": 1, "review-required": 2, "mechanical-checks-passed": 0}[report["status"]]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "build", "inspect"))
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, default=Path("figure-build"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--max-width-mm", type=positive_float)
    parser.add_argument("--max-height-mm", type=positive_float)
    parser.add_argument("--min-text-pt", type=positive_float)
    parser.add_argument("--expected-pages", type=nonnegative_int, default=1, help="0: no page-count check")
    parser.add_argument("--language", choices=("zh", "en", "bi"), help="Character screen only")
    parser.add_argument("--require-font", action="append", default=[], help="Required font substring; repeatable")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--render-dpi", type=raster_dpi, default=150,
                        help="72..1200; 150 preview default")
    parser.add_argument("--timeout", type=positive_int, default=120)
    parser.add_argument("--passes", type=int, choices=(1, 2), default=1,
                        help="XeLaTeX passes (2 for references)")
    args = parser.parse_args()
    source = args.source.resolve()
    report = dict(mode=args.mode, input=str(source), findings=[],
                  png_dpi=args.render_dpi if args.render else None,
                  protected_inputs=[str(source)] + ([str(args.log.resolve())] if args.log else []))
    target = args.report or args.out / "report.json"
    try:
        if not source.is_file():
            raise FileNotFoundError(str(source))
        if args.mode in ("preflight", "build"):
            report["source"] = source_checks(source)
        if args.mode == "inspect":
            run = run_directory(args.out)
            target = args.report or run / "report.json"
            report["run_directory"] = str(run)
            report["pdf"] = inspect_pdf(source, args, run)
            if args.log:
                report["log"] = log_checks(args.log.read_text(encoding="utf-8", errors="replace"))
        if args.mode == "build":
            if any(f["level"] == "error" for f in report.get("source", {}).get("findings", [])):
                report["findings"].append(issue("error", "preflight-blocked", "Source error; build skipped."))
                return finalize(report, target)
            run = run_directory(args.out)
            target = args.report or run / "report.json"
            report["run_directory"] = str(run)
            engine = shutil.which("xelatex")
            if not engine:
                raise RuntimeError("XeLaTeX missing from PATH.")
            command = [engine, "-no-shell-escape", "-recorder", "-interaction=nonstopmode", "-halt-on-error",
                       f"-output-directory={run}", source.name]
            report["processes"] = []
            for pass_number in range(1, args.passes + 1):
                output_name = (f"process-output-pass-{pass_number}.txt" if args.passes > 1
                               else "process-output.txt")
                report["process"] = execute(command, source.parent, run, args.timeout, output_name)
                report["processes"].append(dict(pass_number=pass_number, **report["process"]))
                if report["process"]["returncode"] != 0:
                    break
            if report["process"]["returncode"] != 0:
                report["findings"].append(issue("error", "process-failed", "Build failed/timed out; see process-output*.txt."))
            runtime_inputs = recorder_inputs(run / (source.stem + ".fls"), source.parent)
            report["_runtime_inputs"] = sorted(runtime_inputs)
            report["recorded_input_count"] = len(runtime_inputs)
            log = run / (source.stem + ".log")
            if log.exists():
                report["log"] = log_checks(log.read_text(encoding="utf-8", errors="replace"))
            pdf = run / (source.stem + ".pdf")
            if report["process"]["returncode"] == 0 and pdf.exists():
                report["pdf_path"] = str(pdf)
                report["pdf"] = inspect_pdf(pdf, args, run)
            elif report["process"]["returncode"] == 0:
                report["findings"].append(issue("error", "pdf-missing", "Compiler produced no expected PDF."))
    except (OSError, ValueError, RuntimeError) as exc:
        report["findings"].append(issue("error", "tool-error", str(exc)))
    return finalize(report, target)

if __name__ == "__main__":
    raise SystemExit(main())
