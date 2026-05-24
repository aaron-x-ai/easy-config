from pathlib import Path

import pytest

from easy_config.schema_pipeline import parse_skill_target


def test_parse_demo_skill(demo_skill_dir: Path) -> None:
    target = parse_skill_target("demo-skill")
    assert target.root == demo_skill_dir.resolve()
    assert target.config_format == "yaml"
    assert target.write_target.name == "config.yaml"


def test_schema_not_found(skills_root: Path) -> None:
    (skills_root / "empty-skill").mkdir()
    with pytest.raises(Exception) as exc:
        parse_skill_target("empty-skill")
    assert "schema" in str(exc.value).lower()
