#!/usr/bin/env python3
"""Render a static Markdown research overview for cloud workspaces."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.research_dashboard import DashboardData, DashboardError


def _cell(value: object) -> str:
    text = str(value or "未记录").replace("\n", " ").strip()
    if text == "Not recorded":
        text = "未记录"
    return text.replace("|", "\\|") or "未记录"


def render_report(repo_root: Path) -> str:
    """Return a preview-friendly Markdown overview."""

    overview = DashboardData(repo_root).overview()
    totals = overview["totals"]
    lines = [
        "# 数学研究项目云端概览",
        "",
        f"生成时间：{overview['generated_at']}",
        "",
        (
            f"共 {totals['projects']} 个登记项目；最近七天更新 {totals['recent']} 个；"
            f"开放义务 {totals['open_problems']} 项；待审核交接 {totals['pending_handoffs']} 项；"
            f"inbox 待整理文件 {totals['inbox']} 个。"
        ),
        "",
        "| 项目 | 角色 | 状态 | 最近更新 | 当前目标 | 下一步 | 阻碍 | 开放义务 |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for project in overview["projects"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(project["title"]),
                    _cell(project["role"]),
                    _cell(project["status"]),
                    _cell(project["last_updated"]),
                    _cell(project["target"]),
                    _cell(project["next_action"]),
                    _cell(project["blocker"]),
                    str(project["counts"]["open_problems"]),
                ]
            )
            + " |"
        )

    missing = [
        project["path"]
        for project in overview["projects"]
        if project.get("state_error")
    ]
    if missing:
        lines.extend(
            [
                "",
                "## 尚未装载状态的项目",
                "",
                "以下项目只有公开骨架，当前云端工作区没有相应的 `research_state.md`：",
                "",
                *[f"- `{path}`" for path in missing],
            ]
        )

    lines.extend(
        [
            "",
            "## 云端持久化提醒",
            "",
            "本报告只反映生成时工作区内可见的文件。需要跨会话保留的研究状态，应写入已授权的持久目标（例如连接的 GitHub 仓库），或作为可下载文件交付；不要把未提交的云端临时目录视为永久存储。",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing the public and optional local project registries.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write Markdown to this path instead of stdout.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = render_report(args.repo_root.resolve())
    except DashboardError as exc:
        print(f"Cannot build cloud report: {exc}")
        return 1
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(output)
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
