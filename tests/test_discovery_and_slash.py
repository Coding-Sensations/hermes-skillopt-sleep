"""Production discovery, nested workspace, and concurrent slash contracts."""
import asyncio
import json
import subprocess
import threading
from pathlib import Path

from hermes_plugins.skillopt_sleep import cli
from hermes_plugins.skillopt_sleep.configuration import configuration
from hermes_plugins.skillopt_sleep.hermes_source import harvest_hermes
from hermes_state import SessionDB


def test_nested_project_harvest_and_lock_leave_checkout_unchanged(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    nested = root / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    db = SessionDB(db_path=home / "state.db")
    db.create_session("nested-source", "cli", cwd=str(nested), git_repo_root=str(root))
    db.append_message("nested-source", "user", "Inspect parser behavior")
    db.append_message("nested-source", "assistant", "Parser behavior inspected")
    db.close()
    assert harvest_hermes(project=str(nested))[0].session_id == "nested-source"
    parser = cli.argparse.ArgumentParser()
    cli.register_cli(parser)
    args = parser.parse_args(["run", "--json"])
    cfg = configuration(args)
    assert cfg.invoked_project == str(root)
    from hermes_plugins.skillopt_sleep import runner
    monkeypatch.setattr(runner, "_execute", lambda args, cfg: {"status": "tested"})
    before = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"])
    assert runner.run_result(args)[0] == 0
    assert (Path(cfg.state_dir) / "hermes.lock").exists()
    assert subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]) == before


def test_slash_work_yields_event_loop_and_returns_only_its_payload(monkeypatch):
    entered = threading.Event()
    release = threading.Event()

    def work(args):
        entered.set()
        assert release.wait(5)
        print("unrelated worker output")
        return 0, {"status": "own result"}

    monkeypatch.setattr(cli, "run_result", work)

    async def scenario():
        task = asyncio.create_task(cli.skillopt_sleep_slash("harvest"))
        try:
            for _ in range(100):
                if entered.is_set():
                    break
                await asyncio.sleep(0.01)
            assert entered.is_set()
            assert not task.done()
        finally:
            release.set()
        result = await task
        assert json.loads(result) == {"status": "own result"}
        assert "unrelated worker output" not in result

    asyncio.run(scenario())
