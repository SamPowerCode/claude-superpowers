import argparse
import sys
from pathlib import Path

from agent_superpowers import __version__
from agent_superpowers.installer import (
    get_skills_dir,
    get_copilot_skills_dir,
    install_skills,
    SkillConflictError,
)


def get_project_root() -> Path:
    """Return the current working directory (project root)."""
    return Path.cwd()


def prompt_choice() -> int:
    """Display install location menu and return user's choice (1-4)."""
    print()
    print("Where would you like to install the Superpowers skills?")
    print()
    print("  1. This project (GitHub Copilot)  →  .github/skills/   [Copilot-adapted]")
    print("  2. This project (Claude Code)     →  .claude/skills/   [original]")
    print("  3. GitHub Copilot (global)        →  ~/.copilot/skills/ [Copilot-adapted]")
    print("  4. Claude Code (global)           →  ~/.claude/skills/  [original]")
    print()
    while True:
        raw = input("Enter choice [1/2/3/4]: ").strip()
        if raw in ("1", "2", "3", "4"):
            return int(raw)
        print("Please enter 1, 2, 3, or 4.")


def _target_for_choice(choice: int) -> Path:
    if choice == 1:
        return get_project_root() / ".github" / "skills"
    if choice == 2:
        return get_project_root() / ".claude" / "skills"
    if choice == 3:
        return Path.home() / ".copilot" / "skills"
    if choice == 4:
        return Path.home() / ".claude" / "skills"
    raise ValueError(f"Invalid choice: {choice}")


def _is_copilot_choice(choice: int) -> bool:
    return choice in (1, 3)


def list_skills(copilot: bool = False) -> None:
    """Print each bundled skill's name and description."""
    skills_dir = get_copilot_skills_dir() if copilot else get_skills_dir()
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        description = ""
        if skill_md.exists():
            description = _parse_description(skill_md.read_text())
        print(f"  {skill_dir.name}")
        if description:
            print(f"    {description}")


def _parse_description(content: str) -> str:
    """Extract the description field from SKILL.md YAML frontmatter."""
    lines = content.splitlines()
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter and line.startswith("description:"):
            return line[len("description:"):].strip()
    return ""


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agent-superpowers",
        description="Install obra/superpowers agentic skills for GitHub Copilot and Claude Code.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Install skills")
    install_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing skills without prompting"
    )
    install_parser.add_argument(
        "--skip-existing", action="store_true", help="Skip skills that already exist"
    )

    list_parser = subparsers.add_parser("list", help="List bundled skills")
    list_parser.add_argument(
        "--copilot", action="store_true", help="List the Copilot-adapted skills"
    )

    return parser.parse_args(argv)


def main(argv: list = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    if args.command == "list":
        list_skills(copilot=getattr(args, "copilot", False))
        return

    if args.command == "install" or args.command is None:
        choice = prompt_choice()
        target = _target_for_choice(choice)
        copilot = _is_copilot_choice(choice)

        force = getattr(args, "force", False)
        skip_existing = getattr(args, "skip_existing", False)

        installed = install_skills(target, force=force, skip_existing=skip_existing, copilot=copilot)
        count = len(installed)
        variant = "Copilot-adapted" if copilot else "original"
        print(f"\nInstalled {count} {variant} skill{'s' if count != 1 else ''} to {target}")
