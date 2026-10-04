import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class DetachedWorkflowPolicyTests(unittest.TestCase):
    def test_root_policy_preserves_daily_shorthand_but_gates_detached_work(self):
        agents = read("AGENTS.md")
        compact = " ".join(agents.split())
        self.assertIn("## Detached Work Boundary", agents)
        self.assertIn("Ordinary mathematical discussion may resolve informal pronouns", compact)
        self.assertIn("ask the user for the missing specification", compact)
        self.assertIn("make no detached-work write while waiting", compact)
        self.assertIn("needs no redundant confirmation", compact)

    def test_pro_handoff_separates_interactive_chat_from_subagents(self):
        skill = read("skills/pro-research-handoff/SKILL.md")
        compact_skill = " ".join(skill.split())
        script = read("scripts/pro_handoff.py")
        self.assertIn("## Choose the route by who must continue the discussion", skill)
        self.assertIn("Use **a separate Pro chat in the same project** by default", skill)
        self.assertIn("Never claim that a subagent thread is a user-facing Pro chat", skill)
        self.assertIn("Do not treat a subagent as Pro", skill)
        self.assertIn("at most three follow-ups", skill)
        self.assertIn("Pro receives only the brief", skill)
        self.assertIn("Do not add the repository to project Sources", compact_skill)
        self.assertIn("CURRENT_PRO_HANDOFF.md", skill)
        self.assertIn("Do not claim immediate permanent deletion", skill)
        self.assertIn("## Resolve the handoff specification", skill)
        self.assertIn("While waiting, do not delegate", skill)
        self.assertIn("--user-authorized", skill)
        self.assertIn("if not user_authorized:", script)
        self.assertIn('"user_authorized": True', script)

    def test_standalone_and_delegated_work_ask_instead_of_switching_targets(self):
        proof = read("skills/write-self-contained-math-proof/SKILL.md")
        recursive = read("skills/recursive-proving/SKILL.md")
        self.assertIn("## Resolve the standalone deliverable", proof)
        self.assertIn("make no standalone-proof write while waiting", proof)
        self.assertIn("ask a focused question before spawning anything", recursive)
        self.assertIn("do not silently continue sequentially instead", recursive)

    def test_transport_and_manuscript_work_have_specialized_gates(self):
        bundle = read("docs/problem_bundle.md")
        review = read("skills/review-latex-math-manuscript/SKILL.md")
        self.assertIn("## Clarify the transport operation", bundle)
        self.assertIn("Do not create an archive", bundle)
        self.assertIn("If more than one", review)
        self.assertIn("before compiling, generating files, or editing", review)

    def test_skill_ui_prompts_name_the_skill(self):
        proof_ui = read("skills/write-self-contained-math-proof/agents/openai.yaml")
        review_ui = read("skills/review-latex-math-manuscript/agents/openai.yaml")
        self.assertIn("$write-self-contained-math-proof", proof_ui)
        self.assertIn("$review-latex-math-manuscript", review_ui)

    def test_progressive_retrieval_preserves_authority_and_retractions(self):
        agents = " ".join(read("AGENTS.md").split())
        self.assertIn("latest 3–5 complete dated entries", agents)
        self.assertIn("heading boundaries", agents)
        self.assertIn("newer timestamp does not validate", agents)
        self.assertIn("withdrawn premises", agents)
        self.assertIn("user pauses", agents)
        self.assertIn("reopening condition", agents)
        self.assertIn("Self-review is not independent or formal verification", agents)
        self.assertIn("projects.local.json", agents)
        self.assertIn("missing private state", agents.lower())

    def test_compaction_is_named_scope_opt_in_and_not_proof_certification(self):
        agents = " ".join(read("AGENTS.md").split())
        self.assertIn("exceeds 24,576 bytes AND a substantive milestone", agents)
        self.assertIn("explicit agreement before drafting, archiving, or rewriting", agents)
        self.assertIn("Never automatically compact progress, daily, or memory logs", agents)
        self.assertIn("checks navigation, not mathematical validity", agents)
        self.assertIn("docs/state_compaction.md", agents)

    def test_correspondence_is_conditionally_routed_without_sending_authority(self):
        agents = " ".join(read("AGENTS.md").split())
        self.assertIn("docs/email_workflow.md", agents)
        self.assertIn("manuscript finalization/release", agents)
        self.assertIn("not at every compile", agents)
        self.assertIn("never treat silence as agreement or a draft as sent", agents)
        self.assertIn("Do not send external messages without an explicit request", agents)

    def test_same_project_lean_workflow_is_explicit_and_has_setup_gate(self):
        agents = read("AGENTS.md")
        skill = read("skills/lean-formalization/SKILL.md")
        compact_skill = " ".join(skill.split())
        ui = read("skills/lean-formalization/agents/openai.yaml")
        self.assertIn("Only when the user explicitly asks", agents)
        self.assertIn("Do not create request packets", agents)
        self.assertIn("lean/AGENTS.md", agents)
        self.assertIn("Audit before using Lean", skill)
        self.assertIn("Stop before infrastructure changes", skill)
        self.assertIn("shared Git history", compact_skill)
        self.assertIn("complete the audit yourself", compact_skill)
        self.assertIn("perform the audit yourself", read("lean/AGENTS.md"))
        self.assertIn("allow_implicit_invocation: false", ui)
        self.assertIn("$lean-formalization", ui)


if __name__ == "__main__":
    unittest.main()
