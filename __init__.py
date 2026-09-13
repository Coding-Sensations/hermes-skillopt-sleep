"""Opt-in SkillOpt-Sleep integration for Hermes."""

from __future__ import annotations

from pathlib import Path

from .cli import register_cli, skillopt_sleep_command, skillopt_sleep_slash


def register(ctx) -> None:
    ctx.register_skill("workflow", Path(__file__).parent / "skills/skillopt-sleep/SKILL.md",
                       description="Inspect session-derived tasks and staged proposals.")
    ctx.register_cli_command(
        name="skillopt-sleep",
        help="Run validation-gated SkillOpt self-improvement",
        setup_fn=register_cli,
        handler_fn=skillopt_sleep_command,
        description=(
            "Harvest Hermes sessions, replay recurring tasks, and stage bounded "
            "skill edits behind a held-out validation gate."
        ),
    )
    ctx.register_command(
        "skillopt-sleep",
        skillopt_sleep_slash,
        description="Run or inspect the validation-gated SkillOpt sleep cycle.",
        args_hint="[status|harvest|dry-run|run|adopt]",
    )
