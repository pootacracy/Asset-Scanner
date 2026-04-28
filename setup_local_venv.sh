#!/bin/bash
set -e

# Define the local venv path
VENV_PATH="$HOME/asset_scanner_venv"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_EXEC="/usr/bin/python3" # Using system python 3.9.6 for better compatibility

echo "--- Asset Scanner Local Venv Setup ---"
echo "Project Directory: $PROJECT_DIR"
echo "Local Venv Path:   $VENV_PATH"
echo "Python Version:    $($PYTHON_EXEC --version)"
echo ""

# 1. Create the virtual environment if it doesn't exist
if [ -d "$VENV_PATH" ]; then
    echo "Cleaning up old venv..."
    rm -rf "$VENV_PATH"
fi

echo "[1/3] Creating local virtual environment at $VENV_PATH..."
$PYTHON_EXEC -m venv "$VENV_PATH"

# 2. Install requirements
echo "[2/3] Installing dependencies..."
"$VENV_PATH/bin/pip" install --upgrade pip
"$VENV_PATH/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# 3. Link the local venv to the project directory
echo "[3/4] Linking local venv to the project directory..."
SLOW_VENV="$PROJECT_DIR/.venv"
if [ -d "$SLOW_VENV" ] && [ ! -L "$SLOW_VENV" ]; then
    echo "Backing up slow network venv to .venv_slow..."
    mv "$SLOW_VENV" "${SLOW_VENV}_slow"
fi

if [ -L "$SLOW_VENV" ]; then
    rm "$SLOW_VENV"
fi
ln -s "$VENV_PATH" "$SLOW_VENV"

# 4. Create launcher
LAUNCHER="$PROJECT_DIR/run_app.sh"
echo "[4/4] Creating launcher script: $LAUNCHER"

cat > "$LAUNCHER" << EOF
#!/bin/bash
# Launcher for Asset Scanner using local venv for performance
VENV_PYTHON="$VENV_PATH/bin/python"
PROJECT_DIR="\$(cd "\$(dirname "\$0")" && pwd)"

if [ ! -f "\$VENV_PYTHON" ]; then
    echo "Error: Local venv not found at $VENV_PATH"
    echo "Please run setup_local_venv.sh again."
    exit 1
fi

echo "Launching Asset Scanner using local venv..."
"\$VENV_PYTHON" "\$PROJECT_DIR/metadata_browser.py"
EOF

chmod +x "$LAUNCHER"

echo ""
echo "--- Setup Complete! ---"
echo "To run the application with high performance, use:"
echo "  ./run_app.sh"
echo ""
