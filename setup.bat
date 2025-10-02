@echo off
setlocal

echo =================================================================
echo  Setting up the Socratic AI Tutor Tutorial Environment
echo =================================================================
echo.

rem --- Step 1: Check if Python is installed and in PATH ---
echo [1/5] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python command not found.
    echo    Please install Python 3.13.2 from python.org and ensure it is added to your system's PATH.
    goto :error
)
echo ✅ Python is installed.
echo.

rem --- Step 2: Check for the correct Python version (must be 3.13.2) ---
echo [2/5] Verifying Python version...
for /f "delims=" %%v in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"') do set "PY_VERSION=%%v"

if not "%PY_VERSION%"=="3.13.2" (
    echo ❌ ERROR: Incorrect Python version detected.
    echo    This tutorial requires Python EXACTLY version 3.13.2.
    echo    You are currently using version: %PY_VERSION%.
    echo    Please download the correct version from: https://www.python.org/downloads/release/python-3132/
    goto :error
)
echo ✅ Python version 3.13.2 confirmed.
echo.

rem --- Step 3: Create the Python virtual environment ---
echo [3/5] Creating virtual environment in '.\venv\'...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to create the virtual environment.
    goto :error
)
echo ✅ Virtual environment created successfully.
echo.

rem --- Step 4: Install required packages ---
echo [4/5] Activating environment and installing packages from requirements.txt...
echo      (This may take a few moments)
call venv\Scripts\activate.bat && pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install required packages. Please check your internet connection and try again.
    goto :error
)
echo ✅ All required packages installed successfully.
echo.

rem --- Step 5: Create the .env file for the API key ---
echo [5/5] Preparing the .env file for your API key...
if not exist .env (
    echo GEMINI_API_KEY='YOUR_API_KEY_HERE' > .env
    echo ✅ '.env' file created. You will need to add your API key to it.
) else (
    echo ✅ '.env' file already exists. Please ensure your API key is set correctly.
)
echo.

echo =================================================================
echo  🎉 Setup Complete!
echo =================================================================
echo.
echo  Next Steps:
echo  1. IMPORTANT: Open the '.env' file and replace 'YOUR_API_KEY_HERE' with your Google Gemini API key.
echo  2. In your terminal, activate the new environment by running: venv\Scripts\activate
echo  3. Launch the tutorial by running: jupyter lab
echo.
goto :eof

:error
echo.
echo =================================================================
echo  Setup failed. Please review the error message above.
echo =================================================================
endlocal