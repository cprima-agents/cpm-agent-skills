"""A generated document as Word: pandoc with the two filters, then the footer from the manifest.

The footer text is stated in the manifest of the output repository, per artefact and language:

    artefacts:
      - id: pdd
        footer: { de: "PDD · {process} · Version {version}", en: "PDD · {process} · version {version}" }

`{process}`, `{version}`, `{date}` and `{artefact}` are filled from the project data. The page number is added by the
generator ("Seite 3" / "Page 3"). A Word template brings a footer of its own; it is always replaced, so text from
another project never reaches a document. Without `footer` in the manifest the footer holds only the page number.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

_PANDOC = Path(__file__).resolve().parent.parent.parent / "assets" / "pandoc"
_PAGE_WORD = {"de": "Seite ", "en": "Page "}


def footer_text(manifest: dict[str, Any], data: dict[str, Any], artefact: str, lang: str) -> str:
    """The footer text of one artefact in one language, placeholders filled; empty when the manifest states none."""
    entry = next((a for a in manifest.get("artefacts") or [] if a.get("id") == artefact), {})
    template = (entry.get("footer") or {}).get(lang) or ""
    values = {
        "process": data.get("process_name") or "",
        "version": data.get(f"{artefact}_version") or "",
        "date": data.get(f"{artefact}_date") or "",
        "artefact": artefact.upper(),
    }
    return re.sub(r"\{(\w+)\}", lambda m: str(values.get(m.group(1), m.group(0))), template)


def patch_footer(docx: Path, text: str, lang: str) -> None:
    """Set the footer text and the word before the page number in the footer of a Word file."""
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(docx) as source, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            payload = source.read(item.filename)
            if re.fullmatch(r"word/footer\d*\.xml", item.filename):
                xml = payload.decode("utf-8")
                texts = re.findall(r"<w:t(?: [^>]*)?>[^<]*</w:t>", xml)
                if texts:  # the first run is the text of the footer, the second the word before the page number
                    xml = xml.replace(texts[0], f'<w:t xml:space="preserve">{escape(text)}</w:t>', 1)
                    if len(texts) > 1:
                        xml = xml.replace(texts[1], f'<w:t xml:space="preserve">{_PAGE_WORD[lang]}</w:t>', 1)
                payload = xml.encode("utf-8")
            target.writestr(item, payload)
    tmp.replace(docx)


def export_docx(
    markdown: Path,
    output: Path,
    lang: str,
    artefact: str,
    data: dict[str, Any],
    manifest: dict[str, Any],
    reference_doc: Path | None = None,
) -> Path:
    """Convert the rendered markdown to Word and set the footer. Needs pandoc."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("pandoc was not found on the PATH")
    cmd = [
        pandoc,
        str(markdown.name),
        "-f",
        "markdown",
        "-o",
        str(output.resolve()),
        "--lua-filter",
        str(_PANDOC / "cell-breaks.lua"),
        "--lua-filter",
        str(_PANDOC / "table-widths.lua"),
        "--resource-path",
        ".",
    ]
    if reference_doc:
        cmd += ["--reference-doc", str(reference_doc.resolve())]
    done = subprocess.run(cmd, cwd=markdown.resolve().parent, capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise RuntimeError(f"pandoc failed: {done.stderr.strip()}")
    patch_footer(output, footer_text(manifest, data, artefact, lang), lang)
    return output
