---
name: uip-methodology
description: >
  UiPath RPA project design skill — guides BA, Solution Architect, and PM through
  authoring and amending all project artefacts: PDD, SDD, Architecture Review,
  Estimation, ROI, TDD, DSD, Glossary. Three workflows: (A) Guided Interview —
  full structured elicitation driven by rpa-methodology.yaml, produces any
  artefact; (B) PDD Creation — focused section-by-section PDD authoring for BAs;
  (C) SDD Creation / Amendment — infers architecture decisions from PDD, patches
  existing SDDs idempotently. Trigger phrases: "start interview", "guided interview",
  "interview me", "help me document this process", "create a PDD", "fill out a PDD",
  "start a PDD", "document a process for RPA", "create an SDD", "design the solution",
  "generate SDD", "amend SDD", "update SDD", "fill in the PDD", "let's do the arch
  review", or when a PDD is available and the next step is technical design.
license: Apache-2.0
allowed-tools: shell
---

# UiPath RPA Design

> **Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/).
> After installing this skill, run `uv sync` from the repo root (`cprima-agents/agentskills`)
> where `pyproject.toml` declares the runtime dependencies.
> The scripts under `scripts/` will not work without it.

## Decision tree — pick a workflow in 3 seconds

```
Has a PDD already?
  NO  → is the user a BA or asking how to document a process?
          YES → Workflow B (PDD Creation)
          NO  → Workflow A (Guided Interview)
  YES → does an SDD exist?
          NO  → Workflow C, Create mode
          YES → Workflow C, Amend mode
```

**Default artefact order** (one per project milestone, in sequence):

```
PDD  →  SDD  →  TDD  →  estimation  →  ROI  →  arch-review
```

Each artefact is a prerequisite for the next. Never skip forward unless the user
explicitly asks. Offer the next artefact at the end of each workflow output.

**Hard routing rules — no interpretation required:**

| If the user says … | Do this |
| --- | --- |
| "create / fill out a PDD" or is a BA describing a process | **Workflow B** |
| "create an SDD" / "design the solution" / provides a PDD | **Workflow C, Create mode** |
| "amend / update / fix the SDD" / provides an existing SDD | **Workflow C, Amend mode** |
| "create estimation" / "estimate the project" / "fill out estimation" | **Workflow D, Estimation** |
| "create ROI" / "calculate ROI" / "fill out ROI" | **Workflow D, ROI** |
| "what next?" after a PDD | Say: next step is the SDD; offer Workflow C |
| "what next?" after an SDD | Say: next step is the TDD, then estimation, then arch-review |
| "what next?" after an estimation | Say: next step is ROI; offer Workflow D ROI |
| "start interview" / role unclear / no artefacts yet | **Workflow A** |

---

## Workflow A — Guided Interview

Conducts a staged elicitation interview that builds toward one target artefact at a
time. Driven by `references/rpa-methodology.yaml`.

### Bootstrap (always run first)

Ask these four things in one message:

1. **Project identifier** — "What short slug should I use for this project?
   (lowercase, hyphens only — e.g. `invoice-processing`, `ppo-objection`)"
2. **Process identity** — "In one sentence: what does this process do,
   from trigger to outcome?"
3. **Your role** — "What is your role on this project?"
   (Process Owner / BA / Solution Architect / Developer / PM)
4. **Target artefact and stage** — "Which document are we working toward,
   and is this a fresh start or a continuation?"

Derive from answers:
- `project_slug` — validated: lowercase, hyphens, no spaces; derive from process name if skipped
- `process_identity` — anchor sentence used to contextualise all questions
- `stage` — one of: `pdd | arch_chapter | estimation | roi | sdd | tdd | dsd | glossary | project_plan`
- `interviewer_role` — depth signal

### Scaffold (run immediately after bootstrap)

Check whether `./docs/` exists. If not, create it and tell the user. If it already
exists, confirm its location and continue.

The user works in a single project directory — all input, model, and output files
live under `./docs/`. No sub-project nesting.

### Harvest (run after scaffold; skip if day zero)

Read all files in `./docs/`. Build a coverage map:

