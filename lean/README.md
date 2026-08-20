# MathDailyLean

这是主仓库内的 Lean 形式化子项目，与数学讨论框架共享同一个 Git
历史。它不是公开或私有登记表中的研究问题，也不是第二个仓库。

只有显式要求 Lean 形式化、验证或审阅时才启用。正式写代码前，先按
`skills/lean-formalization/SKILL.md` 检查陈述和证明是否闭合，并把依赖拆解
写入 `<problem_dir>/memory/formalization/<slug>.md`。随后必须读取根
`AGENTS.md` 和本目录的 `AGENTS.md`。

当前目录只提供可复用骨架，尚未锁定或下载 Lean/Mathlib。检查骨架不会联网：

```bash
bash scripts/bootstrap_lean.sh --check
```

用户确认安装后，才从仓库根目录运行：

```bash
bash scripts/bootstrap_lean.sh --install
```

安装步骤会在 `tmp/lean-runtime/` 建立当前工作区专用的 elan 运行时，读取
Mathlib 当前工具链，生成 `lean-toolchain` 与 `lake-manifest.json`，获取缓存并
构建。安装成功后应审阅并提交这两个复现文件；`.lake/` 和运行时缓存不提交。

项目专属代码放在 `MathDailyLean/Projects/<problem_name>/`，共享代码只有在多个
形式化确实复用时才移入 `MathDailyLean/Common/`。`Projects/` 下除公开说明文件
外全部被 Git 忽略；跨工作区时，所选问题的 `.lean` 源码随私有问题包导出和恢复，
不携带 `.lake/`、Mathlib 缓存或运行时。私有数学计划与 Lean 声明的映射记录在
对应 `<problem_dir>/memory/formalization/` 中；`FORMALIZATION_INDEX.md` 只登记
明确允许公开的示例。
