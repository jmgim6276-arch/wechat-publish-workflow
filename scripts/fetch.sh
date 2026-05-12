#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${HOME}/.wechat-venv"
cd "$ROOT"
"$VENV/bin/python3" toolkit/fetch_draft.py "$@"
