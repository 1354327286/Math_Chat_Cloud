# 数学聊天与研究记录项目

这个项目用于在 ChatGPT Work 云端环境中持续讨论数学、查找资料、尝试证明，并把重要内容整理为结构化 Markdown 研究状态。每个数学问题使用一个独立的顶层目录；公开 `projects.json` 只保存无隐私的示例，真实项目登记保存在被 Git 忽略的 `projects.local.json`，运行时合并读取两者。

## 快速开始

把仓库和所需私有研究状态提供给 ChatGPT Work 后，可以直接发：

```text
继续 sample_problem。请先读 sample_problem/research_state.md、sample_problem/goal.md、sample_problem/progress.md、sample_problem/subgoal.md、最近日期笔记和 sample_problem/memory/，总结当前状态。然后围绕我下面的问题推进：...

要求：
- 数学结论标注置信度；
- 每个证明尝试说明关键假设；
- 失败路径写入 memory/failed_paths.md；
- 有实质进展时更新今天的日期笔记；
- 结束时给出下一步建议。
```

如果只想临时讨论，不想改文件：

```text
先别改文件，我们只讨论这个数学问题：...
```

`AGENTS.md` 是给 ChatGPT Work 读取的行为指令；这份 README 是给人看的使用说明。第一次装载仓库时运行：

```bash
bash scripts/bootstrap_cloud.sh
```

## 云端运行边界

Work 云端任务可以使用当前工作区文件、已授权插件和工具并运行 Linux 命令，但不能假定可以访问你电脑上的磁盘、浏览器会话、凭证管理器、Ollama 或其他本机仓库。云端工作目录也不应被当作永久存储：一次任务内以仓库文件为准，跨任务内容必须写入明确授权的 GitHub 目标，或作为可下载文件/问题包交付。

公开仓库只保存框架和一个虚构示例；真实 `projects.local.json`、真实问题目录、`research_state.md`、日期笔记、`memory/`、`refs/`、`handoff/`，以及 `lean/MathDailyLean/Projects/<problem_name>/` 下的问题专属 Lean 源码都必须通过私有问题包装载。缺失时，Work 应明确说明只有公开框架，不能把它当作最新研究状态。完整说明见 [ChatGPT Work 云端运行约定](docs/cloud_workflow.md)。

## 目录结构

```text
.
├── README.md
├── AGENTS.md
├── reference_index.py
├── search_references.py
├── search_arxiv_theorems.py
├── inbox/
├── docs/
├── skills/
├── lean/
│   ├── AGENTS.md
│   ├── lakefile.toml
│   ├── MathDailyLean.lean
│   └── MathDailyLean/
├── templates/
│   ├── research_state.md
│   ├── pro_task.md
│   └── pro_review.md
└── example_math_problem/
```

每个问题目录内部使用相同结构：

```text
<problem_dir>/
    ├── research_state.md
    ├── goal.md
    ├── progress.md
    ├── subgoal.md
    ├── YYYY-MM-DD.md
    ├── notes/
    ├── memory/
    ├── refs/
    ├── downloads/
    └── handoff/
```

常用文件：

| 路径 | 用途 |
| --- | --- |
| `AGENTS.md` | 给 ChatGPT Work 读取的 agent 行为指令 |
| `docs/research_state_workflow.md` | 状态文件职责、新项目创建和收尾顺序 |
| `projects.json` | 公开示例登记表；只能包含明确允许公开的虚构示例 |
| `projects.local.json` | 真实项目登记表；本地生成、被 Git 忽略并由问题包迁移 |
| `templates/research_state.md` | 新建问题目录时使用的统一状态模板 |
| `docs/reference_workflow.md` | PDF、TeX、TXT 后备、版本与校验信息的统一规范 |
| `inbox/` | 跨问题、尚未确定归属或尚未整理的外部材料入口 |
| `lean/` | Lean/Lake 子项目；框架和版本锁由 Git 提供，`Projects/` 下的问题源码由私有问题包迁移 |
| `<problem_dir>/handoff/` | 该问题与外部 Pro 或旧跨工作区形式化任务的中转记录；同项目 Lean 工作流不使用此目录 |
| `<problem_dir>/research_state.md` | 当前问题的六栏紧凑状态页 |
| `<problem_dir>/goal.md` | 当前数学问题的长期目标和精确陈述 |
| `<problem_dir>/progress.md` | 跨会话进展摘要 |
| `<problem_dir>/subgoal.md` | 当前证明分解和子目标 |
| `<problem_dir>/YYYY-MM-DD.md` | 每日研究笔记 |
| `<problem_dir>/memory/` | 推论、例子、反例、失败路径、搜索结果等结构化记忆 |
| `<problem_dir>/refs/` | PDF、论文笔记、提取文本和本地索引 |

