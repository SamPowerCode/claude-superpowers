import pytest

from agent_superpowers.installer import (
    get_superpowers_dir,
    get_copilot_superpowers_dir,
    get_skills_dir,
    get_copilot_skills_dir,
    install_skills,
    SkillConflictError,
)


# --- directory accessors ---

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


def test_get_copilot_superpowers_dir_returns_existing_path():
    copilot_dir = get_copilot_superpowers_dir()
    assert copilot_dir.is_dir(), f"Expected copilot superpowers dir to exist: {copilot_dir}"


def test_get_copilot_superpowers_dir_contains_expected_content():
    copilot_dir = get_copilot_superpowers_dir()
    assert (copilot_dir / "skills").is_dir()
    assert (copilot_dir / "agents").is_dir()
    assert (copilot_dir / "copilot-instructions-template.md").exists()


def test_get_skills_dir_returns_existing_path():
    skills_dir = get_skills_dir()
    assert skills_dir.is_dir(), f"Expected skills dir to exist: {skills_dir}"


def test_get_skills_dir_contains_skill_md_files():
    skills_dir = get_skills_dir()
    skill_mds = list(skills_dir.rglob("SKILL.md"))
    assert len(skill_mds) >= 14, f"Expected at least 14 SKILL.md files, found {len(skill_mds)}"


def test_get_copilot_skills_dir_returns_existing_path():
    skills_dir = get_copilot_skills_dir()
    assert skills_dir.is_dir(), f"Expected copilot skills dir to exist: {skills_dir}"


def test_get_copilot_skills_dir_contains_skill_md_files():
    skills_dir = get_copilot_skills_dir()
    skill_mds = list(skills_dir.rglob("SKILL.md"))
    assert len(skill_mds) >= 14, f"Expected at least 14 SKILL.md files, found {len(skill_mds)}"


def test_copilot_skills_contain_copilot_adaptations():
    skills_dir = get_copilot_skills_dir()
    # subagent-driven-development should have the Copilot warning banner
    sdd = (skills_dir / "subagent-driven-development" / "SKILL.md").read_text()
    assert "GitHub Copilot" in sdd
    # using-superpowers should reference #file: instead of Skill tool
    using = (skills_dir / "using-superpowers" / "SKILL.md").read_text()
    assert "#file:" in using
    # brainstorming should not contain the visual companion server instructions
    brainstorm = (skills_dir / "brainstorming" / "SKILL.md").read_text()
    assert "start-server.sh" not in brainstorm


def test_original_skills_are_unchanged():
    skills_dir = get_skills_dir()
    # Original subagent-driven-development should NOT have the Copilot warning
    sdd = (skills_dir / "subagent-driven-development" / "SKILL.md").read_text()
    assert "GitHub Copilot:" not in sdd
    # Original using-superpowers should reference the Skill tool
    using = (skills_dir / "using-superpowers" / "SKILL.md").read_text()
    assert "Skill" in using


# --- install_skills ---

def test_install_skills_copies_all_skill_dirs(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    installed = [p for p in target.iterdir() if p.is_dir()]
    assert len(installed) >= 14


def test_install_skills_copilot_flag_uses_adapted_skills(tmp_path):
    target = tmp_path / "skills"
    install_skills(target, copilot=True)
    sdd = (target / "subagent-driven-development" / "SKILL.md").read_text()
    assert "GitHub Copilot" in sdd


def test_install_skills_default_uses_original_skills(tmp_path):
    target = tmp_path / "skills"
    install_skills(target)
    sdd = (target / "subagent-driven-development" / "SKILL.md").read_text()
    assert "GitHub Copilot:" not in sdd


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
