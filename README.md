# agent-superpowers

Install the [obra/superpowers](https://github.com/obra/superpowers) agentic skills framework directly into your project or user profile — no GitHub access or manual cloning required.

Superpowers provides a set of skills (brainstorming, TDD, systematic debugging, code review, and more) that guide AI coding assistants through structured development workflows. Skills follow the open [agentskills.io](https://agentskills.io) standard and work with **GitHub Copilot** (VS Code, PyCharm) and **Claude Code**.

## Installation

```bash
# pip
pip install agent-superpowers

# uv — install as a persistent tool
uv tool install agent-superpowers

# uvx — run once without installing
uvx agent-superpowers install
```

## Usage

### Install skills

```bash
agent-superpowers install
```

You'll be prompted to choose where to install:

```
Where would you like to install the Superpowers skills?

  1. This project (GitHub Copilot)  →  .github/skills/   [Copilot-adapted]
  2. This project (Claude Code)     →  .claude/skills/   [original]
  3. GitHub Copilot (global)        →  ~/.copilot/skills/ [Copilot-adapted]
  4. Claude Code (global)           →  ~/.claude/skills/  [original]
```

Copilot targets (1 and 3) install a version of the skills adapted for GitHub Copilot on Windows — subagent references removed, `#file:` loading patterns added, PowerShell equivalents included. Claude Code targets (2 and 4) install the original upstream skills unchanged.

**Options:**

| Flag | Effect |
|---|---|
| `--force` | Overwrite existing skills without prompting |
| `--skip-existing` | Leave existing skills untouched |

### List bundled skills

```bash
agent-superpowers list             # original skills
agent-superpowers list --copilot   # Copilot-adapted skills
```

### Check version

```bash
agent-superpowers --version
```

## What gets installed

14 skills from the [obra/superpowers](https://github.com/obra/superpowers) framework (v5.0.6):

| Skill | When to use |
|---|---|
| `brainstorming` | Before any new feature or creative work |
| `test-driven-development` | When implementing features or fixing bugs |
| `systematic-debugging` | When encountering bugs or unexpected behavior |
| `writing-plans` | When planning multi-step tasks |
| `executing-plans` | When executing a written plan |
| `subagent-driven-development` | For parallel independent implementation tasks |
| `requesting-code-review` | Before merging work |
| `receiving-code-review` | When responding to review feedback |
| `dispatching-parallel-agents` | When facing 2+ independent tasks |
| `verification-before-completion` | Before claiming work is done |
| `finishing-a-development-branch` | When implementation is complete |
| `using-git-worktrees` | For isolated feature branches |
| `writing-skills` | When creating new skills |
| `using-superpowers` | Session initialization |

### GitHub Copilot adaptation

The package also includes a full copy of the obra/superpowers repository content (`CLAUDE.md`, `GEMINI.md`, `commands/`, `agents/`, `hooks/`, platform plugins, etc.) alongside the Copilot-adapted skills.

For GitHub Copilot users, a `copilot-instructions-template.md` is included — copy its contents into your project's `.github/copilot-instructions.md` to auto-load skill awareness into every Copilot Chat session.

See `COPILOT-ADAPTATION.md` in this repo for the full specification of what was changed and why.

## Credits

Skills are from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent, licensed MIT.

The skill format follows the open standard at [agentskills.io](https://agentskills.io).