```
topic → covered | partial | unknown | conflicting
```

For each topic record: `source` (which file), `confidence` (high / low).
If `./docs/` is empty or contains no recognisable artefacts → all topics `unknown`; skip to Interview.

### Interview Loop

Load `references/rpa-methodology.yaml`. For the active `stage`:

1. **Own topics** — where `<stage>.owns: true` → ask fully
2. **Reference topics** — where `<stage>` has `role` but no `owns` → verify briefly
3. **Absent topics** — not present for this stage → accept as forward observations only

Order: `required: true` own topics first, then optional own topics, then reference topics.

**Per own topic:** state coverage status if partial/conflicting; ask the `question` from
the YAML; follow up once on required incomplete topics; confirm before moving on.

**Per reference topic:** one line — "For [topic] — [brief restatement of known answer]
— anything to add or correct?"

**Forward observations:** when the interviewee mentions something belonging to a
different stage, capture as:
```
[FORWARD → <stage> / <topic> / section <n>]: <note>
```

### Output

After all required own topics are covered:

1. Present the **coverage summary** (covered / partial / unknown per topic)
2. List all **forward observations** grouped by target stage
3. Ask: "Shall I generate the [target artefact] draft now, or continue?"
4. If confirmed: load the matching template from `assets/templates/`, fill every section
   where answers were collected, mark uncovered sections `[TBD]`, write to
   `docs/`

### Modes at a glance

| Situation | Scaffold | Harvest? | Interview mode |
| --- | --- | --- | --- |
| No artefacts exist (day zero) | create folders | skip | full greenfield — all own topics |
| Prior artefacts exist | confirm folder | yes → coverage map | gaps only |
| Resuming interrupted session | confirm folder | yes | remaining gaps |

---

## Workflow B — PDD Creation

Guide a Business Analyst through filling out a PDD interactively. Work through
sections sequentially.

### 0. Start
Ask for the **process name** and **your name / role** (BA). Confirm the output
filename: `<process-name-kebab>-pdd.md`.

### 1. Section by section
Work through the 5 PDD sections in order. For each section:
- Ask the questions from [references/elicitation-questions.md](references/elicitation-questions.md)
- Accept partial answers — mark unanswered fields `[TBD]`
- After each section, summarise what was captured and ask "Anything to add or correct before we continue?"

**Section order:**
1. Introduction (Purpose, Objectives, Key Contacts, Prerequisites)
2. AS-IS Process Description (Overview, Applications, Process Map, Steps, Input Data)
3. TO-BE Process Description (Scope, Exceptions, Reporting)
4. Decisions (one numbered section per decision: question, data it reads, rules with their status)
5. Additional Documentation

### 2. Write the file
Load `assets/templates/pdd-template.md`, substitute all captured values, and write
to `docs/<process-name-kebab>-pdd.md`.

### 3. Finish
Tell the user the output path. List any `[TBD]` items remaining and suggest they
resolve them before handing the PDD to a Solution Architect.

### Rules
- Never invent business rules, volumes, or exception behaviour — always ask.
- Ask at most 4–5 questions per message.
- Use plain business language, not UiPath jargon.
- If the user says "skip" or "I don't know", mark the field `[TBD]` and move on.
- Prefer tables and bullet lists when summarising captured data back to the user.

---

## Workflow C — SDD Creation / Amendment

Guide a Solution Architect through producing or completing an SDD. Infer as much
as possible from the PDD; ask only for decisions that cannot be derived from it.
**Idempotent** — safe to run repeatedly against an existing SDD.

### 0. Start — detect mode

Ask for the PDD (file path or reference to an already-loaded file).

Check whether an SDD already exists:
- **No SDD found** → **Create mode**: proceed from step 1.
- **SDD found** → **Amend mode**: jump to step A.

Confirm the output filename: `<process-name-kebab>-sdd.md`.

---

### Create path

### 1. Extract PDD data
Read the full PDD and extract:
- Process name, department, schedule, volume, peak volume
- Applications list (names, client type, access method)
- In-scope / out-of-scope steps
- Known business and application exceptions
- Reporting requirements

