#!/usr/bin/env python3
"""Build and render a LaTeX manuscript reproducibly in the Work cloud."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


WARNING_RE = re.compile(
    r"LaTeX Warning|Package .* Warning|Overfull|Underfull|pdfTeX warning|"
    r"undefined references?|undefined citations?|multiply defined|Rerun to get",
    re.IGNORECASE,
)
FATAL_WARNING_RE = re.compile(
    r"undefined references?|undefined citations?|(?:Reference|Citation).*undefined|"
    r"multiply defined|Rerun to get",
    re.IGNORECASE,
)


class BuildError(RuntimeError):
    pass


def system_tool(name: str) -> str | None:
    system = Path("/usr/bin") / name
    if system.is_file() and os.access(system, os.X_OK):
        return str(system)
    return shutil.which(name)


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-80:])
        raise BuildError(f"Command failed ({result.returncode}): {' '.join(command)}\n{tail}")
    return result


def ensure_tex_runtime(repo_root: Path) -> tuple[Path, Path, dict[str, str]]:
    pdftex = system_tool("pdftex")
    if not pdftex:
        raise BuildError("pdftex is not available in this workspace")

    texmf = Path("/usr/share/texlive/texmf-dist")
    latex_ltx = texmf / "tex/latex/base/latex.ltx"
    cm_map = texmf / "fonts/map/dvips/amsfonts/cm.map"
    symbols_map = texmf / "fonts/map/dvips/amsfonts/symbols.map"
    for required in (latex_ltx, cm_map, symbols_map):
        if not required.is_file():
            raise BuildError(f"Required TeX runtime file is missing: {required}")

    runtime = repo_root / "tmp/tex-runtime"
    format_dir = runtime / "format"
    map_dir = runtime / "maps"
    format_dir.mkdir(parents=True, exist_ok=True)
    map_dir.mkdir(parents=True, exist_ok=True)

    base_env = os.environ.copy()
    base_env["TEXMF"] = f"{texmf}//"
    fmt = format_dir / "pdflatex.fmt"
    if not fmt.is_file():
        run(
            [
                pdftex,
                "-ini",
                "-etex",
                "-jobname=pdflatex",
                "-progname=pdflatex",
                str(latex_ltx),
            ],
            cwd=format_dir,
            env=base_env,
        )

    combined_map = map_dir / "pdftex.map"
    map_text = cm_map.read_text(encoding="utf-8") + "\n" + symbols_map.read_text(encoding="utf-8")
    if not combined_map.is_file() or combined_map.read_text(encoding="utf-8") != map_text:
        combined_map.write_text(map_text, encoding="utf-8")

    env = os.environ.copy()
    env["TEXMF"] = f"{texmf}//"
    env["TEXFORMATS"] = f"{format_dir}:"
    env["TEXFONTMAPS"] = f"{map_dir}:{texmf / 'fonts/map'}//:"
    return Path(pdftex), fmt, env


def compile_manuscript(
    source: Path,
    build_dir: Path,
    repo_root: Path,
    passes: int,
) -> tuple[Path, Path]:
    if "{" in source.name or "}" in source.name:
        raise BuildError("TeX source names containing braces are unsupported")
    pdftex, fmt, env = ensure_tex_runtime(repo_root)
    build_dir.mkdir(parents=True, exist_ok=True)
    env["TEXINPUTS"] = f"{source.parent}:"
    env["BIBINPUTS"] = f"{source.parent}:"

    command = [
        str(pdftex),
        f"-fmt={fmt}",
        "-progname=pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={build_dir}",
        rf"\pdfoutput=1\input{{{source.name}}}",
    ]

    bibliography_done = False
    for index in range(passes):
        run(command, cwd=source.parent, env=env)
        aux = build_dir / f"{source.stem}.aux"
        if index == 0 and aux.is_file() and "\\bibdata" in aux.read_text(encoding="utf-8", errors="replace"):
            bibtex = system_tool("bibtex")
            if not bibtex:
                raise BuildError("The manuscript uses BibTeX but bibtex is unavailable")
            run([bibtex, source.stem], cwd=build_dir, env=env)
            bibliography_done = True

    if (build_dir / f"{source.stem}.bcf").is_file() and not bibliography_done:
        raise BuildError("The manuscript appears to require Biber, which this builder does not provide")

    pdf = build_dir / f"{source.stem}.pdf"
    log = build_dir / f"{source.stem}.log"
    if not pdf.is_file() or not log.is_file():
        raise BuildError("TeX completed without producing the expected PDF and log")
    return pdf, log


def log_warnings(log: Path) -> list[str]:
    warnings: list[str] = []
    seen: set[str] = set()
    for raw in log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and WARNING_RE.search(line) and line not in seen:
            seen.add(line)
            warnings.append(line)
    return warnings


def pdf_page_count(pdf: Path) -> int:
    pdfinfo = system_tool("pdfinfo")
    if not pdfinfo:
        raise BuildError("pdfinfo is unavailable")
    result = subprocess.run(
        [pdfinfo, str(pdf)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise BuildError(f"pdfinfo failed:\n{result.stdout}")
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise BuildError("pdfinfo did not report a page count")
    return int(match.group(1))


def render_pdf(pdf: Path, build_dir: Path, dpi: int) -> list[Path]:
    pdftoppm = system_tool("pdftoppm")
    if not pdftoppm:
        raise BuildError("pdftoppm is unavailable")
    render_dir = build_dir / "render"
    render_dir.mkdir(parents=True, exist_ok=True)
    for old in render_dir.glob("page-*.png"):
        old.unlink()
    result = subprocess.run(
        [pdftoppm, "-png", "-r", str(dpi), str(pdf), str(render_dir / "page")],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise BuildError(f"pdftoppm failed:\n{result.stdout}")
    return sorted(render_dir.glob("page-*.png"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="authoritative TeX source")
    parser.add_argument("--build-dir", type=Path, help="build directory (default: tmp/tex-build/<stem>)")
    parser.add_argument("--passes", type=int, default=3, help="number of TeX passes (default: 3)")
    parser.add_argument("--dpi", type=int, default=130, help="render resolution (default: 130)")
    parser.add_argument("--no-render", action="store_true", help="compile without page rendering")
    parser.add_argument("--strict", action="store_true", help="fail when any final-log warning remains")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    source = args.source.resolve()
    if not source.is_file() or source.suffix.lower() != ".tex":
        print(f"Invalid TeX source: {source}", file=sys.stderr)
        return 2
    if args.passes < 2:
        print("--passes must be at least 2", file=sys.stderr)
        return 2
    build_dir = (args.build_dir or (repo_root / "tmp/tex-build" / source.stem)).resolve()

    try:
        pdf, log = compile_manuscript(source, build_dir, repo_root, args.passes)
        warnings = log_warnings(log)
        pages = pdf_page_count(pdf)
        renders = [] if args.no_render else render_pdf(pdf, build_dir, args.dpi)
    except BuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = {
        "source": str(source),
        "pdf": str(pdf),
        "log": str(log),
        "pages": pages,
        "warnings": warnings,
        "renders": [str(path) for path in renders],
    }
    report_path = build_dir / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Source: {source}")
    print(f"PDF: {pdf}")
    print(f"Pages: {pages}")
    print(f"Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"  - {warning}")
    if renders:
        print(f"Rendered pages: {len(renders)} in {renders[0].parent}")
    print(f"Report: {report_path}")

    if any(FATAL_WARNING_RE.search(item) for item in warnings):
        return 3
    if args.strict and warnings:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
