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


# The look of every run of the footer, stated here and not inherited: a template without a footer style would give
# the defaults of the document (the theme font at 12 pt), and a field would not take the look of the text before it.
FOOTER_RPR = (
    '<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>'
    '<w:color w:val="333333"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
)


def _footer_paragraph_body(text: str, lang: str) -> str:
    """The runs of the footer: the text, a tab, the word, and the page number as a field. Every run states its look."""
    run = lambda inner: f"<w:r>{FOOTER_RPR}{inner}</w:r>"  # noqa: E731
    return (
        run(f'<w:t xml:space="preserve">{escape(text)}</w:t>')
        + run("<w:tab/>")
        + run(f'<w:t xml:space="preserve">{_PAGE_WORD[lang]}</w:t>')
        + run('<w:fldChar w:fldCharType="begin"/>')
        + run('<w:instrText xml:space="preserve"> PAGE </w:instrText>')
        + run('<w:fldChar w:fldCharType="separate"/>')
        + run("<w:t>1</w:t>")
        + run('<w:fldChar w:fldCharType="end"/>')
    )


def patch_footer(docx: Path, text: str, lang: str) -> None:
    """Replace the footer of a Word file: the text, the word before the page number and the page number itself.

    The border and the tab stop of the paragraph stay as the template has them; the look of the runs is stated.
    """
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(docx) as source, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            payload = source.read(item.filename)
            if re.fullmatch(r"word/footer\d*\.xml", item.filename):
                xml = payload.decode("utf-8")
                paragraph = re.search(r"<w:p>(<w:pPr>.*?</w:pPr>)?.*?</w:p>", xml, re.DOTALL)
                if paragraph:
                    props = re.sub(r"<w:pStyle [^>]*/>", "", paragraph.group(1) or "")  # the style may not exist
                    xml = xml.replace(paragraph.group(0), f"<w:p>{props}{_footer_paragraph_body(text, lang)}</w:p>", 1)
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