### 2. Apply inference rules
Load [references/inference-rules.md](references/inference-rules.md) and derive as many
SDD fields as possible. Summarise inferences in a short table for the architect to review:

| Field | Inferred Value | Confidence | Reason |
| --- | --- | --- | --- |
| Framework | REFramework | High | Queue-based transactional, >50 items/day |
| Robot Type | BOR | High | No human interaction required |
| … | … | … | … |

### 3. Ask for gaps only
For fields that cannot be inferred, ask the architect. Load
[references/gap-questions.md](references/gap-questions.md) for the question set.
Group related questions to max 5 per message.

### 4. Build project structure
Apply decomposition heuristics from [references/inference-rules.md](references/inference-rules.md)
to define the project list and workflow inventory. Present for confirmation before writing.

### 5. Write the file
Load `assets/templates/sdd-template.md`, substitute all values, and write to
`docs/<process-name-kebab>-sdd.md`.

Section 9 is an estimation reference stub — fill in the four summary rows only if data
is available. Effort detail lives in a separate `<process-name>-estimation.md`; do not
inline it in the SDD.

### 6. Finish
Report the output path. List any `[SME REVIEW]` items remaining. Suggest next steps:

- Hand-off to TDD author
- Generate `<process-name>-estimation.md` from `assets/templates/estimation-template.md`
- When arch-review is ready, render it and generate the ROI chart:
  ```bash
  uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py render arch_review --data docs/project-data.yaml --output docs/arch-review.md
  uv run .claude/skills/uip-methodology/scripts/generate_roi_chart.py docs/arch-review.md
  ```
  `generate_roi_chart.py` carries its own PEP 723 dependency header — `uv run` installs plotly/kaleido automatically. No `--project` flag needed.
- Open UiPath Studio project

---

### Amend path

### A. Inventory the existing SDD
Read the full SDD. Produce a gap inventory:

| Section | Status | Gap |
| --- | --- | --- |
| 3.1 Design Decisions | complete | — |
| 4.1 Dispatcher config | partial | Trigger/schedule is [TBD] |
| 8.1 System Access Prerequisites | partial | Owner and status columns incomplete |
| … | … | … |

Gap signals (in priority order):
1. `[TBD]` — value deferred
2. `[SME REVIEW]` — needs business owner decision
3. `[DEFAULT]` — placeholder to confirm
4. Open questions in section 10 still marked Open
5. Sections present in `assets/templates/sdd-template.md` but missing from this SDD
6. Data inconsistencies (e.g. payback figure differs from estimation file)

### B. Resolve from PDD and inference rules
Read the PDD. Load [references/inference-rules.md](references/inference-rules.md).
For each gap, attempt to resolve without asking. Mark resolved gaps with the source.

### C. Ask for remaining gaps only
For gaps that cannot be resolved, ask the architect. Group related questions to max 5
per message.

### D. Patch the file
Edit the existing SDD in place. Only modify cells/sections with identified gaps.
Do not reformat, reorder, or rewrite sections that are already complete.

### E. Finish
Report what was changed. List any `[SME REVIEW]` items still open. Note open
questions in section 10 that are now resolved vs. still open.

---

## Workflow D — Estimation & ROI

Produces `<process-name>-estimation.md` and/or `<process-name>-roi.md` from their
templates. **Always load the template — never write these files as plain markdown.**
Both files are structured data documents: the renderer reads their region blocks to
compute derived values and generate the ROI chart. Without regions, the pipeline breaks.

### Estimation

#### 1. Collect inputs
Read the SDD. Extract from section 3 (component inventory / workflow inventory):
- List of pipeline components (Dispatcher, Performer stages, Aggregator if present)
- Application list and access method (drives complexity)
- Schedule / volume (drives effort multipliers)

Ask the architect for any of these that are missing or `[TBD]`:
- PD (person-day) rate in €
- Contingency percentage (default 10 %)
- Per-component: complexity (`low` / `medium` / `high`), base effort in PDs, confidence

Group related questions — at most 5 per message.

