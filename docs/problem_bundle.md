# Portable Private Problem Bundles

The public Git repository and private mathematical research data have separate
lifecycles. Clone or pull the repository normally, and move one problem's
ignored research state with `scripts/problem_bundle.py`.

## What a bundle contains

For one project registered in the merged public/local registry, export includes:

- the complete project registry record (`path`, `title`, `role`, and `description`);
- the project-local `README.md` when present;
- `research_state.md`, `goal.md`, `progress.md`, and `subgoal.md` when present;
- dated root notes such as `2026-08-07.md`;
- `notes/`, `memory/`, `refs/`, `downloads/`, and `handoff/`;
- `.lean` source files under
  `lean/MathDailyLean/Projects/<problem_name>/` for this problem only;
- existing `inbox/` files referenced anywhere in those Markdown files;
- any additional `inbox/` files or directories explicitly named with `--inbox`.

Referenced inbox paths are discovered from relative Markdown links and inline
path mentions such as `../inbox/report.md` or `../../inbox/report.md`. A broken
inbox reference stops export instead of silently producing an incomplete
bundle. Unreferenced inbox material is not included.

The exporter excludes public framework files already supplied by Git, `.gitkeep`,
LanceDB and extracted-reference caches, Python/LaTeX intermediates, generated
`.reader.md` companions, Lean/Lake build products, Mathlib packages, and the Lean
runtime. Only `.lean` files from the selected problem's exact Lean module
directory are accepted; another problem's Lean directory is never included.
Reference PDFs, source archives, formal TeX manuscripts, compiled PDFs, catalog
files, and handoff evidence remain included.

The ZIP manifest records repository-relative paths, byte sizes, SHA-256 hashes,
file modification times, project metadata, the current Git commit/branch/remote,
and every discovered or explicit inbox selection. SHA-256 detects corruption or unexpected
changes; it is not a signature and does not prove who created the archive.

Problem bundles are not encrypted. Store or transmit unpublished research bundles
through an appropriately private or encrypted channel.

The public repository ignores everything below
`lean/MathDailyLean/Projects/` except its tracked `README.md`. The public-scope
checker independently rejects problem-specific Lean source even if it is
force-added to Git. Public framework files, `lean-toolchain`,
`lake-manifest.json`, and `lakefile.toml` remain supplied by the repository.

## Clarify the transport operation

Use recent discussion when it uniquely identifies the operation. Before creating
an archive or restoring files, identify:

- whether the user wants export, inspection, or restore;
- the one registered problem or exact bundle involved;
- any additional `inbox/` material and any intended exclusions;
- the output location or destination repository, using the ignored default
  bundle directory when the user requested only a local archive;
- for restore, the conflict policy and whether differing mathematical states
  require semantic reconciliation;
- before actual transmission, the intended channel and whether its privacy is
  suitable for the unencrypted bundle.

If a material field has more than one reasonable interpretation, inspect or
dry-run read-only as useful, then ask the user. Do not create an archive,
restore files, choose `--overwrite`, or transmit anything while ambiguity
remains. A complete request that explicitly asks to proceed needs no redundant
confirmation.

## Export

Preview the automatically discovered scope without creating or hashing an archive:

```bash
python scripts/problem_bundle.py export sample_problem --dry-run --list
```

Create a bundle in the default ignored directory `tmp/problem_bundles/`:

```bash
python scripts/problem_bundle.py export sample_problem
```

Add inbox material that belongs to this problem but is not referenced by its Markdown:

```bash
python scripts/problem_bundle.py export sample_problem \
  --inbox inbox/relevant_report.md \
  --inbox inbox/another_relevant_directory
```

Choose an explicit output path when creating a cloud artifact or copying to an
approved encrypted destination:

```bash
python scripts/problem_bundle.py export sample_problem \
  --output /workspace/transfer/sample-problem.zip
```

The exporter refuses to replace an existing ZIP unless `--overwrite-output` is
explicitly supplied.

## Inspect and verify

Inspection streams every archived file and verifies its size and SHA-256:

```bash
python scripts/problem_bundle.py inspect /workspace/transfer/sample-problem.zip
python scripts/problem_bundle.py inspect /workspace/transfer/sample-problem.zip --list
```

## Restore in another workspace or computer

First make the repository available and check out the desired branch. Then
preview restoration:

```bash
cd Math_Chat_Cloud
python scripts/problem_bundle.py restore /workspace/transfer/sample-problem.zip --dry-run
```

Restore after the preview succeeds:

```bash
python scripts/problem_bundle.py restore /workspace/transfer/sample-problem.zip
```

Restore always verifies the whole ZIP before writing. Existing files with the
same hash are left unchanged. If any existing file differs, the default mode
reports all conflicts and writes nothing. Resolve the differences manually, or
choose one explicit policy:

The bundle's project record is also checked before any file write. A missing
project is registered in the ignored `projects.local.json` after payload restore;
an identical registration is left unchanged, while a same-slug different record
stops restoration with zero writes.

```bash
# Keep differing destination files; restore only missing files.
python scripts/problem_bundle.py restore bundle.zip --keep-existing

# Replace differing destination files with the bundle versions.
python scripts/problem_bundle.py restore bundle.zip --overwrite
```

### Conflicting research states

Do not treat differing research files as a mechanical copy conflict and do not
automatically use `--overwrite`. Read the local and bundled versions together
with the problem's detailed records, then propose a semantic merge:

- append and deduplicate chronological logs;
- preserve failures, counterexamples, examples, searches, and evidence from both sides;
- reconcile `subgoal.md` against the newer proof obligations;
- rebuild `research_state.md` as a compact snapshot only after detailed records agree.

Preserve both versions until the merge is verified. Ask the user to decide
incompatible mathematical conclusions or ambiguous provenance. After approved
manual reconciliation, use `restore ... --keep-existing` to retain the merged
local files while adding any remaining missing bundle files.

Treat differing `.lean` source files the same way: inspect both versions and
reconcile declarations and proof dependencies before choosing an overwrite
policy. A successful compile of one side is not by itself a reason to discard
the other side.

After restoration, validate references and regenerate disposable reader copies
when relevant:

```bash
python scripts/check_reference_catalog.py sample_problem/refs/catalog.json --check-files
python scripts/generate_tex_reader.py sample_problem/notes/proof.tex
bash scripts/bootstrap_lean.sh --check
```

If the pinned Lean environment is already installed, also compile the restored
problem modules using the audit commands in `lean/AGENTS.md`. The problem bundle
does not install or update Lean.

Avoid editing the same private problem state independently in multiple workspaces.
The bundle is a transport and integrity format, not a multi-writer merge system.
