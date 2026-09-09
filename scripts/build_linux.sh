#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname -- "$SCRIPT_DIR")"
BUILD_PYTHON="$PROJECT_DIR/.venv-build/bin/python"
OUTPUT_DIR="$HOME/Aplicaciones/Clipper/Linux"
WORK_DIR="$PROJECT_DIR/build/linux"

if [[ ! -x "$BUILD_PYTHON" ]]; then
	python3 -m venv "$PROJECT_DIR/.venv-build"
fi

"$BUILD_PYTHON" -m pip install -r "$PROJECT_DIR/requirements.txt" -r "$PROJECT_DIR/requirements-build.txt"
"$BUILD_PYTHON" -m PyInstaller --noconfirm --clean \
	--distpath "$OUTPUT_DIR" \
	--workpath "$WORK_DIR" \
	"$PROJECT_DIR/packaging/clipper.spec"