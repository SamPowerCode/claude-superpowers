from unittest.mock import patch

import pytest

from agent_superpowers.cli import main, list_skills, parse_args


# --- parse_args ---

def test_parse_args_install_is_default_command():
    args = parse_args(["install"])
    assert args.command == "install"


def test_parse_args_list_command():
    args = parse_args(["list"])
    assert args.command == "list"


def test_parse_args_force_flag():
    args = parse_args(["install", "--force"])
    assert args.force is True


def test_parse_args_skip_existing_flag():
    args = parse_args(["install", "--skip-existing"])
    assert args.skip_existing is True


def test_parse_args_version_flag(capsys):
    with pytest.raises(SystemExit):
        parse_args(["--version"])
    captured = capsys.readouterr()
    assert "5.0.6" in captured.out or "5.0.6" in captured.err


# --- list_skills ---

def test_list_skills_outputs_skill_names(capsys):
    list_skills()
    captured = capsys.readouterr()
    assert "brainstorming" in captured.out
    assert "test-driven-development" in captured.out


def test_list_skills_outputs_descriptions(capsys):
    list_skills()
    captured = capsys.readouterr()
    # Every SKILL.md has a description in frontmatter — at least one should appear
    assert len(captured.out.strip()) > 0


# --- main: install command with mocked prompt ---

def test_main_install_project_github_copilot(tmp_path):
    """Choice 1: .github/skills/ in current directory."""
    with patch("agent_superpowers.cli.prompt_choice", return_value=1), \
         patch("agent_superpowers.cli.get_project_root", return_value=tmp_path):
        main(["install"])
    assert (tmp_path / ".github" / "skills").is_dir()


def test_main_install_project_claude_code(tmp_path):
    """Choice 2: .claude/skills/ in current directory."""
    with patch("agent_superpowers.cli.prompt_choice", return_value=2), \
         patch("agent_superpowers.cli.get_project_root", return_value=tmp_path):
        main(["install"])
    assert (tmp_path / ".claude" / "skills").is_dir()


def test_main_install_global_copilot(tmp_path):
    """Choice 3: ~/.copilot/skills/"""
    fake_home = tmp_path / "home"
    with patch("agent_superpowers.cli.prompt_choice", return_value=3), \
         patch("agent_superpowers.cli.Path.home", return_value=fake_home):
        main(["install"])
    assert (fake_home / ".copilot" / "skills").is_dir()


def test_main_install_global_claude_code(tmp_path):
    """Choice 4: ~/.claude/skills/"""
    fake_home = tmp_path / "home"
    with patch("agent_superpowers.cli.prompt_choice", return_value=4), \
         patch("agent_superpowers.cli.Path.home", return_value=fake_home):
        main(["install"])
    assert (fake_home / ".claude" / "skills").is_dir()


def test_main_install_prints_summary(tmp_path, capsys):
    with patch("agent_superpowers.cli.prompt_choice", return_value=1), \
         patch("agent_superpowers.cli.get_project_root", return_value=tmp_path):
        main(["install"])
    captured = capsys.readouterr()
    assert "Installed" in captured.out
    assert "skills" in captured.out


def test_main_list_calls_list_skills(capsys):
    main(["list"])
    captured = capsys.readouterr()
    assert "brainstorming" in captured.out
