#!/bin/bash

echo "====================================================="
echo "Setting up Socratic AI Tutor Tutorial Environment..."
echo "====================================================="

# Check for python3 command
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 could not be found. Please install Python 3.13.2."
    exit 1
fi

# --- NEW: Check Python version ---
PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
if [[ "$PY_VERSION" != "3.13.2" ]]; then
    echo "❌ ERROR: Incorrect Python version."
    echo "This tutorial requires Python 3.13.2, but you are using $PY_VERSION."
    echo "Please install the correct version from https://www.python.org/downloads/release/python-3132/"
    exit 1
fi
echo "✅ Python 3.13.2 found."

echo "[1/4] Creating Python virtual environment 'venv'..."
python3 -m venv venv

echo "[2/4] Activating the virtual environment for this script..."
source venv/bin/activate

echo "[3/4] Installing required packages from requirements.txt..."
pip install -r requirements.txt

echo "[4/4] Creating the optional local .env file..."
# Create .env file but don't overwrite if it already exists
if [ ! -f .env ]; then
    printf "OPENAI_API_KEY=\nGEMINI_API_KEY=\n" > .env
    echo ".env file created. Keys are optional and can also be entered in Notebooks 01–03."
else
    echo ".env file already exists; it was not overwritten."
fi

echo ""
echo "====================================================="
echo "✅ Setup Complete!"
echo "====================================================="
echo "Next Steps:"
echo "1. Activate the environment in your terminal: source venv/bin/activate"
echo "2. Start Jupyter Lab: jupyter lab"
echo "3. Optional: enter an OpenAI or Google key in the final cell of Notebooks 01–03."
echo "====================================================="
