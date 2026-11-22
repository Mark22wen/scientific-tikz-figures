# Academic symbols without silent substitution

Keep ordinary Chinese/English text in its requested text family, and mathematics in a dedicated Unicode math font through `unicode-math`. Times New Roman is the Latin text default; this does not mean forcing every mathematical glyph into that text font. TeX Gyre Termes Math is preferred, with an explicit Latin Modern Math fallback in the supplied font fragment. Author choices override defaults.

Use editable math commands inside math mode. Prefer notation already used by the manuscript; similar-looking symbols are not interchangeable. Preserve the difference between a multiplication sign and a Latin x, the letter v and Greek nu, zero and capital O, prime and quotation marks, and a hyphen and a mathematical minus.

| Family | Examples of editable source |
|---|---|
| Greek and variants | `\alpha`, `\beta`, `\gamma`, `\theta`, `\vartheta`, `\epsilon`, `\varepsilon`, `\phi`, `\varphi`, `\mu`, `\sigma`, `\omega`, `\Gamma`, `\Delta`, `\Sigma`, `\Omega` |
| Relations | `\leq`, `\geq`, `\neq`, `\approx`, `\equiv`, `\sim`, `\propto`, `\ll`, `\gg` |
| Sets and logic | `\in`, `\notin`, `\subseteq`, `\cup`, `\cap`, `\emptyset`, `\forall`, `\exists`, `\neg`, `\land`, `\lor` |
| Calculus | `\partial`, `\nabla`, `\int`, `\iint`, `\oint`, `\sum`, `\prod`, `\lim`, `\infty` |
| Statistics | `\mathbb{E}`, `\mathbb{P}`, `\operatorname{Var}`, `\operatorname{Cov}`, `\mathcal{N}`, `\hat{\theta}`, `\bar{x}` |
| Vectors and algebra | `\symbf{x}`, `\symbf{\Sigma}`, `\vec{v}`, `\lVert x\rVert`, `\langle x,y\rangle`, `\otimes`, `\oplus`, `\det` |
| Arrows and annotations | `\to`, `\mapsto`, `\Rightarrow`, `\leftrightarrow`, `\uparrow`, `\dot{x}`, `\ddot{x}`, `\tilde{x}`, `\prime` |
| Units | `25\,{}^{\circ}\mathrm{C}`, `\mathrm{K}`, `\mathrm{kPa}`, `\mathrm{W\,m^{-2}}`; follow the manuscript's quantity/unit convention |

The [symbol proof sheet](../assets/symbol-coverage.tex) is a complete editable regression example covering these families, mathematical alphabets, Greek variants, matrices, subscripts and superscripts, plus Chinese punctuation. It is a finite tested set, not a claim that every Unicode character or every specialist symbol is supported by every font.

When a character looks wrong:

1. Compare the source with the author's intended notation. A literal question mark in a decision label can be ordinary punctuation; do not replace it with a guessed Greek letter. The supplied loop example omits this punctuation to avoid confusion.
2. Check UTF-8 decoding and U+FFFD replacement characters. The helper rejects a replacement character in active source rather than silently repairing lost information.
3. Compile and read the missing-glyph findings. Missing characters are errors even when XeLaTeX still produces a PDF. Fix the source command or choose a font that contains the intended glyph, then rebuild.
4. Check the actual PDF fonts and render. A font fallback is disclosed. If source/glyphs are missing, retain the failure evidence and do not call the figure ready.
5. PDF text extraction may lose mappings even when ink renders correctly, or may return a substituted question mark. Compare the visible formula to source; an extraction-only language check cannot certify every symbol. For outlined or imported artwork, visual inspection remains necessary.

Never apply a bulk “replace all question marks” repair or strip unsupported characters. If the intended character is unknown, ask for that notation. Added specialist commands require an actual compile/render check in the selected font and final layout.
