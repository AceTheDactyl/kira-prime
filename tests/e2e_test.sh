#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${PRIME_CLI:-}" ]]; then
  # shellcheck disable=SC2206
  CLI_ARR=(${PRIME_CLI})
else
  CLI_ARR=(node "$REPO_ROOT/tools/codex-cli/bin/codex.js")
fi

run_cli() {
  "${CLI_ARR[@]}" "$@"
}

note() {
  printf '%s\n' "$@"
}

note "🧪 End-to-End Integration Test"

note "1️⃣ Testing semantic memory..."
run_cli "limnus" "cache" "I love programming"
run_cli "limnus" "cache" "Coding is my passion"
run_cli "limnus" "cache" "The weather is nice"
run_cli "limnus" "recall" "software"
note "✅ Semantic recall command executed"

note "2️⃣ Testing git automation..."
run_cli "kira" "push"
note "✅ Git push dry-run executed"

note "3️⃣ Testing validation..."
run_cli "kira" "validate"
note "✅ Validation command executed"

note ""
note "✅ End-to-End test commands completed!"
