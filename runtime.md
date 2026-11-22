# Run the standalone helper

The marketplace helper imports only Python standard-library modules plus optional `pypdfium2` for PDF inspection and `Pillow` for PNG saving. It reads no neighbouring package modules or assets. The user's generated `.tex` must incorporate the font fragment and other needed content, rather than point to a nonexistent installed skill folder.

Load the exact helper source through the marketplace resource mechanism, execute it unchanged from a temporary file according to the host's rules, and remove that temporary helper afterwards. Keep the generated figure, caption and review evidence as work products. Do not save the skill itself or use an external download workaround.

Example arguments below use placeholders for task-local paths; do not run them literally:

```text
python <temporary-helper.py> preflight <figure.tex> --report <preflight.json>
python <temporary-helper.py> build <figure.tex> --out <new-build-folder> --language en --max-width-mm 160 --render --render-dpi 600
python <temporary-helper.py> inspect <figure.pdf> --out <new-review-folder> --language en --require-font TimesNewRoman --render --render-dpi 600
```

`build` invokes XeLaTeX with shell escape disabled, records actual inputs and preserves compilation evidence in a new run directory. The default process timeout is 120 seconds. `--passes 2` is available for genuine internal references. It does not install software or retry indefinitely. Compile only trusted author-approved source; these options do not isolate malicious TeX from local files.

`inspect` checks page dimensions, actual font names and PDFium-reported embedding flags, text bounds, extractable minimum text size, raster-image and vector-path counts, and optional language character presence. Outlined text cannot be validated as ordinary extracted text. Fonts can have different names in PDF metadata; `--require-font` performs a substring match and should name only a font actually expected to appear.

Exit 0 means the performed mechanical checks passed. Exit 1 means failure. Exit 2 means review or partial verification (including missing pypdfium2); argument parsing errors also use exit 2 with an error message and no success report. Read the structured report and log instead of using the exit code alone. All actual figures still need visible layout and scientific-content review.

Render output defaults to 150 dpi. `--render-dpi 600` requests 600 dpi without changing PDF geometry. Values outside 72–1200 are rejected, and a page over 40 megapixels at the requested resolution is rejected before bitmap allocation. This helps bound local export cost; it is not a hosted service resource-isolation system.

If XeLaTeX is missing, report that the source was not compiled. If PDF inspection is unavailable, do not claim fonts, vector structure or PNG output were verified. If a report path collides with an input, the helper refuses to overwrite it. Do not publish logs or reports containing private local paths as listing screenshots.

Counts cover page-content objects and nested forms through 15 levels. Deep forms trigger review. Patterns, annotations and outlined text require visual review; zero counted raster objects is not a universal proof about arbitrary third-party PDFs. Bitmap dimensions use the rotated page size; text bounds use native crop/media coordinates. Embedding flags describe technical presence, not font-use rights.

Use the tested dependency versions listed in [requirements.txt](../requirements.txt). Dependency installation is a host/user setup action, not an action the helper performs. Never treat an import-only probe as a successful render.
