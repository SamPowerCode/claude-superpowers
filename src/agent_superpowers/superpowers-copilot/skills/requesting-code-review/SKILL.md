---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch superpowers:code-reviewer subagent to catch issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history. This keeps the reviewer focused on the work product, not your thought process, and preserves your own context for continued work.

**Core principle:** Review early, review often.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**

```bash
git rev-parse HEAD~1   # base SHA
git rev-parse HEAD     # head SHA
```

**2. Load the code reviewer persona and request inline review:**

```
#file:src/agent_superpowers/superpowers-copilot/agents/code-reviewer.md
```

Then ask:
> "Review the changes between `<BASE_SHA>` and `<HEAD_SHA>`.
> What was implemented: `<WHAT_WAS_IMPLEMENTED>`
> What it should do: `<PLAN_OR_REQUIREMENTS>`"

Or paste the diff directly:
```bash
git diff <BASE_SHA> <HEAD_SHA>
# Copy output and paste into Copilot Chat as context
```

**3. Act on feedback:** Fix Critical issues immediately. Fix Important issues before proceeding. Note Minor issues for later.

## Example
