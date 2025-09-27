#!/bin/bash

echo "====================================================="
echo "Setting up Socratic AI Tutor Tutorial Environment..."
echo "====================================================="

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 could not be found. Please install Python 3."
    exit 1
fi

echo "[1/4] Creating a Python virtual environment in 'venv'..."
python3 -m venv venv

echo "[2/4] Activating the virtual environment for this script..."
source venv/bin/activate

echo "[3/4] Installing required packages from requirements.txt..."
pip install -r requirements.txt

echo "[4/4] Creating the .env file for your API key..."
# Create .env file but don't overwrite if it already exists
if [ ! -f .env ]; then
    echo "GEMINI_API_KEY='YOUR_API_KEY_HERE'" > .env
    echo ".env file created. Please edit it with your Gemini API key."
else
    echo ".env file already exists. Please ensure your GEMINI_API_KEY is set."
fi

echo ""
echo "====================================================="
echo "✅ Setup Complete!"
echo "====================================================="
echo "Next Steps:"
echo "1. IMPORTANT: Open the '.env' file and replace 'YOUR_API_KEY_HERE' with your actual Gemini API key."
echo "2. Activate the environment in your terminal by running: source venv/bin/activate"
echo "3. Start Jupyter Lab by running: jupyter lab"
echo "====================================================="