#### 2. Build the file
Load `assets/templates/estimation-template.md`. Substitute all values collected above.
For every component in the SDD's component inventory, add a row to the `effort_items`
region. For every `[TBD]` that is still unknown, write `[TBD]` in the cell — do not
omit the row.

**Region map — all six must be present and paired in the output:**

| Region | Contains |
| --- | --- |
| `estimation_header` | Version, date, status, confidence, contingency |
| `estimation_history` | Document version history table |
| `estimation_approvals` | Sign-off table |
| `effort_items` | Per-component effort table (machine-readable) |
| `cost_items` | Monthly run costs table (machine-readable) |
| `estimation_summary` | Financial summary: PD rate, totals, build cost |

Write to `docs/<process-name-kebab>-estimation.md`.

#### 3. Finish
Run the linter. List any `[TBD]` items remaining. Offer to generate the ROI next.

---

### ROI

#### 1. Collect inputs
Read `docs/<process-name>-estimation.md` for `monthly_run_cost` and `build_cost`.
Read the PDD for monthly transaction volume.

Ask for any missing values:
- FTE cost rate (€/hour)
- AHT saved per transaction (minutes)

#### 2. Build the file
Load `assets/templates/roi-template.md`. Substitute all values.

**Region map — all four must be present and paired in the output:**

| Region | Contains |
| --- | --- |
| `roi_header` | Version, date, status |
| `roi_history` | Document version history table |
| `roi_inputs` | FTE cost rate, AHT saved — the two SA-provided inputs |
| `roi_summary` | Full financial summary table (monthly/annual savings, payback, net benefit) |

Write to `docs/<process-name-kebab>-roi.md`.

#### 3. Finish
Run the linter. List any `[TBD]` items remaining. When both estimation and ROI are
complete and the arch-review template is filled, generate the ROI chart:

```bash
uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py render arch_review --data docs/project-data.yaml --output docs/arch-review.md
uv run .claude/skills/uip-methodology/scripts/generate_roi_chart.py docs/arch-review.md
```

---

## Workflow E — Bilingual documents from yaml (German and English)

Every document comes out twice, as two separate files: one in German (`de`), one in English (`en`). Never one mixed file.

The source of truth is the yaml files, with every reader-facing text written as a pair `{ de: ..., en: ... }` (see Shared Rules):

- `process.yaml` — steps and edges (a network, with sub-steps), exceptions, terminal states, lanes. In the to-be model the seven pipeline stages (initialize, ingest, enrich, decide, execute, complete, finalize) are container steps (`stage:` on a top-level task); the steps of a stage name it as `parent`, per model: `parent: { to-be: INGEST }`. PDD 3.1 lists the stages from these containers.
- `systems.yaml` — the systems and what the robot does in them
- `decisions.yaml` — the decisions at the gateways

Steps, in this order:

1. **Lint the yaml** and fix all FAILs:
   ```bash
   uv run .claude/skills/uip-methodology/scripts/lint_yaml_text.py docs/process.yaml docs/systems.yaml docs/decisions.yaml
   ```
1b. **Render the diagrams** (optional, needed for the process map of the PDD): `cli.py render-diagrams --process docs/process.yaml -o docs/diagrams` writes `<diagram-id>.<lang>.generated.drawio`, `.mmd` and `.png` (or `.svg` and `.pdf` with `--format`). A pdf page is as big as its diagram, with no paper size, so a reviewer zooms in the PDF reader; `--format drawio,mermaid,png,pdf --combine diagrams` also writes `diagrams.<lang>.generated.pdf`, all diagrams in the order of the process file with one bookmark each. The png and svg are exported with the draw.io desktop app; when it is missing or the export fails, that is only a warning. Only `.generated` files are written; a copy without `.generated` is never touched.
2. **Build the project data** from the yaml files. Add `--diagrams-dir docs/diagrams` to put the AS-IS high-level map into PDD section 2.4 (the image if it exists, else the Mermaid text, else `[TBD]`), and `--data-model docs/data-model.yaml` to fill PDD section 2.6 with the data containers (the entities of the data model grouped by `source.container`, one row per container).
   Text pairs stay pairs, step numbers are derived, nothing is typed by hand. The process steps of the PDD (section 2, AS-IS) come from the as-is model; the business exceptions (section 3, TO-BE) from the to-be model. Other keys already in the output file are kept:
   ```bash
   uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py build-data --process docs/process.yaml --systems docs/systems.yaml --decisions docs/decisions.yaml --output docs/project-data.yaml
   ```
