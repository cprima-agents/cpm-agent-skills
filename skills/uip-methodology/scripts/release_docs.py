"""Zip the generated documents and publish them as a GitHub Release. A manual trigger: you run it, nothing runs by itself.

What goes into the release is stated in the manifest of the output repository (docs/manifest.yaml):

    release:
      tag_prefix: docs-v          # the tag is <tag_prefix><version>, so it says that it marks documents
      files:                      # globs, relative to the folder of the manifest
        - requirements/dmk-pdd.*.docx

The version is the version of the documents (the last history row of every artefact; they must agree). The script
refuses to run when the release would not match the zip: files under the docs folder that are not committed, a commit
that is not pushed, a tag that exists, a file pattern that finds nothing. By default the release is a draft; check it
on the release page and publish it there, or run again with --publish.

Usage:
    uv run --project <skill> <skill>/scripts/release_docs.py --docs docs            # draft release
    uv run --project <skill> <skill>/scripts/release_docs.py --docs docs --dry-run  # only show what would happen
    uv run --project <skill> <skill>/scripts/release_docs.py --docs docs --publish  # published at once
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from ruamel.yaml import YAML


def run(*cmd: str, cwd: Path | None = None) -> str:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        sys.exit(f"ERROR: {' '.join(cmd)}\n{done.stderr.strip()}")
    return done.stdout.strip()


def text(value) -> str:
    """A text pair as 'de / en', a plain value as it is."""
    if isinstance(value, dict):
        de, en = value.get("de", ""), value.get("en", "")
        return f"{de} / {en}" if de and en and de != en else (de or en)
    return str(value or "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs", type=Path, default=Path("docs"), help="folder with manifest.yaml (default: docs)")
    parser.add_argument("--name", help="name of the zip without version (default: <repository folder>-documents)")
    parser.add_argument("--publish", action="store_true", help="publish at once instead of a draft")
    parser.add_argument("--dry-run", action="store_true", help="check everything and show the plan; create nothing")
    args = parser.parse_args()

    docs = args.docs.resolve()
    manifest = YAML(typ="safe").load((docs / "manifest.yaml").read_text(encoding="utf-8")) or {}
    release = manifest.get("release") or {}
    prefix, patterns = release.get("tag_prefix"), release.get("files") or []
    if not prefix or not patterns:
        sys.exit("ERROR: manifest.yaml needs `release.tag_prefix` and `release.files`.")

    # the version: the last history row of every artefact, and they agree
    last = {a["id"]: (a.get("history") or [{}])[-1] for a in manifest.get("artefacts") or []}
    versions = {a: str(row.get("version")) for a, row in last.items() if row.get("version")}
    if len(set(versions.values())) != 1:
        sys.exit(f"ERROR: the documents are at different versions: {versions}. A release has one version.")
    version = next(iter(versions.values()))
    tag = f"{prefix}{version}"

    root = Path(run("git", "rev-parse", "--show-toplevel", cwd=docs))
    name = args.name or f"{root.name}-documents"

    # the files
    files: list[Path] = []
    for pattern in patterns:
        found = sorted(p for p in docs.glob(pattern) if p.is_file())
        if not found:
            sys.exit(f"ERROR: the pattern `{pattern}` finds no file under {docs}. Generate the documents first.")
        files += [p for p in found if p not in files]

    # the release must match the zip: what goes into it, and the manifest that names it, is committed and pushed
    problems: list[str] = []
    checked = [str(p) for p in files] + [str(docs / "manifest.yaml")]
    dirty = run("git", "status", "--porcelain", "--", *checked, cwd=root)
    if dirty:
        problems.append(f"uncommitted changes in the files of the release; commit them first:\n{dirty}")
    untracked = [p for p in files if not run("git", "ls-files", "--", str(p), cwd=root)]
    if untracked:
        problems.append("these files are not in git: " + ", ".join(str(p.relative_to(root)) for p in untracked))
    head = run("git", "rev-parse", "HEAD", cwd=root)
    upstream = subprocess.run(["git", "rev-parse", "@{u}"], cwd=root, capture_output=True, text=True).stdout.strip()
    if head != upstream:
        problems.append("the current commit is not pushed (or the branch has no upstream); push first")
    if run("git", "tag", "--list", tag, cwd=root) or run("git", "ls-remote", "--tags", "origin", tag, cwd=root):
        problems.append(f"the tag {tag} exists already; raise the version in the manifest first")

    # the notes: what changed in this version, for every document, in both languages
    lines = [f"Documents of version {version}, generated from commit {head[:9]}.", ""]
    for artefact, row in last.items():
        lines.append(f"- **{artefact.upper()} {row.get('version')}** ({row.get('date')}): {text(row.get('changes'))}")
    lines += ["", "Files:"] + [f"- `{p.relative_to(docs).as_posix()}`" for p in files]
    notes = "\n".join(lines) + "\n"

    zip_name = f"{name}-v{version}.zip"
    print(f"Release : {tag}  ({'published' if args.publish else 'draft'})")
    print(f"Commit  : {head}")
    print(f"Zip     : {zip_name}  ({len(files)} files)")
    for p in files:
        print(f"          {p.relative_to(docs).as_posix()}")
    for problem in problems:
        print(f"\nPROBLEM: {problem}")
    if args.dry_run:
        print("\nDry run: nothing created." + ("" if not problems else " Fix the problems above before the real run."))
        return
    if problems:
        sys.exit("\nERROR: no release created.")

    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / zip_name
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in files:
                zf.write(p, p.relative_to(docs).as_posix())
        cmd = ["gh", "release", "create", tag, str(archive), "--target", head, "--title", f"Documents {version}", "--notes", notes]
        if not args.publish:
            cmd.append("--draft")
        print(run(*cmd, cwd=root))


if __name__ == "__main__":
    main()