## 状态页与详细记录

两套记录结合使用，但职责不同：`research_state.md` 是当前状态和导航入口，原有文件保存完整事实、推导与历史。

| 状态页栏目 | 状态页保留 | 详细记录位置 |
| --- | --- | --- |
| `Research State` | 当前状态、置信度、假设和简短摘要 | `goal.md`、`progress.md`、每日笔记 |
| `Known Theorems` | 当前最关键的定理 | `memory/immediate_conclusions.md`、来源笔记 |
| `Open Problems` | 主要未决问题 | `subgoal.md`、`memory/subgoals_state.md` |
| `Failed Attempts` | 路线和一句失败原因 | `memory/failed_paths.md` |
| `Current Goal` | 当前唯一目标、下一步和阻碍 | `goal.md`、`subgoal.md` |
| `References` | 当前最相关的文献 | `memory/search_results.md`、`refs/` |

数学结论、证据和历史以详细文件为准；当前工作快照以 `research_state.md` 为准。有实质进展时，先更新详细文件，再刷新状态页。状态页只写摘要并链接详情，不复制长证明和完整搜索记录。

## 日常工作流

1. 开始会话时，让 Work 先读 `research_state.md`，再读 `goal.md`、`progress.md`、`subgoal.md`、最近日期笔记和 `memory/`。
2. 讨论数学问题时，要求 Work 区分“已证明”“合理猜想”“需要验证”“可能错误”。
3. 有重要结论、反例、失败路径或文献线索时，让 Work 写回当前问题目录下的相应文件；跨两个问题的讨论分别更新，不能混写。
4. 结束前让 Work 先更新当天笔记、`progress.md` 和相关详细记录，最后刷新 `research_state.md`。

新建问题建议使用脚本，自动创建标准目录、私有状态文件和注册表条目：

```bash
python scripts/create_math_project.py my_math_problem --title "My Math Problem" --role active --description "One-line research objective"
```

创建前需要确定目录名、标题、精确目标与范围、项目角色、说明，以及它和已有问题的关系。如果其中有实质歧义，Work 会先只读检查并向你询问，不会先创建一个占位目录。

### 脱离当前讨论时的澄清边界

日常数学讨论可以依据紧邻语境理解“这个引理”“刚才的路线”等指代，不要求反复重述。只有当工作要形成独立文件交给其他读者、代理、模型或仓库，跨项目或机器传输，长期运行，或者向外部服务提交时，才必须先固定目标、假设、预期产物、验收条件和执行目的地。

如果这些实质字段存在多种合理解释，Work 应当针对缺失项反问；澄清前可以只读检查，但不能先生成半成品、委派、传输或提交，也不能静默改成较弱目标或另一种执行方式。当前语境已经唯一确定全部字段且你明确要求开始时，不会重复要求确认。

这一规则也适用于独立证明稿、外部审阅稿、子代理并行和 LaTeX 文稿审阅：目标、读者、输出格式、委派范围、权威源文件或“只诊断/允许修改”边界不清楚时先询问。明确要求子代理但任务不清楚时，不会悄悄退回另一种执行模式。

### 长时间自主研究（按需启用）

