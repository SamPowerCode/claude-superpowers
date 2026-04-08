import shutil
from pathlib import Path


class SkillConflictError(Exception):
    """Raised when a skill already exists at the target and force/skip_existing not set."""


def get_superpowers_dir() -> Path:
    """Return the path to the bundled obra/superpowers repository content."""
    return Path(__file__).parent / "superpowers"


def get_copilot_superpowers_dir() -> Path:
    """Return the path to the GitHub Copilot-adapted superpowers content."""
    return Path(__file__).parent / "superpowers-copilot"


def get_skills_dir() -> Path:
    """Return the path to the original (Claude Code) skills directory."""
    return get_superpowers_dir() / "skills"


def get_copilot_skills_dir() -> Path:
    """Return the path to the GitHub Copilot-adapted skills directory."""
    return get_copilot_superpowers_dir() / "skills"


def install_skills(
    target: Path,
    force: bool = False,
    skip_existing: bool = False,
    copilot: bool = False,
) -> list:
    """Copy all bundled skills to target directory.

    Args:
        target: Destination directory (will be created if missing).
        force: Overwrite existing skills without prompting.
        skip_existing: Leave existing skills untouched.
        copilot: If True, install the GitHub Copilot-adapted skills instead of the originals.

    Returns:
        List of installed skill names.

    Raises:
        SkillConflictError: If a skill exists and neither force nor skip_existing is set.
    """
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)

    skills_dir = get_copilot_skills_dir() if copilot else get_skills_dir()
    installed = []

    for skill_src in sorted(skills_dir.iterdir()):
        if not skill_src.is_dir():
            continue

        skill_dest = target / skill_src.name

        if skill_dest.exists():
            if skip_existing:
                continue
            if not force:
                raise SkillConflictError(
                    f"Skill '{skill_src.name}' already exists at {skill_dest}. "
                    "Use force=True to overwrite or skip_existing=True to keep existing."
                )
            shutil.rmtree(skill_dest)

        shutil.copytree(skill_src, skill_dest)
        installed.append(skill_src.name)

    return installed
