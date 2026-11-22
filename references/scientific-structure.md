# Select the scientific role first

| Role | Reader's question | Useful structure | Check |
|---|---|---|---|
| Mechanism/theory | Why, through what relation, under which conditions? | Entities, supported effects and explicit assumptions | Correlation is not causation; distinguish hypothesis from supported result |
| Physical principle | How do objects, fields, constraints or conservation laws interact? | Physical connectivity, boundaries, flow directions, governing equations | Units, sign convention, scale and idealizations |
| Whole-paper roadmap | How does the work answer the research question? | Work packages, evidence sources and validation | Do not turn it into a detailed algorithm |
| Local model | How does this problem become equations and outputs? | Inputs/assumptions, model, solver, output and checks | Preserve the actual objective and boundary conditions |
| Algorithm | What happens next and when does it stop? | States, decisions, updates and explicit exit | Cover every branch and define return target |
| Architecture | What does each module consume and produce? | Interfaces, parallel paths, fusion and output | Distinguish training from inference and data dependencies from time order |

Do not infer role from a figure number alone. A composite figure can have different roles in separate labelled panels. Physical energy/material transfer, causal hypotheses, control flow and data flow need distinguishable meanings. A connection dot denotes a physical junction when that convention is used; an algorithmic merge is an operation, not automatically a physical junction.

Before layout, write a small internal map: element, role, author/manuscript basis, incoming/outgoing relation. Unsupported relations remain missing or explicitly hypothetical.

At merges, check manually:

- **Concatenation:** compatible non-concatenated axes; correct combined size; same observation/window IDs; each channel retains its unit.
- **Sum / weighted mean:** compatible shapes and units; aligned observations; mean weights defined and normalized where appropriate.
- **Exclusive selection:** one alternative path supplies the result; do not add mutually exclusive outputs.
- **Other operations:** use the author's actual definition for dot products, parameter fusion, broadcasting and symbolic dimensions.

Matching labels do not prove matching data. Never invent tensor dimensions or unit conversions. This marketplace profile guides these checks; it does not contain the local full edition's machine-readable merge-contract validator.

For visual topology, keep a clear reading direction, align parallel branches, reserve arrow channels before placing labels, and label ambiguous conditions. Prefer orthogonal connections where suitable. Intentional feedback may bend around the perimeter with a clear return target. Split crowded figures into panels instead of reducing body text below the agreed final-size minimum.