普通讨论不自动进入长时间攻坚模式。需要对一个精确定义的目标进行多轮证明、反例搜索和独立审核时，可以说：

```text
使用 $long-autonomous-math-research，围绕当前问题的这个目标持续研究：……
```

技能首先只读项目状态，向你展示拟冻结的目标、成功标准、执行模式、权限、限制和停止条件。只有你明确确认后才会创建文件并开始研究；如果你已经给出完整契约并明确说“开始”，该消息本身即视为确认。选择跨任务持久运行、子代理、远程计算或外部交接都需要单独明确授权。

每次运行使用独立目录，不再把几十个 wave 追加到 `notes/` 根目录的一个文件：

```text
<problem_dir>/notes/autonomous_runs/<run_id>/
├── contract.md
├── index.md
├── checkpoint.md
├── waves/
├── audits/
└── artifacts/
```

`contract.md` 保存冻结契约，`index.md` 每个 wave 只保留一行索引，`checkpoint.md` 保存当前阻碍和恢复动作，每个详细 wave 单独写入 `waves/`。可复用数学结论仍进入原有 `memory/`，项目当前状态仍以 `research_state.md` 为准，不建立第二套研究状态。旧的 `notes/autonomous_run_*.md` 保持只读兼容，不会自动迁移或继续追加。

只要成功标准尚未达到、用户没有明确暂停、也不存在真正的权限或外部环境阻碍，运行就必须保持 `active` 并进入下一 wave。当前路线困难、需要证明新定理、完成固定范围计算或已经运行很多 waves 都不是停止条件。单次任务因产品或上下文边界结束时记为 `interrupted_runtime`，不能写成研究暂停或完成；如果你要求跨任务持续运行，需要在契约中明确选择并授权 `persistent-goal`。

可以随时检查新格式运行目录：

```bash
python scripts/check_autonomous_runs.py <problem_dir>
```

## 云端静态研究概览

需要同时查看多个问题的当前目标、下一步、开放义务和交接状态时，生成 Work 可以直接预览的 Markdown：

```bash
python scripts/cloud_research_report.py --output tmp/research-overview.md
```

报告合并读取公开 `projects.json` 和私有 `projects.local.json`，再读取各问题的 `research_state.md` 与 `handoff/manifest.json`，不会修改研究文件。`scripts/research_dashboard.py` 只保留为本地兼容工具；Work 云端不启动无法从用户设备访问的 `localhost` 服务。

## 在云端任务或电脑之间迁移单个问题

Git 仓库代码通过 GitHub 或当前工作区提供；被 Git 忽略的私有研究状态使用问题包单独迁移：

```bash
python scripts/problem_bundle.py export sample_problem --dry-run
python scripts/problem_bundle.py export sample_problem
python scripts/problem_bundle.py export sample_problem --inbox inbox/额外材料.md
python scripts/problem_bundle.py inspect tmp/problem_bundles/<bundle>.zip
```

导出器会自动包含该问题 Markdown 中明确引用且实际存在的 `inbox/` 文件，以及 `lean/MathDailyLean/Projects/<problem_name>/` 下该问题的 `.lean` 源码；`--inbox` 只用于补充尚未被引用的材料，不会打包整个 inbox，也不会携带其他问题的 Lean 代码、`.lake/`、Mathlib 缓存或运行时。在目标工作区装载仓库后，先预演再恢复：

```bash
python scripts/problem_bundle.py restore /workspace/transfer/<bundle>.zip --dry-run
python scripts/problem_bundle.py restore /workspace/transfer/<bundle>.zip
```

问题包同时携带所选项目的私有登记条目。恢复前会完整验证清单、文件大小、SHA-256 和登记冲突；默认遇到不同内容或同名异义的登记就停止，并保证零写入。成功恢复后，登记条目自动写入被忽略的 `projects.local.json`。压缩包未加密，不应通过公开渠道传输未公开研究。完整范围、冲突策略和安全说明见 [Portable Private Problem Bundles](docs/problem_bundle.md)。

