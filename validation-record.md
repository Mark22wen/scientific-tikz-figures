# Marketplace v1.0.0 validation

Checked 2026-11-17: 38 local checks passed (15 normal, 11 boundary, 12 failure).
Four diagram examples and one academic-symbol proof sheet were compiled. The assistant visually reviewed the resulting diagrams and symbol sheet; this is not an external human blind test.

Environment: Windows; Python 3.13.13; TeX Live 2026; pypdfium2 5.9.0; Pillow 12.2.0. PDFium performs the shipped inspection/rendering. A separate local PDF engine and Poppler previews were used as additional audit tools; neither is included in the package.

| Check | Type | Input | Expected | Actual |
|---|---|---|---|---|
| helper-alone | normal | Only helper source in isolated directory. | Runs without sibling imports/assets. | PASS; exit 0 |
| example-en-build | normal | en source, 160 mm, 600 dpi. | Compile, inspect and render; preserve genuine review flags. | PASS; exit 0 |
| example-en-independent-inspection | normal | PDF plus PNG checked with separate PDF engine. | Vector content, embedded fonts, correct size and PNG DPI. | PASS; 3780 x 2079 px; 600.079 effective dpi |
| example-principle-bi-build | normal | bi source, 148 mm, 600 dpi. | Compile, inspect and render; preserve genuine review flags. | PASS; exit 2 |
| example-principle-bi-independent-inspection | normal | PDF plus PNG checked with separate PDF engine. | Vector content, embedded fonts, correct size and PNG DPI. | PASS; 3497 x 2410 px; 600.157 effective dpi |
| example-workflow-zh-build | normal | zh source, 85 mm, 300 dpi. | Compile, inspect and render; preserve genuine review flags. | PASS; exit 0 |
| example-workflow-zh-independent-inspection | normal | PDF plus PNG checked with separate PDF engine. | Vector content, embedded fonts, correct size and PNG DPI. | PASS; 1004 x 674 px; 300.025 effective dpi |
| example-loop-en-build | normal | en source, 150 mm, 600 dpi. | Compile, inspect and render; preserve genuine review flags. | PASS; exit 2 |
| example-loop-en-independent-inspection | normal | PDF plus PNG checked with separate PDF engine. | Vector content, embedded fonts, correct size and PNG DPI. | PASS; 3544 x 3355 px; 600.127 effective dpi |
| symbol-coverage-build | normal | bi source, 181 mm, 600 dpi. | Compile, inspect and render; preserve genuine review flags. | PASS; exit 2 |
| symbol-coverage-independent-inspection | normal | PDF plus PNG checked with separate PDF engine. | Vector content, embedded fonts, correct size and PNG DPI. | PASS; 4252 x 3094 px; 600.0 effective dpi |
| academic-symbol-extraction | normal | Greek, calculus, set, statistical and algebraic proof sheet. | No missing glyphs, replacement characters or substituted question marks; sample mappings preserved. | PASS |
| absent-font | boundary | ["--require-font", "DefinitelyMissingTypeface"] | required-font-absent | PASS; exit 1 |
| wrong-language | boundary | ["--language", "zh"] | expected-cjk-absent | PASS; exit 1 |
| canvas-limit | boundary | ["--max-width-mm", 50] | canvas-limit | PASS; exit 1 |
| page-count | boundary | ["--expected-pages", 2] | page-count | PASS; exit 1 |
| minimum-text | boundary | ["--min-text-pt", 15] | small-text | PASS; exit 2 |
| unexpected-han | failure | Bilingual PDF as English. | Reject Han labels. | PASS; exit 1 |
| missing-pdfium | boundary | No site packages. | Partial verification. | PASS; exit 2 |
| missing-pillow | boundary | PDF engine present, image saver absent. | Inspection retained, PNG explicitly unverified. | PASS; exit 2 |
| invalid-dpi-0 | failure | 0 | CLI rejection. | PASS; exit 2 |
| invalid-dpi-1201 | failure | 1201 | CLI rejection. | PASS; exit 2 |
| invalid-dpi-nan | failure | nan | CLI rejection. | PASS; exit 2 |
| preserve-input | failure | Report path equals PDF input. | Reject without mutation. | PASS; exit 1 |
| corrupt-pdf | failure | Invalid PDF bytes. | Structured failure. | PASS; exit 1 |
| rotated-bounds | boundary | rotated page. | Native text bounds and rotated image dimensions handled. | PASS; exit 0 |
| cropped-bounds | boundary | cropped page. | Native text bounds and rotated image dimensions handled. | PASS; exit 2 |
| raster-budget | failure | 1200pt square at 1200 dpi. | Reject before bitmap allocation. | PASS; exit 1 |
| raster-disclosure | normal | Vector figure with one bitmap. | Disclose raster instead of calling it pure vector. | PASS; exit 0 |
| font-embedding-warning | boundary | Standard nonembedded Helvetica. | Flag embedding review. | PASS; exit 2 |
| preview-limit | boundary | Nine-page PDF. | Render only first eight and disclose limit. | PASS; exit 2 |
| failed-compilation | failure | Undefined TeX command. | Fail with preserved log, no fabricated PDF. | PASS; exit 1 |
| missing-xelatex | failure | PATH without XeLaTeX. | Fail explicitly; no automatic install. | PASS; exit 1 |
| no-generic-execution | failure | Unsupported execution mode. | CLI rejection. | PASS; exit 2 |
| replacement-character-rejected | failure | U+FFFD in active source. | Reject corrupted source before build. | PASS; exit 1 |
| missing-glyph-rejected | failure | Unsupported codepoint in real XeLaTeX build. | Fail even if the compiler emits a PDF. | PASS; exit 1 |
| literal-question-preserved | normal | Intentional question mark. | Do not misdiagnose ordinary punctuation as a missing symbol. | PASS; exit 0 |
| english-font-override-no-cjk | normal | English-only, Arial override, unavailable Chinese font. | Use actual Arial without needing CJK fonts. | PASS; exit 0 |

