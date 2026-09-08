#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
infra_root="${project_root}/infra"
bicep_bin="${BICEP_BIN:-bicep}"

if ! command -v "${bicep_bin}" >/dev/null 2>&1 && [[ ! -x "${bicep_bin}" ]]; then
  echo "ERROR: Bicep CLI not found. Set BICEP_BIN or install bicep." >&2
  exit 1
fi

"${bicep_bin}" --version
"${bicep_bin}" lint "${infra_root}/main.bicep" --no-restore
"${bicep_bin}" build "${infra_root}/main.bicep" --no-restore --stdout >/dev/null
"${bicep_bin}" build-params \
  "${infra_root}/environments/dev.bicepparam" \
  --no-restore \
  --stdout >/dev/null

echo "PASSED: Bicep lint, template build, and dev parameter build"
