#!/bin/bash
# Launcher for Asset Scanner using local venv for performance
VENV_PYTHON="/Users/ttyler/asset_scanner_venv/bin/python"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Local venv not found at /Users/ttyler/asset_scanner_venv"
    echo "Please run setup_local_venv.sh again."
    exit 1
fi

echo "Launching Asset Scanner using local venv..."
"$VENV_PYTHON" "$PROJECT_DIR/metadata_browser.py"
