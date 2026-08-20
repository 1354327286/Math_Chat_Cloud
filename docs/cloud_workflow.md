# ChatGPT Work 云端运行约定

本仓库以 ChatGPT Work 云端任务为主要运行环境。云端任务可以读取当前工作区文件、调用已授权插件和工具、运行 Python 与 shell 命令并生成可审阅文件，但不应假定能够访问用户电脑上的磁盘、浏览器会话、凭证管理器、Ollama 服务或其他本机仓库。

## 启动与检查

在仓库根目录运行：

```bash
bash scripts/bootstrap_cloud.sh
```

脚本安装基础 Python 依赖、编译检查脚本、验证公开 `projects.json` 与可选的私有 `projects.local.json`，并检查公开 Git 跟踪范围。它不下载论文、不启动后台服务，也不建立语义索引。

## 状态装载

公开仓库只保存框架、公开示例登记和虚构示例目录。真实项目的 `projects.local.json`、问题目录、`research_state.md`、日期笔记、`memory/`、`refs/`、`handoff/`，以及 `lean/MathDailyLean/Projects/<problem_name>/` 下的问题专属 Lean 源码都被 Git 忽略，并由私有问题包迁移。开始研究前，应确认所需私有状态已经装载；缺失时必须明确说明，不能把公开框架当作最新状态。

生成适合 Work 文件预览的静态概览：

```bash
python scripts/cloud_research_report.py --output tmp/research-overview.md
```

云端不启动 `localhost` 仪表盘；`scripts/research_dashboard.py` 只保留为本地兼容工具。

## 持久化边界

云端工作目录可能随任务结束而消失。一次任务内，仓库文件仍是数学状态的规范来源；跨任务持久化则必须落到用户已授权的目标：

- 已连接并明确允许更新的 GitHub 仓库，仅用于公开框架；
- 交付给用户的私有问题包，用于真实项目登记和研究数据；
- 当前产品提供并由用户授权的持久文件空间。

只修改云端临时工作树不等于已经持久保存。结束时应说明修改了哪些文件、通过了哪些检查，以及内容是否已写入外部持久目标。没有发布授权时，不自动提交、推送、创建 PR 或覆盖远端文件。

## 外部能力

- GitHub：优先使用已连接的 GitHub 工具读取远端信息；本地 `git` 适合检查 diff 和状态，但不能假定拥有 `pull`/`push` 凭证。
- 网络：依赖当前环境的网络策略和域名白名单。文献调研优先使用可用的网页检索与连接器；脚本联网失败时记录失败，不绕过限制。
- Lean：只有用户显式要求 Lean 形式化或 Lean 审阅时，才读取 `skills/lean-formalization/SKILL.md`。每轮先固定精确命题、`sorry-free` / `provenance-complete` / `internally-closed` 验收档位、普通 Work 或持久 goal、子代理许可与（若许可）模型/推理强度/任务边界/数量和停止规则，以及工具链运行与安装权限；字段未齐不得写计划、运行或委派。先完成陈述闭合、指代消解和依赖拆解；精准文献档位下，每个外部输入必须有具体来源位置，组合性质必须引用原始组成定理并形式化组合。工具链缺失时停在准备结果，除非本轮契约已明确授权安装，才运行 `scripts/bootstrap_lean.sh --install`。代码直接写入同一仓库的 `lean/` 子项目，任何操作前同时读取根 `AGENTS.md` 与 `lean/AGENTS.md`。同一工作区内不使用 `stage`、请求包或回传包；跨工作区时，问题专属 `.lean` 源码随对应的私有问题包迁移。框架、工具链版本和依赖清单由公开 Git 仓库提供，不建立嵌套仓库，也不假定固定盘符或本机路径。
- Pro 交接：需要用户与 Pro 多轮讨论时，Work 从仓库整理自包含的 `CURRENT_PRO_HANDOFF.md`，并在能力可用时临时加入项目 Sources；否则交付给用户手动添加。Pro 只读取这一文件，不需要 GitHub 仓库、项目路径或 Work 运行目录。用户在独立 Pro 聊天中讨论，最终把交接稿带回 Work 审核；审核完成后从项目 Sources 移除临时文件。固定槽未完成时不得覆盖，并行问题改用任务专属文件。普通 Codex 子代理不是 Pro。只有跨项目、外部服务、单文件无法传递或明确需要不可变审计时才生成完整任务包。
- 语义索引：LanceDB/Ollama 是本地兼容能力。在 Work 云端默认使用 `rg`、现有 TeX/TXT/PDF 和网页检索，不启动 Ollama 或长期后台服务。

## 推荐收尾

1. 将实质数学结果写入详细记录，再刷新 `research_state.md`。
2. 运行 `python -m unittest discover -s tests -v` 和相关检查。
3. 生成必要的静态报告或问题包并交付。
4. 明确区分“当前工作区已修改”和“已经持久发布”。
