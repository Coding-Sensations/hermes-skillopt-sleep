"""Load the standalone plugin through Hermes production discovery."""
import shutil
import tempfile
from pathlib import Path

import pytest


def pytest_sessionstart(session):
    from hermes_cli.plugins import PluginManager

    temporary = tempfile.TemporaryDirectory(prefix="skillopt-discovery-")
    home = Path(temporary.name)
    plugin = home / "plugins" / "skillopt-sleep"
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root, plugin, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"))
    (home / "config.yaml").write_text("plugins:\n  enabled: [skillopt-sleep]\n", encoding="utf-8")
    manager = PluginManager(scope_key=str(home))
    manager.discover_and_load()
    loaded = manager._plugins["skillopt-sleep"]
    assert loaded.enabled and not loaded.error, loaded.error
    assert "skillopt-sleep" in manager._cli_commands
    assert "skillopt-sleep" in manager._plugin_commands
    session.skillopt_discovery = (temporary, manager)


def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, "skillopt_discovery"):
        temporary, manager = session.skillopt_discovery
        manager.unload()
        temporary.cleanup()


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
