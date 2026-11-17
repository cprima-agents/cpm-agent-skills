"""CLI entry point for rendering and parsing UiPath RPA project documents.

The commands here are intentionally thin wrappers around the renderer and
parser modules so they stay easy to document and easy to reuse from `just`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running the file directly without installing the package first.
# The scripts directory is added to sys.path so `import cpm_rpa` resolves.
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from io import StringIO  # noqa: E402

import typer  # noqa: E402
from ruamel.yaml import YAML as _YAML  # noqa: E402

from cpm_rpa import mermaid as _mermaid  # noqa: E402
from cpm_rpa import renderer as _renderer  # noqa: E402
from cpm_rpa import schema as _schema  # noqa: E402
from cpm_rpa.config import DEFAULT_DATA, DEFAULT_DOCS, DEFAULT_SCHEMA  # noqa: E402
from cpm_rpa.parser import parse_document_full as _parse_full  # noqa: E402

app = typer.Typer(help="Render and parse UiPath RPA project documents.")
__all__ = ["app", "parse", "render"]


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


@app.command()
def render(
    artefact: str = typer.Argument(help="Artefact type: pdd, sdd, estimation, …"),
    data: Path = typer.Option(DEFAULT_DATA, "--data", "-d", help="project-data.yaml"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output path"),
    schema: Path = typer.Option(DEFAULT_SCHEMA, "--schema", help="rpa-methodology.yaml"),
    project: Path | None = typer.Option(None, "--project", "-p", help="UiPath project.json"),
    config_dev: Path | None = typer.Option(None, "--config-dev", help="Config_Dev.toml path"),
    config_test: Path | None = typer.Option(None, "--config-test", help="Config_Test.toml path"),
    config_prod: Path | None = typer.Option(None, "--config-prod", help="Config_Prod.toml path"),
    adr_dir: Path | None = typer.Option(None, "--adr-dir", help="Directory containing ADR YAML files (docs/adr/)"),
    lang: str | None = typer.Option(
        None, "--lang", "-l", help="de or en: choose that language of every text pair, and the matching template"
    ),
) -> None:
    """Render one artefact template from `project-data.yaml`.

    The command loads the canonical project data, optionally enriches it with
    project metadata and environment config, and writes the rendered markdown
    to the selected output path.
    """
    if lang not in (None, "de", "en"):
        typer.echo("ERROR: --lang must be 'de' or 'en'.", err=True)
        raise typer.Exit(1)
    if not data.exists():
        typer.echo(f"ERROR: {data} not found — run 'build-data' or 'parse' first, or create it manually.", err=True)
        raise typer.Exit(1)

    project_data = _YAML(typ="safe").load(data.read_text(encoding="utf-8")) or {}
    out = output or DEFAULT_DOCS / (f"{artefact}.{lang}.md" if lang else f"{artefact}.md")

    # Collect only the environment config files the caller actually supplied.
    config_paths: dict[str, Path] = {}
    for env, path in [("dev", config_dev), ("test", config_test), ("prod", config_prod)]:
        if path:
            config_paths[env] = path

    _renderer.render(
        artefact,
        project_data,
        out,
        schema_path=schema,
        project_json_path=project,
        config_paths=config_paths or None,
        adr_dir=adr_dir,
        lang=lang,
        asset_base=data.parent,
    )
    typer.echo(f"Rendered: {out}")


# ---------------------------------------------------------------------------
# render-diagrams
# ---------------------------------------------------------------------------


@app.command("render-diagrams")
def render_diagrams(
    process: Path = typer.Option(..., "--process", help="process.yaml"),
    out_dir: Path = typer.Option(Path("docs/diagrams"), "--out-dir", "-o", help="folder for the .generated files"),
    lang: str = typer.Option("de,en", "--lang", "-l", help="comma-separated: de, en"),
    diagram: str | None = typer.Option(None, "--diagram", help="comma-separated diagram ids; default: all"),
    fmt: str = typer.Option(
        "drawio,mermaid,png", "--format", "-f", help="comma-separated: drawio, mermaid, png, svg"
    ),
) -> None:
    """Write the diagrams of `process.yaml` as `<id>.<lang>.generated.drawio`, `.mmd`, `.png` and `.svg`.

    All formats are built from the same graph, so they show the same steps, numbers and links. png and svg are
    exported from the .drawio file with the draw.io desktop app; when it is missing or the export fails, that is a
    warning and the other files are still written. Only `.generated` files are written; a working copy (the same
    name without `.generated`) is never touched.
    """
    from cpm_rpa import diagrams as _diagrams

    langs, formats = [x.strip() for x in lang.split(",")], [x.strip() for x in fmt.split(",")]
    allowed = (*_diagrams.FORMATS, *_diagrams.IMAGE_FORMATS)
    if any(x not in ("de", "en") for x in langs) or any(x not in allowed for x in formats):
        typer.echo(f"ERROR: --lang takes de and en; --format takes {', '.join(allowed)}.", err=True)
        raise typer.Exit(1)
    data = _YAML(typ="safe").load(process.read_text(encoding="utf-8")) or {}
    only = [x.strip() for x in diagram.split(",")] if diagram else None
    written, warnings = _diagrams.write_diagrams(data, out_dir, langs, formats, only)
    for path in written:
        typer.echo(f"Written: {path}")
    for warning in warnings:
        typer.echo(f"WARN: {warning}", err=True)


# ---------------------------------------------------------------------------
# build-data
# ---------------------------------------------------------------------------


@app.command("build-data")
def build_data(
    process: Path = typer.Option(..., "--process", help="process.yaml"),
    systems: Path = typer.Option(..., "--systems", help="systems.yaml"),
    decisions: Path | None = typer.Option(None, "--decisions", help="decisions.yaml"),
    diagrams_dir: Path | None = typer.Option(
        None, "--diagrams-dir", help="folder of the .generated diagrams; puts the AS-IS high-level map into the PDD"
    ),
    data_model: Path | None = typer.Option(
        None, "--data-model", help="data-model.yaml; fills the PDD input data table (2.6) with the data containers"
    ),
    manifest: Path | None = typer.Option(
        None, "--manifest", help="manifest.yaml of the output repository; the versions, history and status of the documents"
    ),
    stakeholders: Path | None = typer.Option(
        None, "--stakeholders", help="stakeholders.yaml; the business contacts (PDD 1.2) and technical contacts (SDD 2.1)"
    ),
    objectives: Path | None = typer.Option(
        None, "--objectives", help="objectives.yaml; the business objectives (PDD 1.1, SDD 1.1)"
    ),
    output: Path = typer.Option(DEFAULT_DATA, "--output", "-o", help="project-data.yaml to create or update"),
) -> None:
    """Fill `project-data.yaml` from the process, systems and decisions yaml files.

    Only the fields these files can supply are written: process name, short description,
    applications, process steps with derived numbers, business exceptions and the open
    questions. Other keys already in the output file are kept. Text pairs stay pairs;
    `render --lang` picks the language.
    """
    from cpm_rpa import from_yaml as _from_yaml

    yaml = _YAML(typ="safe")
    load = lambda p: yaml.load(p.read_text(encoding="utf-8")) or {}  # noqa: E731
    derived = _from_yaml.build_project_data(
        load(process),
        load(systems),
        load(decisions) if decisions else None,
        diagrams_dir=diagrams_dir.resolve() if diagrams_dir else None,
        base_dir=output.resolve().parent,
        data_model=load(data_model) if data_model else None,
        process_dir=process.resolve().parent,
        manifest=load(manifest) if manifest else None,
        stakeholders=load(stakeholders) if stakeholders else None,
        objectives=load(objectives) if objectives else None,
    )
    existing = load(output) if output.exists() else {}
    for key in ("process_map", "entities", "contacts_business", "contacts_technical", "objectives"):
        if key not in derived:
            existing.pop(key, None)  # nothing found this time: never keep a stale value
    existing.update(derived)
    output.parent.mkdir(parents=True, exist_ok=True)
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    stream = StringIO()
    yaml.dump(existing, stream)
    output.write_text(stream.getvalue(), encoding="utf-8")
    typer.echo(f"Written: {output}  ({len(derived)} field(s) from the yaml files)")


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------


@app.command()
def parse(
    file: Path | None = typer.Argument(None, help="Document to parse (default: docs/pdd.md)"),
    output: Path = typer.Option(DEFAULT_DATA, "--output", "-o", help="project-data.yaml path"),
    schema: Path = typer.Option(DEFAULT_SCHEMA, "--schema", help="rpa-methodology.yaml"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace instead of merging"),
    artefact: str | None = typer.Option(
        None, "--artefact", "-a", help="Artefact type (auto-detected from filename if omitted)"
    ),
) -> None:
    """Parse a rendered artefact back into structured project data.

    The parser is ownership-aware: when an artefact can be detected, only the
    regions that belong to that artefact are extracted. That prevents duplicate
    fields when multiple generated documents share the same topic.
    """
    source = file or DEFAULT_DOCS / "pdd.md"
    if not source.exists():
        typer.echo(f"ERROR: {source} not found.", err=True)
        raise typer.Exit(1)

    # The schema is the source of truth for which fields are known and how
    # rendered regions map back to the data model.
    schema_data = _schema.load(schema)
    known = set(_schema.model_fields(schema_data).keys())

    artefact_id = artefact or _schema.detect_artefact(schema_data, source)
    if artefact_id is None:
        typer.echo(
            f"WARN: cannot detect artefact type for '{source.name}' — "
            "parsing without ownership filter (may produce duplicates).",
            err=True,
        )

    extracted, origins = _parse_full(source, schema_path=schema, artefact_id=artefact_id)

    for key in extracted:
        if key not in known:
            if key in origins:
                region, label = origins[key]
                typer.echo(
                    f"WARN: unknown field in [{region}] — row '{label}' (parsed as '{key}') "
                    f"is not in the schema and will be dropped on next render.",
                    err=True,
                )
            else:
                typer.echo(
                    f"WARN: unknown field '{key}' is not in the schema and will be dropped on next render.",
                    err=True,
                )

    if not overwrite and output.exists():
        existing = _YAML(typ="safe").load(output.read_text(encoding="utf-8")) or {}
        conflicts = {k for k in extracted if k in existing and existing[k] != extracted[k]}
        if conflicts:
            typer.echo(
                f"CONFLICT: {', '.join(sorted(conflicts))} — extracted values will overwrite.",
                err=True,
            )
        existing.update(extracted)
        merged = existing
    else:
        merged = extracted

    output.parent.mkdir(parents=True, exist_ok=True)
    _buf = StringIO()
    _y = _YAML()
    _y.default_flow_style = False
    _y.dump(merged, _buf)
    output.write_text(_buf.getvalue(), encoding="utf-8")
    typer.echo(f"Written: {output}  ({len(extracted)} field(s) extracted from {source})")


# ---------------------------------------------------------------------------
# mermaid
# ---------------------------------------------------------------------------


@app.command()
def mermaid(
    file: Path = typer.Argument(..., help="code-structure.yml to render"),
    style: str = typer.Option("flow", "--style", help="flow (subgraph phases) or tree (parent→child)"),
    depth: int | None = typer.Option(None, "--depth", help="max depth from root (root=1); default: unlimited"),
    types: str | None = typer.Option(
        None, "--types",
        help="node types to render as nodes, comma-separated: process,phase,module,unit",
    ),
    colorscheme: str = typer.Option(
        "solarized-light", "--colorscheme",
        help="color palette for status fills: solarized-light, default",
    ),
    out: Path | None = typer.Option(None, "--out", "-o", help="write to file instead of stdout"),
    auto_out: bool = typer.Option(
        False, "--auto-out",
        help="auto-derive output filename as {stem}.{C4Level}{depth}.md",
    ),
) -> None:
    """Render a code-structure YAML as a Mermaid flowchart diagram."""
    if not file.exists():
        typer.echo(f"ERROR: {file} not found.", err=True)
        raise typer.Exit(1)

    raw = _YAML(typ="safe").load(file.read_text(encoding="utf-8")) or {}
    nodes: list[dict] = raw.get("nodes", [])
    if not nodes:
        typer.echo(f"ERROR: no nodes found in {file}", err=True)
        raise typer.Exit(1)

    allowed_types: set[str] | None = set(types.split(",")) if types else None
    status_fill = _mermaid.COLORSCHEMES.get(colorscheme, _mermaid.COLORSCHEMES["solarized-light"])

    g = _mermaid.build_graph(nodes)

    for w in _mermaid.validate(g):
        typer.echo(f"WARNING: {w}", err=True)

    c4_title, depth_tag = _mermaid.c4_title_for(nodes, g, file.stem, depth, allowed_types, colorscheme)

    if style == "flow":
        lines = _mermaid.render_flow(g, depth, allowed_types, status_fill, c4_title)
    else:
        lines = _mermaid.render_tree(g, depth, allowed_types, status_fill, c4_title)

    content = "\n".join(lines)

    if out:
        out.write_text(content + "\n", encoding="utf-8")
        typer.echo(f"written: {out}", err=True)
    elif auto_out:
        auto_path = file.parent / f"{file.stem}.{c4_title.split(' | ')[0]}{depth_tag}.md"
        auto_path.write_text(content + "\n", encoding="utf-8")
        typer.echo(f"written: {auto_path}", err=True)
    else:
        typer.echo(content)


if __name__ == "__main__":
    app()