## Visual findings

- example-en: Aligned parallel branches and clear orthogonal arrows; final merge concatenates matched windows. No clipped text observed. K and kPa remain distinct in the caption.
- example-principle-bi: Physical junctions, resistance labels, heat-rate arrows and bilingual labels checked. Equations and caption agree on steady-state positive resistances. Small math scripts are readable; Latin Modern Math fallback disclosed.
- example-workflow-zh: Three aligned Chinese action labels, even padding and clear downward arrows. No missing characters observed.
- example-loop-en: Decision question marks removed; conditions and Yes/No labels remain explicit. Both exits and the return to the update step are visible, without crossing nodes. Small math scripts reviewed.
- symbol-coverage: Greek variants, relations, calculus, probability, alphabets, arrows, accents, matrices and Chinese punctuation visually compared with source. No replacement boxes, substituted question marks or missing glyphs observed. Formula scripts remain smaller than body text.

All five output PDFs had embedded fonts and no observed embedded raster objects in both local PDF inspections. The actual primary Latin family was Times New Roman, Chinese labels used SimSun, and requested TeX Gyre Termes Math fell back to Latin Modern Math. An additional English override test used Arial without requiring a Chinese font.

The mechanical review-required flags for small mathematical scripts are retained. Visual acceptance of these examples does not lower the font-size requirements for future tasks or a particular journal.

## Scope and limits

The helper was tested as an isolated temporary script with no sibling modules or assets. Missing PDFium/Pillow/XeLaTeX, bad PDF data, missing fonts/glyphs, corrupted source, incorrect language, canvas limits and oversized raster requests were exercised. Intended punctuation is not treated as missing data.
Live marketplace loading/approval, other operating systems, an external human blind test and arbitrary unseen scientific briefs remain unverified. A finite academic-symbol sheet does not establish universal Unicode/font coverage. No publication-acceptance or scientific-validity guarantee follows.