3. **Render each language** into its own file:
   ```bash
   uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py render pdd --lang de --output docs/<process>-pdd.de.md
   uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py render pdd --lang en --output docs/<process>-pdd.en.md
   ```
   `--lang` picks the matching template (`<artefact>-template.<lang>.md`) and snippet (`snippets/<name>.<lang>.md`); a missing German file falls back to the English one. Today only the PDD has German templates; the SDD, TDD, estimation and ROI are English until their `.de.md` templates exist.
4. **Lint both documents** with `lint_docs.py`.

**A data field must not map to one single column.** In data-driven generation the data says what a thing is (`description`, `where`, `next`, `rules`), and the snippet decides how it is shown; one field may appear in several places, and one table cell may combine several fields. Never name a field after the column that shows it. The PDD step table (2.5) is the example: two columns, `Step | What happens`, where the cell holds the description, the system and the screenshots, a divider, and then the next steps, rules and exceptions. Because merged cells cannot be read back, such a region is generated only and not parsed back (`from_markdown` is empty in the schema).
Each part of such a cell is a `<span custom-style="…">`: `StepDescription`, `StepSystem`, `StepNext`, `StepRule`, `StepException`, and `StepDivider` for the divider (a line of dashes). The names are the same in German and English. The parts are separated by `<br>`. Never use `<hr>` in a cell: when pandoc writes docx, everything after it in the cell is lost. Markdown is only a step on the way to docx or PDF; convert with the filter that turns `<br>` into a Word line break, and the spans arrive as named Word styles: `pandoc document.md --lua-filter assets/pandoc/cell-breaks.lua --lua-filter assets/pandoc/table-widths.lua -o document.docx`. The second filter gives every table the full page width and columns whose width follows their amount of text; without it a table with short rows is only as wide as its content and all columns are equally wide.

A generated document is never edited by hand. To change it, change the yaml and render again. Text that the yaml cannot supply (stakeholders, volume, scope) renders as `[TBD]`.

## Shared Rules

- Never invent selectors, UI element identifiers, or field names — mark as `[DEV: inspect at build time]`.
- Use `[DEFAULT]` for industry-standard values (retry=3, timeout=30s, queue item deadline=24h).
- Use `[SME REVIEW]` for gaps requiring business knowledge not covered by PDD or inference rules.
- Do not copy PDD sections verbatim into an SDD — reorganise content into the SDD structure.
- The Workflow Inventory table is the most important SDD section; every PDD in-scope step must map to at least one workflow file.
- **Amend mode only**: never touch a field that already has a real value.
- **After writing or amending any artefact, run the linter and fix all FAILs before reporting completion to the user:**
  ```bash
  uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/lint_docs.py docs/<artefact-file>.md
  ```
  Exit code 1 means failures remain — fix them and re-run. List remaining WARNs to the user (TBD count, SME review items, etc.).
