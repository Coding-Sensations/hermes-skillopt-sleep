#!/usr/bin/env bash
set -euo pipefail
: "${HERMES_SOURCE:?Set HERMES_SOURCE to a tested Hermes checkout}"
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$HERMES_SOURCE${PYTHONPATH:+:$PYTHONPATH}"
export HERMES_PYTHON="${HERMES_PYTHON:-$PLUGIN_ROOT/.venv/bin/python}"
exec "$HERMES_SOURCE/scripts/run_tests.sh" "$PLUGIN_ROOT/tests/plugins/test_skillopt_sleep_plugin.py" "$PLUGIN_ROOT/tests/plugins/test_skillopt_sleep_source.py" "$PLUGIN_ROOT/tests/test_discovery_and_slash.py" --import-mode=importlib "$@"
