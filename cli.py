"""CLI and slash commands share the same validated arguments."""
from __future__ import annotations

import argparse
import asyncio
import shlex

from .runner import run, run_result, format_result

_ACTIONS = ("status", "harvest", "dry-run", "run", "adopt")


def _positive(value):
    number = int(value)
    if not 1 <= number <= 1000:
        raise argparse.ArgumentTypeError("Expected an integer between 1 and 1000.")
    return number


def register_cli(subparser):
    subs = subparser.add_subparsers(dest="skillopt_sleep_action")
    for action in _ACTIONS:
        parser = subs.add_parser(action)
        parser.add_argument("--project", default="", help="existing project directory (default: cwd)")
        parser.add_argument("--backend", default="mock", choices=("mock", "codex", "claude", "copilot"))
        parser.add_argument("--model", default="")
        parser.add_argument("--target-skill-path", default="")
        parser.add_argument("--max-sessions", type=_positive, default=120)
        parser.add_argument("--max-tasks", type=_positive, default=40)
        parser.add_argument("--lookback-hours", type=_positive, default=72)
        parser.add_argument("--edit-budget", type=_positive, default=4)
        parser.add_argument("--progress", action="store_true")
        parser.add_argument("--json", action="store_true")
    subparser.set_defaults(func=skillopt_sleep_command)


def skillopt_sleep_command(args_or_text):
    if not isinstance(args_or_text, str):
        # Bare CLI invocation uses the same status defaults as the slash form.
        if getattr(args_or_text, "skillopt_sleep_action", None):
            return run(args_or_text)
        parser = argparse.ArgumentParser(prog="skillopt-sleep")
        register_cli(parser)
        return run(parser.parse_args(["status"]))
    raise TypeError("Use the async slash handler for in-session commands.")


class _SlashParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


async def skillopt_sleep_slash(text):
    try:
        argv = shlex.split(text)
        if not argv or argv[0].startswith("-"):
            argv.insert(0, "status")
        parser = _SlashParser(prog="skillopt-sleep")
        register_cli(parser)
        if "--help" in argv or "-h" in argv:
            return parser.format_help()
        args = parser.parse_args(argv)
    except ValueError:
        return "Invalid SkillOpt command arguments. Use /skillopt-sleep --help."
    _, payload = await asyncio.to_thread(run_result, args)
    return format_result(payload, pretty=True)
