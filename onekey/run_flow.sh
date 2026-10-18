#!/usr/bin/env bash
# Re-run only the flow (toolchain already installed).
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh" --flow-only "$@"
