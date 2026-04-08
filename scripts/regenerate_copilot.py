#!/usr/bin/env python3
"""Regenerate superpowers-copilot/ from superpowers/ with GitHub Copilot adaptations.

Run from the project root:
    python scripts/regenerate_copilot.py

Exits 0 on success, 1 if any replacement targets were not found (upstream content
may have changed — review COPILOT-ADAPTATION.md and update this script).
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src" / "agent_superpowers" / "superpowers"
DEST = PROJECT_ROOT / "src" / "agent_superpowers" / "superpowers-copilot"

_warnings = 0


def _warn(msg: str) -> None:
    global _warnings
    _warnings += 1
    print(f"  WARN {msg}")


def replace(path: Path, old: str, new: str, name: str) -> None:
    """Replace first occurrence of old with new in path."""
    content = path.read_text(encoding="utf-8")
    if old not in content:
        _warn(f"[{name}] text not found in {path.relative_to(PROJECT_ROOT)}")
        return
    path.write_text(content.replace(old, new, 1), encoding="utf-8")
    print(f"  ok   [{name}]")


def replace_from(path: Path, marker: str, new_tail: str, name: str) -> None:
    """Replace from marker to end of file with new_tail."""
    content = path.read_text(encoding="utf-8")
    idx = content.find(marker)
    if idx == -1:
        _warn(f"[{name}] marker not found in {path.relative_to(PROJECT_ROOT)}")
        return
    path.write_text(content[:idx] + new_tail, encoding="utf-8")
    print(f"  ok   [{name}]")


def insert_after(path: Path, marker: str, insertion: str, name: str) -> None:
    """Insert text immediately after the first occurrence of marker."""
    content = path.read_text(encoding="utf-8")
    idx = content.find(marker)
    if idx == -1:
        _warn(f"[{name}] marker not found in {path.relative_to(PROJECT_ROOT)}")
        return
    pos = idx + len(marker)
    path.write_text(content[:pos] + insertion + content[pos:], encoding="utf-8")
    print(f"  ok   [{name}]")


def prepend(path: Path, text: str, name: str) -> None:
    """Prepend text to the file."""
    content = path.read_text(encoding="utf-8")
    path.write_text(text + content, encoding="utf-8")
    print(f"  ok   [{name}]")


def main() -> int:
    if not SRC.is_dir():
        print(f"ERROR: source not found: {SRC}")
        return 1

    # ── Step 1: fresh copy ────────────────────────────────────────────────────
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SRC, DEST)
    print(f"Copied {SRC.name} → {DEST.name}  ({sum(1 for _ in DEST.rglob('*') if _.is_file())} files)")

    skills = DEST / "skills"

    # ── Step 2: global replacements across all SKILL.md files ─────────────────
    print("\nGlobal replacements...")
    for skill_md in sorted(skills.rglob("SKILL.md")):
        content = skill_md.read_text(encoding="utf-8")
        updated = (
            content
            .replace("your human partner", "the user")
            .replace("~/.claude/skills/", "src/agent_superpowers/superpowers-copilot/skills/")
        )
        if updated != content:
            skill_md.write_text(updated, encoding="utf-8")
    print("  ok   [global: 'your human partner' → 'the user']")
    print("  ok   [global: '~/.claude/skills/' → copilot path]")

    # ── Step 3: per-skill changes ─────────────────────────────────────────────

    # --- subagent-driven-development -----------------------------------------
    print("\nskills/subagent-driven-development/SKILL.md...")
    sdd = skills / "subagent-driven-development" / "SKILL.md"
    prepend(
        sdd,
        "> **GitHub Copilot:** This skill requires subagent dispatch, which Copilot does not support.\n"
        "> Use `executing-plans` instead for inline step-by-step execution within a single chat session.\n\n",
        "copilot banner",
    )

    # --- dispatching-parallel-agents -----------------------------------------
    print("\nskills/dispatching-parallel-agents/SKILL.md...")
    dpa = skills / "dispatching-parallel-agents" / "SKILL.md"
    prepend(
        dpa,
        "> **GitHub Copilot:** This skill requires parallel agent dispatch, which Copilot does not support.\n"
        "> For multiple independent problems, address them sequentially in a single chat session,\n"
        "> or open separate Copilot Chat conversations and handle each independently.\n\n",
        "copilot banner",
    )

    # --- using-superpowers ---------------------------------------------------
    print("\nskills/using-superpowers/SKILL.md...")
    us = skills / "using-superpowers" / "SKILL.md"
    replace(
        us,
        "**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.\n"
        "\n"
        "**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins. The `skill` tool works the same as Claude Code's `Skill` tool.\n"
        "\n"
        "**In Gemini CLI:** Skills activate via the `activate_skill` tool. Gemini loads skill metadata at session start and activates the full content on demand.\n"
        "\n"
        "**In other environments:** Check your platform's documentation for how skills are loaded.",
        "**In GitHub Copilot (VS Code):** Skills are markdown files in `src/agent_superpowers/superpowers-copilot/skills/`.\n"
        "Load a skill by referencing it in your chat message:\n"
        "\n"
        "```\n"
        "#file:src/agent_superpowers/superpowers-copilot/skills/brainstorming/SKILL.md\n"
        "```\n"
        "\n"
        "Or add skills to `.github/copilot-instructions.md` to load them automatically in every session.\n"
        "\n"
        "There is no `/skill-name` command — you must explicitly reference the file.",
        "how to access skills",
    )
    replace(
        us,
        "Skills use Claude Code tool names. Non-CC platforms: see `references/copilot-tools.md` (Copilot CLI), `references/codex-tools.md` (Codex) for tool equivalents. Gemini CLI users get the tool mapping loaded automatically via GEMINI.md.",
        "Skills were written for Claude Code. For GitHub Copilot: load skill files via `#file:` references instead of the `Skill` tool. See `references/copilot-tools.md` for the full tool mapping.",
        "platform adaptation",
    )

    # --- brainstorming -------------------------------------------------------
    print("\nskills/brainstorming/SKILL.md...")
    br = skills / "brainstorming" / "SKILL.md"
    replace(
        br,
        "You MUST create a task for each of these items and complete them in order:",
        "You MUST track progress through these items. Create a checklist file at `docs/superpowers/progress/brainstorm-<topic>.md` and tick off each item as you complete it.",
        "checklist instruction",
    )
    replace(
        br,
        "9. **Transition to implementation** — invoke writing-plans skill to create implementation plan",
        "9. **Transition to implementation** — load the writing-plans skill: `#file:src/agent_superpowers/superpowers-copilot/skills/writing-plans/SKILL.md`",
        "checklist step 9",
    )
    replace(
        br,
        "**The terminal state is invoking writing-plans.** Do NOT invoke frontend-design, mcp-builder, or any other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans.",
        "**The terminal state is loading writing-plans.** Load it as context and follow it. Do NOT start any implementation work directly. The ONLY next step after brainstorming is writing-plans.",
        "terminal state note",
    )
    replace_from(
        br,
        "## Visual Companion\n\nA browser-based companion",
        "## Visual Companion\n\n"
        "> **GitHub Copilot:** The visual companion (local web server with browser mockups) is not\n"
        "> supported. Use text-based descriptions, ASCII diagrams, or Mermaid diagrams in markdown\n"
        "> for visual communication during brainstorming.\n",
        "visual companion section",
    )

    # --- writing-plans -------------------------------------------------------
    print("\nskills/writing-plans/SKILL.md...")
    wp = skills / "writing-plans" / "SKILL.md"
    replace(
        wp,
        "**Context:** This should be run in a dedicated worktree (created by brainstorming skill).",
        "**Context:** Optionally set up a git worktree for isolation (see using-git-worktrees skill).",
        "context line",
    )
    replace(
        wp,
        "> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.",
        "> **For agentic workers:** REQUIRED: Load and follow `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.",
        "agentic header",
    )
    replace_from(
        wp,
        "## Execution Handoff\n",
        "## Execution Handoff\n\n"
        "After saving the plan, offer execution:\n\n"
        '**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`.\n\n'
        "To execute: load the executing-plans skill (`#file:src/agent_superpowers/superpowers-copilot/skills/executing-plans/SKILL.md`) and follow it step-by-step in this session.\"**\n",
        "execution handoff section",
    )

    # --- executing-plans -----------------------------------------------------
    print("\nskills/executing-plans/SKILL.md...")
    ep = skills / "executing-plans" / "SKILL.md"
    replace(
        ep,
        "**Note:** Tell the user that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers:subagent-driven-development instead of this skill.",
        "**Note:** This skill is the recommended execution path for GitHub Copilot. Execute all tasks inline in the current chat session, checking off steps as you complete them in a checklist file.",
        "note paragraph",
    )
    replace(
        ep,
        '- Announce: "I\'m using the finishing-a-development-branch skill to complete this work."\n'
        "- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch\n"
        "- Follow that skill to verify tests, present options, execute choice",
        "- Load and follow the finishing-a-development-branch skill:\n"
        "  `#file:src/agent_superpowers/superpowers-copilot/skills/finishing-a-development-branch/SKILL.md`\n"
        "- Follow that skill to verify tests, present options, execute choice",
        "step 3 finishing skill",
    )

    # --- finishing-a-development-branch --------------------------------------
    print("\nskills/finishing-a-development-branch/SKILL.md...")
    fab = skills / "finishing-a-development-branch" / "SKILL.md"
    insert_after(
        fab,
        "### Step 5: Cleanup Worktree",
        "\n\n> **GitHub Copilot / no worktrees:** If you are not using git worktrees, skip this step.\n"
        "> If you are using worktrees, run `git worktree remove <path>` in the terminal manually.",
        "worktrees skip note",
    )
    insert_after(
        fab,
        "gh pr create --title \"<title>\" --body \"$(cat <<'EOF'\n"
        "## Summary\n"
        "<2-3 bullets of what changed>\n"
        "\n"
        "## Test Plan\n"
        "- [ ] <verification steps>\n"
        "EOF\n"
        ")\"",
        "\n\n> **Windows:** Requires [GitHub CLI](https://cli.github.com/) installed and authenticated.\n"
        "> Run `gh auth login` once to set up.",
        "windows gh cli note",
    )

    # --- using-git-worktrees -------------------------------------------------
    print("\nskills/using-git-worktrees/SKILL.md...")
    ugw = skills / "using-git-worktrees" / "SKILL.md"
    replace(
        ugw,
        "grep -i \"worktree.*director\" CLAUDE.md 2>/dev/null",
        "grep -i \"worktree.*director\" .github/copilot-instructions.md 2>/dev/null\n"
        "# Or check README.md conventions section",
        "claude.md grep",
    )
    insert_after(
        ugw,
        "### 1. Detect Project Name",
        "\n\n> **Windows paths:** Git worktrees work on Windows with Git for Windows installed.\n"
        "> Use forward slashes in git commands (Git handles the translation).\n"
        "> For PowerShell, `$HOME` replaces `~`:\n"
        "> `git worktree add \"$HOME/.config/superpowers/worktrees/$project/$BRANCH_NAME\" -b $BRANCH_NAME`",
        "windows paths note",
    )

    # --- requesting-code-review ----------------------------------------------
    print("\nskills/requesting-code-review/SKILL.md...")
    rcr = skills / "requesting-code-review" / "SKILL.md"
    replace_from(
        rcr,
        "## How to Request\n",
        "## How to Request\n\n"
        "**1. Get git SHAs:**\n\n"
        "```bash\n"
        "git rev-parse HEAD~1   # base SHA\n"
        "git rev-parse HEAD     # head SHA\n"
        "```\n\n"
        "**2. Load the code reviewer persona and request inline review:**\n\n"
        "```\n"
        "#file:src/agent_superpowers/superpowers-copilot/agents/code-reviewer.md\n"
        "```\n\n"
        "Then ask:\n"
        "> \"Review the changes between `<BASE_SHA>` and `<HEAD_SHA>`.\n"
        "> What was implemented: `<WHAT_WAS_IMPLEMENTED>`\n"
        "> What it should do: `<PLAN_OR_REQUIREMENTS>`\"\n\n"
        "Or paste the diff directly:\n"
        "```bash\n"
        "git diff <BASE_SHA> <HEAD_SHA>\n"
        "# Copy output and paste into Copilot Chat as context\n"
        "```\n\n"
        "**3. Act on feedback:** Fix Critical issues immediately. Fix Important issues before proceeding. Note Minor issues for later.\n\n"
        "## Example\n",
        "how to request section",
    )

    # --- receiving-code-review -----------------------------------------------
    print("\nskills/receiving-code-review/SKILL.md...")
    recv = skills / "receiving-code-review" / "SKILL.md"
    insert_after(
        recv,
        "When replying to inline review comments on GitHub, reply in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.",
        "\n\n> **Windows:** The `gh` CLI commands work identically on Windows.\n"
        "> Install GitHub CLI from https://cli.github.com/ if not present.",
        "windows gh cli note",
    )

    # --- test-driven-development ---------------------------------------------
    print("\nskills/test-driven-development/SKILL.md...")
    tdd = skills / "test-driven-development" / "SKILL.md"
    replace(
        tdd,
        "```bash\nnpm test path/to/test.test.ts\n```\n\nConfirm:\n- Test fails (not errors)",
        "```bash\nnpm test path/to/test.test.ts\n# Windows: same command — works in PowerShell, cmd, or Git Bash\n```\n\nConfirm:\n- Test fails (not errors)",
        "verify red bash block",
    )
    replace(
        tdd,
        "```bash\nnpm test path/to/test.test.ts\n```\n\nConfirm:\n- Test passes",
        "```bash\nnpm test path/to/test.test.ts\n# Windows: same command — works in PowerShell, cmd, or Git Bash\n```\n\nConfirm:\n- Test passes",
        "verify green bash block",
    )
    # Append Windows note at end of file
    content = tdd.read_text(encoding="utf-8")
    tdd.write_text(
        content.rstrip() + "\n\n"
        "## Windows Note\n\n"
        "All test commands (`npm test`, `pytest`, `cargo test`, `go test ./...`) work on Windows\n"
        "with the appropriate runtimes installed. Use the same commands as shown throughout this skill.\n",
        encoding="utf-8",
    )
    print("  ok   [windows note appended]")

    # --- systematic-debugging ------------------------------------------------
    print("\nskills/systematic-debugging/SKILL.md...")
    sd = skills / "systematic-debugging" / "SKILL.md"
    insert_after(
        sd,
        "   # Layer 4: Actual signing\n"
        "   codesign --sign \"$IDENTITY\" --verbose=4 \"$APP\"\n"
        "   ```",
        "\n\n   **Windows PowerShell equivalents:**\n"
        "   ```powershell\n"
        "   # Check environment variables\n"
        "   if ($env:IDENTITY) { \"IDENTITY: SET\" } else { \"IDENTITY: UNSET\" }\n"
        "   Get-ChildItem Env: | Where-Object Name -like \"IDENTITY*\"\n"
        "   ```",
        "powershell equivalents",
    )

    # --- writing-skills ------------------------------------------------------
    print("\nskills/writing-skills/SKILL.md...")
    ws = skills / "writing-skills" / "SKILL.md"
    replace(
        ws,
        "**Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code, `~/.agents/skills/` for Codex)** ",
        "**Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code).\n"
        "For GitHub Copilot, keep skills in this repository at `src/agent_superpowers/superpowers-copilot/skills/`\n"
        "and load them via `#file:` references or add them to `.github/copilot-instructions.md`.** ",
        "personal skills path",
    )
    replace(
        ws,
        "**IMPORTANT: Use TodoWrite to create todos for EACH checklist item below.**",
        "**IMPORTANT: Create a checklist markdown file to track EACH checklist item below.**",
        "todowrite checklist",
    )
    replace(
        ws,
        "### RED: Write Failing Test (Baseline)\n\nRun pressure scenario with subagent WITHOUT the skill. Document exact behavior:\n- What choices did they make?\n- What rationalizations did they use (verbatim)?\n- Which pressures triggered violations?\n\nThis is \"watch the test fail\" - you must see what agents naturally do before writing the skill.",
        "### RED: Write Failing Test (Baseline)\n\nRun a test conversation in Copilot Chat WITHOUT the skill loaded as context. Describe the\nscenario you want to handle and observe how Copilot responds naturally.\nDocument exact behaviors and rationalizations.",
        "red phase",
    )
    replace(
        ws,
        "### GREEN: Write Minimal Skill\n\nWrite skill that addresses those specific rationalizations. Don't add extra content for hypothetical cases.\n\nRun same scenarios WITH skill. Agent should now comply.",
        "### GREEN: Write Minimal Skill\n\nWrite the skill addressing specific failures from baseline. Add the skill file, then\nreference it in a new Copilot conversation via `#file:` and run the same scenario.\nVerify the behavior improves.",
        "green phase",
    )
    replace(
        ws,
        "**Testing methodology:** See @testing-skills-with-subagents.md for the complete testing methodology:",
        "**Testing in Copilot:** Since subagents aren't available, test by opening fresh Copilot\n"
        "Chat conversations (clears session context) with the skill file as `#file:` context.\n"
        "Run pressure scenarios and evaluate the responses.\n\n"
        "**Testing methodology:** See `#file:src/agent_superpowers/superpowers-copilot/skills/writing-skills/testing-skills-with-subagents.md` for general testing patterns:",
        "testing methodology",
    )

    # ── Step 4: create copilot-instructions template ──────────────────────────
    print("\nCreating copilot-instructions-template.md...")
    template = DEST / "copilot-instructions-template.md"
    template.write_text(
        "# Copilot Instructions — Superpowers\n\n"
        "You have access to a library of workflow skills.\n\n"
        "## Available Skills\n\n"
        "Skills are in `src/agent_superpowers/superpowers-copilot/skills/`. Load any skill with:\n"
        "`#file:src/agent_superpowers/superpowers-copilot/skills/<skill-name>/SKILL.md`\n\n"
        "## When to Use Which Skill\n\n"
        "- **New feature or component** → load `brainstorming/SKILL.md` first\n"
        "- **Have a spec, ready to plan** → load `writing-plans/SKILL.md`\n"
        "- **Have a plan, ready to implement** → load `executing-plans/SKILL.md`\n"
        "- **Bug or unexpected behavior** → load `systematic-debugging/SKILL.md`\n"
        "- **About to write code** → load `test-driven-development/SKILL.md`\n"
        "- **About to claim work is done** → load `verification-before-completion/SKILL.md`\n"
        "- **Received code review feedback** → load `receiving-code-review/SKILL.md`\n\n"
        "## Rule\n\n"
        "If there is even a 1% chance a skill applies to what you are doing, load and follow it.\n",
        encoding="utf-8",
    )
    print("  ok   [copilot-instructions-template.md]")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─' * 50}")
    if _warnings:
        print(f"Completed with {_warnings} warning(s) — review output above.")
        return 1
    print("Completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
