import pytest

from agent_superpowers.installer import get_superpowers_dir, get_skills_dir, install_skills, SkillConflictError


def test_get_superpowers_dir_returns_existing_path():
    superpowers_dir = get_superpowers_dir()
    assert superpowers_dir.is_dir(), f"Expected superpowers dir to exist: {superpowers_dir}"


def test_get_superpowers_dir_contains_full_repo_content():
    superpowers_dir = get_superpowers_dir()
    assert (superpowers_dir / "CLAUDE.md").exists()
    assert (superpowers_dir / "GEMINI.md").exists()
    assert (superpowers_dir / "skills").is_dir()
    assert (superpowers_dir / "commands").is_dir()
    assert (superpowers_dir / "hooks").is_dir()
    assert (superpowers_dir / "agents").is_dir()


def test_get_skills_dir_returns_existing_path():
    skills_dir = get_skills_dir()
    assert skills_dir.is_dir(), f"Expected skills dir to exist: {skills_dir}"


def test_get_skills_dir_contains_skill_md_files():
    skills_dir = get_skills_dir()
    skill_mds = list(skills_dir.rglob("SKILL.md"))
    assert len(skill_mds) >= 14, f"Expected at least 14 SKILL.md files, found {len(skill_mds)}"


def test_install_skills_copies_all_skill_dirs(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    installed = [p for p in target.iterdir() if p.is_dir()]
    assert len(installed) >= 14


def test_install_skills_creates_target_dir_if_missing(tmp_path):
    target = tmp_path / "nested" / "skills"
    assert not target.exists()
    install_skills(target)
    assert target.is_dir()


def test_install_skills_each_skill_has_skill_md(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    for skill_dir in target.iterdir():
        if skill_dir.is_dir():
            assert (skill_dir / "SKILL.md").exists(), f"Missing SKILL.md in {skill_dir.name}"


def test_install_skills_raises_on_conflict_without_force(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    with pytest.raises(SkillConflictError):
        install_skills(target)


def test_install_skills_overwrites_with_force(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    # Corrupt one skill file
    skill_dir = next(target.iterdir())
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("corrupted")
    install_skills(target, force=True)
    assert skill_md.read_text() != "corrupted"


def test_install_skills_skips_existing_with_skip_existing(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    skill_dir = next(target.iterdir())
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("preserved")
    install_skills(target, skip_existing=True)
    assert skill_md.read_text() == "preserved"


def test_install_skills_returns_list_of_installed_skill_names(tmp_path):
    target = tmp_path / "skills"
    installed = install_skills(target)
    assert isinstance(installed, list)
    assert "brainstorming" in installed
    assert "test-driven-development" in installed
