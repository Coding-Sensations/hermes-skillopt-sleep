# SkillOpt-Sleep for Hermes

Opt-in native plugin integrating the pinned `skillopt==0.2.0` Python package.
Clone https://github.com/mrkillbob/hermes-skillopt-sleep under the active profile's `plugins/skillopt-sleep`,
install `requirements.txt` in the Python environment shown by
`hermes --version-local`, then enable it:

```sh
hermes plugins enable skillopt-sleep --no-allow-tool-override
hermes skillopt-sleep status --project /path/to/project --json
hermes skillopt-sleep dry-run --project /path/to/project --json
```

The CLI and `/skillopt-sleep` slash command share the same arguments. No core
tools are added. The registered `skillopt-sleep:workflow` skill contains the full workflow.

## Current capability

- Read-only, project-filtered Hermes SQLite harvesting, with forced redaction.
- Real SkillOpt mining and mock replay, profile/project/target-scoped state,
  bounded task/session budgets, and separately staged proposals.
- Explicit adoption with finite improvement scores, candidate and target hashes,
  a shared target lock, backups, and next-session activation.
- Mock proposals are never eligible for adoption.

Live upstream CLI backends are deliberately unavailable in this integration.
SkillOpt 0.2.0's full-cycle API cannot accept a backend instance; its thread pools
also do not propagate Hermes's protected execution context. A live adapter must
preserve that context and distinguish text replay from real tool verification.
The current mock diagnostic does not establish self-improvement or CI evidence.
Automatic adoption and upstream cron scheduling are not exposed.

## Development

Tested against Hermes commit `ce73e3c5b95413cede9bc47687926527b966e303`.
Create a virtual environment, install that Hermes checkout with its dev dependencies,
and install this repository's `requirements.txt` in the same environment. Then run:

```sh
HERMES_SOURCE=/path/to/hermes-agent HERMES_PYTHON=/path/to/venv/bin/python scripts/run_tests.sh
```

The wrapper uses Hermes's isolated test runner. Tests require the real pinned engine;
missing dependencies fail discovery instead of skipping the suite. Tests load the
installed plugin through `PluginManager`, use temporary profiles and real SQLite
stores, and exercise the engine without network calls. Adoption fixtures use synthetic
evaluation receipts and do not qualify a live provider.

Repository locks and diagnostic state live under the active profile's
`plugin-data/skillopt-sleep`, leaving the project checkout untouched. Nested project
paths resolve to the Git root. Slash work runs off the event loop and returns its own
structured result without capturing process-wide output.

Extracted from `mrkillbob/hermes-agent#43`, preserving the original contribution
commit and authorship. Upstream engine: https://github.com/microsoft/SkillOpt
