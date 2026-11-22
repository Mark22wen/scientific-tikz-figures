# Select a structure, then apply a restrained style

These are design patterns, not claims of journal endorsement. Preserve scientific content when changing appearance. Ask for a reference figure only when its specific conventions matter; learn its organization without copying protected artwork or fabricating its findings.

| Figure role | Layout pattern | Visual grammar | Review priority |
|---|---|---|---|
| Paper roadmap | Question → evidence/work packages → validation | Broad aligned lanes; short task labels | Show how evidence answers the question; omit internal solver detail |
| Algorithm | Vertical steps with side branches and an exterior return lane | Rectangular actions, diamond decisions, rounded exits | Every decision labelled, loop target explicit, finite stop or stated convergence condition |
| Model architecture | Left-to-right or parallel streams with interface labels | Modules and data arrows; aligned fusion layer | Shapes, units, observation IDs and operation at each merge; training/inference distinction |
| Physical principle | Geometry or network reflecting physical connectivity | Objects/boundaries, directed fluxes and junction dots | Boundary conditions, sign conventions, governing relations and idealizations |
| Causal or mechanistic hypothesis | Entities with selected directed relationships | Solid/dashed relations explained in a legend | Evidence status of each relation; no inferred causal claim from correlation |
| Probabilistic model | Variables with dependency arrows; plates only when justified | Observed/latent distinction; repeated-index plates | Joint factorization, indexing, conditional dependencies and meaning of shading |

Default treatment: white background, black or dark gray strokes, one type hierarchy, no shadow or perspective. For semantic color, use a small muted palette and repeat distinctions in labels/line styles. A physical field gradient is acceptable only when it encodes an explicit quantity with a scale; decorative gradients are not a substitute for scientific structure.

The scope is agent-authored TikZ. These patterns do not supply an automatic causal discovery engine, a probabilistic inference engine or a universal automatic layout solver. For a genuinely new physical drawing, make assumptions explicit and review the resulting geometry and equations with the author.

Editable examples: [architecture](../assets/example-en.tex), [bounded loop](../assets/example-loop-en.tex), [bilingual physical principle](../assets/example-principle-bi.tex), [Chinese workflow](../assets/example-workflow-zh.tex). The associated `.caption.txt` files state scope and assumptions. These are original teaching diagrams and must not be presented as experimental results.
