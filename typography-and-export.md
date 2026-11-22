# Typography, language and output

Author requirements override defaults. Chinese defaults to SimSun and Latin text to Times New Roman. Use the supplied font fragment inside the generated complete document. Set `\def\FigureLanguage{en}` before the fragment for English-only figures, which should not load CJK or require Chinese labels. For Chinese/bilingual figures use zh/bi and actually supply the requested translations. Language selection in the font fragment does not translate labels or place two-language text.

Define overrides before the font fragment, for example `\def\FigureLatinFont{Arial}` or `\def\FigureCJKFont{Source Han Serif SC}`. Check availability and the actual PDF result. In bilingual output, stack paired labels in a consistent primary-language order, share equations where the notation is identical, and reserve extra node height. Never drop the second language to force a fit.

Mathematics remains editable LaTeX. The preferred math family is TeX Gyre Termes Math; the fragment reports Latin Modern Math if it must fall back. Missing SimSun or Times New Roman is reported rather than concealed. The font choice in a preamble is not proof of the fonts embedded in the output.

Use the intended manuscript width, not a large canvas later shrunk indiscriminately. A 9.5 pt body is a starting point, not a universal journal rule. Formula scripts can be smaller and need visual review. Check actual text boxes, hierarchy, balanced whitespace and exposed arrow shafts at final size. No fixed image/text percentage applies across workflows and mechanisms.

Review density by function: a mechanism needs space for physical entities and annotated relations; an algorithm needs short action labels and visible branch conditions. For each panel, compare occupied content, whitespace and visual weight on both sides. Keep consistent padding, comparable branch widths and aligned baselines. Wrap or abbreviate author-approved labels before reducing type. Reserve routing lanes outside nodes; keep conditions away from arrowheads and crossings. A geometric crossing is not a junction unless explicitly marked. If final-width text cannot remain readable, reflow, split panels or negotiate a larger canvas.

Use shapes consistently within the selected convention. In a conventional flowchart, rectangles are actions, diamonds decisions, rounded terminals start/end and parallelograms data. An architecture may use labelled rectangular modules throughout; do not impose flowchart shapes on a physical schematic. Black-and-white output must retain semantic distinctions without relying on color.

Keep captions independent of the graphic unless the author requests otherwise. Define important abbreviations, symbols, assumptions and units, and distinguish a teaching schematic from measured evidence. Black-and-white is a robust starting style; semantic color can help distinguish classes but should also be encoded by labels or shapes. Avoid decorative shadows, texture, 3D effects and unexplained gradients.

| Format | Meaning | Verification |
|---|---|---|
| TEX | Complete editable source | Recompile, preserve math and notation |
| PDF | Vector paths and font glyphs where drawn as such | Count raster inclusions, inspect embedding and final-size layout |
| PNG | Raster output | Verify actual pixel dimensions and physical-size DPI; no limitless scaling |

The helper's default PNG is a 150 dpi preview. Use an explicit `--render-dpi`, such as 600 when that meets the actual requirement, for a higher-resolution export. The supported range is 72–1200 dpi with a 40-million-pixel cap per page. A 160 mm-wide figure at 600 dpi is about 3780 pixels wide. This changes rendering samples of vectors; it does not add information to an embedded low-resolution image.

Before calling a file submission-ready, check the particular journal's current official requirements for the figure type, final size, file format and color mode. No universal DPI, font or “Nature style” proves compliance. This profile does not export TIFF/EPS/SVG or perform print color-profile certification.