- **Yaml data files (`process`, `decisions`, `systems`, `data-model`) follow two rules; run the yaml linter after writing or amending one and fix all FAILs:**
  ```bash
  uv run .claude/skills/uip-methodology/scripts/lint_yaml_text.py docs/<file>.yaml
  ```
  - Every field marked `Text` in `assets/templates/*.template.yml` is a pair `{ de: ..., en: ... }`, both keys filled. A plain string is an error. Identifiers, refs, enums and names stay single values.
  - An item may carry `status: New | InProgress | UnderReview | Approved | Rejected | Complete`. The key may be missing. When present it must be one of these six spellings; an empty status is an error. Never set a status the user has not given.
  - An item may carry `tags: [kebab-case-word, ...]`. The key may be missing. The tag `open-question` marks an open question: it is open while the status is `New`, `InProgress`, `UnderReview` or missing, and answered once the status is `Approved`, `Rejected` or `Complete`. Never write "is not decided" or "not verified" into free text; use the tag.
  - **A process is a network of steps, not a numbered list.** `process.yaml` holds `steps` (each with a readable, stable `id`) and `edges` (`from`, `to`, pointing forward). Never write a sequence number into a yaml file, a label or free text; refer to a step by its id. Order and numbers (1, 2, … and 6.1, 6.2) are derived by the view layer (`scripts/yaml_graph.py`, `number()`), and the diagram level by `views`.
    - A step with `parent` is a sub-step; edges connect steps of the same level only. The top level has one `start_event`; each sub-level has one entry step and at least one exit step.
    - A gateway has `kind` (`exclusive`, `inclusive`, `parallel`) and `role` (`split`, `join`). An inclusive or parallel split needs exactly one join (`closes` names the split) and every branch must reach it; an exclusive split needs none. Every branch of an exclusive or inclusive split carries a `condition`.
    - A cycle is allowed only on an edge tagged `loop`.
    - **Models and diagrams.** `as-is` and `to-be` are the two process models of the requirements lifecycle: the as-is model describes what exists, the to-be model specifies what shall exist. They are not states and not phases; do not call them that. One process file holds both. An item (step, edge, exception, terminal state) says which with `models: [as-is]`, `[to-be]` or `[as-is, to-be]`; a missing `models` means both. A step that sits in different places in the two models is two steps. Each model is linted as a graph of its own.
    - A **diagram** renders one or both models (both = a comparison) at a level of detail, `high-level` (top-level steps) or `detailed` (with sub-steps). Diagrams are defined once under `diagrams` (`id`, `title`, `models`, `detail`); a step may limit itself to some diagrams with `diagrams: [ID]`. Every diagram is linted as a graph too.
    - **Pipeline stages.** A step may carry `stage`, one of `initialize`, `ingest`, `enrich`, `decide`, `execute`, `complete`, `finalize` (defined once, as `enums.pipeline_stage` in `references/rpa-methodology.yaml`, with a German and English purpose; these are the code-guideline stages of the robot run, in this order). A sub-step without `stage` takes its parent's. Never write `init`; the stage is `initialize`.
    - **A system is an entity with an `id`**, not a name: `systems.yaml` items have `id` (UPPER_SNAKE_CASE, unique, never renamed once referenced, e.g. `MEINSERVICE`) and `label` (the display name). A `system:` in `process.yaml`, `decisions.yaml` or `credentials.yml` refers to that id. The key `name` is a linter error.
    - Never put a tool-specific shape id (`drawio_id` and the like) into a yaml file. If a drawn diagram must stay linked, keep the mapping in a separate file next to it.
    - `decisions.yaml` has no `sequence`; its `id` is the gateway step it decides.
- **Preserve all `<!-- #region name -->` / `<!-- #endregion name -->` markers** from the template verbatim. These are load-bearing: the parser (`cpm_rpa/parser.py`) uses them to extract structured data for rendering. Write the captured content *between* the tags, never outside or instead of them. A region with no data gets `[TBD]` between its tags — never an empty or missing block. Never strip, rename, or reorder region markers.
- **Generate Mermaid diagrams from a `code-structure.yml`** using the `mermaid` CLI subcommand:
  ```bash
  # stdout
  uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py mermaid docs/code-structure.yml

  # write file — explicit path
  uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py mermaid docs/code-structure.yml --out docs/code-structure.md

  # write file — auto-derive name ({stem}.{C4Level}.md)
  uv run --project .claude/skills/uip-methodology/ .claude/skills/uip-methodology/scripts/cpm_rpa/cli.py mermaid docs/code-structure.yml --auto-out
  ```
  Options: `--style flow|tree` (default: flow), `--depth N`, `--types process,phase,module,unit`, `--colorscheme solarized-light|default`.
  `flow` renders phases as subgraph containers; `tree` renders raw parent→child edges.
- **All diagrams must be written as Mermaid code blocks** (```` ```mermaid ```` fenced blocks). Never describe diagrams in prose or ASCII art. Use `flowchart TD` for process flows and `C4Context` / `graph LR` for system context and architecture diagrams.