如果导出/恢复对象、附带的 `inbox/` 材料、输出或目标位置、冲突策略、传输渠道不清楚，Work 会先执行必要的只读检查或 dry-run，再向你确认；不会在歧义仍存在时创建、恢复、覆盖或传输问题包。

## Pro 项目内委派与跨项目中转

如果你需要亲自与 Pro 多轮讨论，默认流程是在同一个 ChatGPT Work 项目里新开一个独立聊天并在编辑器中选择 Pro，而不是启动当前 Work 的子代理。普通 Codex 子代理没有自动切换成 Pro 的能力，不能以“高推理代理”为由冒充 Pro。

当前 Work 先读取仓库中的研究状态，再生成一份自包含的首轮问题，固定命名为 `CURRENT_PRO_HANDOFF.md`。仓库只供 Work 整理题目使用；Pro 不需要查看 GitHub 仓库，也不应被要求读取项目路径。如果当前会话具有项目 Sources 的新增或替换能力，Work 会把该文件临时加入项目；否则交付文件，由你在项目 Sources 中添加一次。随后在项目里新建聊天并选择 Pro，它就可以直接读取这个固定文件，不必再次复制长提示词。

```text
把当前最早的承重缺口导出为临时项目文件 CURRENT_PRO_HANDOFF.md。把必要定义、已知结果、失败路线、现有假设和禁止替代条件全部写进文件；不要让 Pro 查看仓库。要求 Pro 在讨论结束时区分已证明、条件性、猜测、反例和待验证结论。不要启动子代理或生成外部任务包。
```

