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

rem --- Step 5: Create an optional local .env file ---
echo [5/5] Preparing the optional local .env file...
if not exist .env (
    (echo OPENAI_API_KEY=& echo GEMINI_API_KEY=) > .env
    echo ✅ '.env' file created. Keys can also be entered in Notebooks 01-03.
) else (
    echo ✅ '.env' already exists and was not overwritten.
)
echo.

echo =================================================================
echo  🎉 Setup Complete!
echo =================================================================
echo.
echo  Next Steps:
echo  1. Activate the environment: venv\Scripts\activate
echo  2. Launch the tutorial: jupyter lab
echo  3. Optional: enter an OpenAI or Google key in the final cell of Notebooks 01-03.
echo.
goto :eof

:error
echo.
echo =================================================================
echo  Setup failed. Please review the error message above.
echo =================================================================
endlocal