首轮问题包含：精确目标与假设、总目标中的位置、必要定义、已有结论及状态、最早缺口、失败路线、允许与禁止的替代、预期产物和验收标准。它必须独立可读，不引用只有 Work 能看到的文件路径或当前聊天片段。同一项目的聊天能读取项目 Sources，因此只需要临时加入这一份文件，不需要把仓库加入项目。[ChatGPT 项目与聊天](https://learn.chatgpt.com/docs/projects)

随后由你在新的 Pro 聊天里自由追问、修正和探索，不设置轮数上限，因此不会发生两个代理在后台无休止互相讨论。讨论结束时，让 Pro 输出一份自包含的最终交接稿，再将这段 Markdown 或单个文件带回 Work；Work 对照仓库审核并更新研究记录。审核完成后，Work 删除或提示你移除项目 Sources 中的 `CURRENT_PRO_HANDOFF.md`。官方说明指出项目文件适用独立的保留规则，因此这里准确说的是“从项目 Sources 移除”，不能承诺后端立即永久擦除。[ChatGPT Work 数据保留](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview)

固定文件槽同一时间只容纳一个活动问题，未完成时不能覆盖。如果确实要并行与 Pro 讨论多个问题，应明确改用带任务名的临时文件，例如 `PRO_HANDOFF_integralization_torus.md`，并分别在审计后清理。

[ChatGPT Work 子代理](https://learn.chatgpt.com/docs/agent-configuration/subagents)只用于准备交接说明、独立批判或审核 Pro 返回，不能代替 Pro。若你另行要求普通 Codex 代理内部辩论，才启用一次初答加至多三次追问的上限；继续需要你重新授权，而且必须明确标注这不是 Pro 讨论。

只有以下情况才使用 `scripts/pro_handoff.py` 的文件中转：

- Pro 位于另一个项目或外部服务；
- 自包含问题仍无法通过目标聊天可接受的形式传递；
- 你明确要求可移植、不可变、带哈希的审计包；
- 已经存在需要导入或审阅的中转任务。

短问题可以这样导出：

```bash
python scripts/pro_handoff.py export sample_problem --question "要 Pro 解决的精确问题" --slug open-lemma --user-authorized
```

较长问题适合使用 UTF-8 Markdown，并按需加入当前问题目录内的上下文：

```bash
python scripts/pro_handoff.py export sample_problem --question-file inbox/pro_question.md --context memory/failed_paths.md --user-authorized
```

外部返回稿保持原样导入和审核：

```bash
python scripts/pro_handoff.py import sample_problem <task_id> inbox/pro_answer.md
python scripts/pro_handoff.py review sample_problem <task_id> --summary "审核结论"
python scripts/pro_handoff.py status sample_problem
```

外部提交仍需要单独授权可用的浏览器或连接器操作。每个问题的 `handoff/` 中除 `.gitkeep` 外的内容都被 Git 忽略，并由公开范围检查阻止提交；跨问题或未归属的外部材料放入根目录 `inbox/`。

## 使用 Lean 形式化验证

Lean 验证是当前项目中需要显式触发的工作流。只有你明确说“用 Lean 形式化这个定理”“用 Lean 验证这个证明”或“用 Lean 审阅这份稿件中的某个命题”时，Work 才读取 `skills/lean-formalization/SKILL.md`。普通数学研究不会因为 Lean 可能有帮助而自动安装工具链或启动形式化。

第一阶段完全不需要 Lean：Work 先检查定理和证明是否内部闭合，消除“如上”“自然映射”“类似可得”等不明确指代，固定全部假设、定义、编号引用和外部结果，再把证明拆成有向无环的形式化义务。每项义务记录精确陈述、依赖、来源和预期 Lean 角色；结果写成 `<problem_dir>/memory/formalization/<slug>.md`，或者在一次性任务中直接返回。

如果目标含糊、证明有已知数学缺口或引用未解析，流程停在准备阶段并报告阻碍。只有准备结果为 `ready` 时才进入 Lean。仓库已经跟踪 `lean/` 骨架，但骨架不等于安装许可：工具链缺失时，Work 会展示拆解方案、最终声明和验收标准，然后等你确认；确认前不会下载或安装 elan、Lean、Lake、Mathlib。

确认后，从仓库根目录运行 `bash scripts/bootstrap_lean.sh --install`。脚本在被忽略的 `tmp/lean-runtime/` 放置当前工作区运行时，并在 `lean/` 生成需要审阅和跟踪的 `lean-toolchain` 与 `lake-manifest.json`。Work 在任何 Lean 操作前同时读取根 `AGENTS.md` 和 `lean/AGENTS.md`，再按依赖顺序写代码、运行局部检查和完整构建。`lean/` 与数学框架共享一个 Git 历史，不含嵌套 `.git`，也不登记为数学问题。

同仓库流程不生成请求包、传输 manifest、inbox/outbox 或回传文件；数学拆解保留在 `<problem_dir>/memory/formalization/`，代码放在 `lean/MathDailyLean/Projects/<problem_name>/`。两者都属于私有问题数据：计划和源码映射记录在该问题的 `memory/formalization/` 中，源码随问题包迁移，不能写入公开 `lean/FORMALIZATION_INDEX.md`。最终陈述对应、定义语义、构建、`sorry`、`#print axioms`、外部结果和隐藏接口都由执行形式化的 Work 自己核对，不默认要求用户阅读 Lean 代码；只有出现非等价数学目标、增补假设或外部边界政策等实质选择时才询问用户。审计完成后才能更新研究状态。

旧的 `scripts/formalization_handoff.py` 仅保留为 Windows/跨工作区交接的兼容工具，不是云端同项目工作流的默认入口。

收尾提示词：

```text
请收尾：
1. 更新今天的日期笔记；
2. 更新 progress.md；
3. 如果有新的子目标或失败路径，更新 subgoal.md 或 memory/；
4. 根据上述详细记录刷新 research_state.md；
5. 用三句话总结今天完成了什么、还卡在哪里、下次从哪里开始。
```

## 默认工作区搜索

Work 默认采用以下顺序，不会主动启动 LanceDB、Ollama 或嵌入模型：

```text
项目 memory/、日期笔记和 notes/
→ arXiv 文章强制获取版本匹配的源码包
→ 搜索主 TeX
→ 源码确实不可用时才搜索 PDF 提取 TXT，并记录原因
→ 回到 PDF 或正式发表版本核对
→ 阅读指定论文：工作区资料不足时联网
→ 文献调研：即使工作区已有资料也继续联网
```

先搜索项目记忆：

```bash
rg --no-ignore -n -i "Noetherian localization" sample_problem/memory sample_problem/notes -g "*.md" -g "!**/.lancedb/**" -g "!**/*.lancedb/**"
```

查阅 arXiv 论文时，即使本地已经有 PDF 或提取 TXT，也必须先获取所用 arXiv 版本对应的源码包，解压到当前问题的 `refs/sources/`，并确定主 `.tex` 文件。随后优先搜索主 `.tex`：

```bash
rg --no-ignore -n -i "Noetherian localization" sample_problem/refs -g "*.tex" -g "!**/.lancedb/**" -g "!**/*.lancedb/**"
```

只有源码包不可获取、不含可用 TeX、源码不完整、无法可靠解码或不能形成忠实的可搜索表示时，才搜索 PDF 提取的 TXT：

```bash
rg --no-ignore -n -i "Noetherian localization" sample_problem/refs -g "*.txt" -g "!**/.lancedb/**" -g "!**/*.lancedb/**"
```

问题目录中的研究资料被 Git 主动忽略，因此这里必须使用 `--no-ignore`；命令应限制在当前问题目录内，并排除 LanceDB 等生成目录。

上述例外必须在 `refs/catalog.json` 的 `notes` 中记录具体原因和尝试的 arXiv 版本；只有这种情况下，arXiv 条目的 `tex_main` 才可以是 `null`。同一论文同时存在 TeX 和提取 TXT 时，默认不把它们当作两个独立来源，也不同时搜索。TeX 适合发现定理和公式；重要陈述、编号、页码及版本差异应回到 PDF 或正式发表版本核对。对于指定论文的阅读任务，本地资料不足时再使用 arXiv、LeanSearch、Matlas 或网页搜索。

### 阅读与文献调研

Work 会区分两种任务：

- **阅读指定论文或核对已知结果：** 先按 TeX → TXT 后备 → PDF 核对的本地顺序查阅；缺少准确上下文、权威版本或被引用来源时再联网。
- **文献调研：** 当你要求查找相关结果、研究现状、后续工作、新颖性或最新版本时，本地材料只用于提取术语、作者和引用线索，即使已经存在相关 PDF 或 TeX，也会继续联网搜索。

工作区参考文献是阅读缓存和研究记忆，不是联网检索的边界。明确提出“联网搜索”“查最新文献”“核对当前研究现状”或“寻找更新工作”时，Work 必须联网，不会因为工作区已有材料而停止。

下载和整理文献时，按 [参考文献工作流](docs/reference_workflow.md) 维护 `refs/catalog.json`，记录 arXiv 版本、主 TeX、TXT 后备、PDF、来源和 SHA-256。对 arXiv 文章，版本匹配的源码获取是必做步骤，不是可选优化。目录结构和元数据可以用以下命令检查：

```bash
python scripts/check_reference_catalog.py <problem_dir>/refs/catalog.json --check-files
```

## 可选语义索引（仅手动触发）

LanceDB + Ollama 流程只作为本地兼容能力保留。Work 云端不假定存在 Ollama 服务；普通的“查资料”“搜索文献”或“继续研究”只使用关键词、已有文献和网页检索。只有你明确提供可用服务并要求“语义搜索”“使用 LanceDB/Ollama”“生成嵌入”或“构建/更新索引”时才会运行语义流程。

`search_references.py` 用于搜索 `refs/` 下的 `.md`、`.tex`、`.txt` 文件。它会递归收集文本文件，并跳过 LanceDB 索引目录。

手动运行该脚本时，它会尝试使用 LanceDB + Ollama 做语义搜索；如果 Ollama 不可用，会回退到关键词搜索。除非明确需要，不要使用 `--force`，以保留现有增量索引流程。

```bash
python search_references.py sample_problem/refs "Noetherian localization" --top_k 5
```

跳过索引构建，直接搜索现有索引或关键词 fallback：

```bash
python search_references.py sample_problem/refs "flat descent" --no-build
```

强制重建索引：

```bash
python search_references.py sample_problem/refs "derived completion" --force --verbose
```

一行一个 JSON 结果，方便脚本处理：

```bash
python search_references.py sample_problem/refs "comparison morphism" --jsonl
```

禁用关键词 fallback；如果语义搜索不可用则报错：

```bash
python search_references.py sample_problem/refs "spectral sequence" --no-fallback
```

## arXiv 定理搜索

`search_arxiv_theorems.py` 调用外部定理搜索服务，用来找相关定理、引理和定义。默认先用 LeanSearch；如果 LeanSearch 不可访问，会自动回退到 Matlas。

```bash
python search_arxiv_theorems.py "derived completion flat base change" --num 10
```

也可以指定服务：

```bash
python search_arxiv_theorems.py "Noetherian ring localization flat" --provider matlas --num 10
python search_arxiv_theorems.py "Noetherian ring localization flat" --provider leansearch --num 10
```

返回 JSON 里会包含实际使用的 `provider` 和可能的 `fallback_errors`。这个脚本需要网络和外部服务可用，适合在工作区资料不足或进行文献调研时使用；若环境网络策略阻止访问，应记录失败并改用可用的网页检索工具。

## 可选索引依赖

本地兼容语义搜索依赖：

- Python
- `lancedb`
- `pyarrow`
- Ollama 服务
- Ollama 模型：`nomic-embed-text:latest`

安装仓库基础包（不拉取外部运行依赖）：

```bash
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

明确需要且运行环境具备 Ollama 时再安装可选依赖：

```bash
python -m pip install -e ".[semantic]"
```

如果 Ollama 不可用，`search_references.py` 默认会退回关键词搜索；结果中会出现：

```json
{"search_type": "keyword"}
```

## 可选语义索引 Python API

可以在具备语义索引服务的脚本环境中直接使用：

```python
from reference_index import ReferenceIndex

idx = ReferenceIndex("sample_problem/refs")
idx.build()
results = idx.search("edge morphism", top_k=5, fallback=True)
```

关键词 fallback：

```python
results = idx.keyword_search("descent obstruction", top_k=5)
```

## 记录规范

建议这样分配内容：

- 当前问题的 `Research State`、`Known Theorems`、`Open Problems`、`Failed Attempts`、`Current Goal`、`References`：`<problem_dir>/research_state.md`
- 当天讨论、灵感、临时推导：`<problem_dir>/YYYY-MM-DD.md`
- 总体进展：`<problem_dir>/progress.md`
- 当前证明路线：`<problem_dir>/subgoal.md`
- 失败证明：`<problem_dir>/memory/failed_paths.md`
- 反例：`<problem_dir>/memory/counterexamples.md`
- 简单例子：`<problem_dir>/memory/toy_examples.md`
- 文献搜索：`<problem_dir>/memory/search_results.md`

## 注意事项

- 不要只把关键数学内容留在聊天里，重要内容要写入文件。
- 如果 Work 给出强结论，要求它列出使用的假设。
- 如果某一步依赖文献，要求记录来源和适用条件。
- 对重要证明，至少做一次反例尝试和一次逐段检查。
- `search_references.py` 没有项目级 `problem-id` 参数；目前按目录组织项目。

提交框架更新前，检查暂存区没有研究正文、PDF、TeX 源码包或索引：

```bash
python scripts/check_public_scope.py
```

检查仓库目前全部已跟踪文件：

```bash
python scripts/check_public_scope.py --tracked
```

可选地启用仓库自带的 pre-commit hook，让每次提交自动执行暂存区检查：

```bash
git config core.hooksPath .githooks
```

运行全部离线测试和注册表检查：

```bash
python -m unittest discover -s tests -v
python scripts/check_project_registry.py
```
