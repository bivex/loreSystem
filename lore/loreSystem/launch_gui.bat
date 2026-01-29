@echo off
REM MythWeave GUI Launcher Script for Windows
REM This script sets up the virtual environment and runs the GUI
REM Usage: launch_gui.bat [--auto-install] [--help]

REM Parse command line arguments
set "AUTO_INSTALL="
if "%1"=="--auto-install" set "AUTO_INSTALL=1"
if "%1"=="--help" goto :show_help

:show_help
if "%1"=="--help" (
    echo MythWeave GUI Launcher for Windows
    echo.
    echo Usage: launch_gui.bat [options]
    echo.
    echo Options:
    echo   --auto-install    Attempt automatic Python installation if not found
    echo   --help           Show this help message
    echo.
    echo Without options, runs interactively with installation choices.
    exit /b 0
)

echo 🎮 MythWeave GUI Launcher
echo =========================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 goto :need_python

REM Python found - continue with application setup
set "PYTHON_CMD=python"

REM Check if we're in the right directory
if not exist "run_gui.py" (
    echo ❌ Error: run_gui.py not found. Please run this script from the loreSystem directory.
    pause
    exit /b 1
)

REM Note: Running without virtual environment for compatibility
REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Check if PyQt6 is installed
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo 📥 Installing PyQt6...
    python -m pip install "PyQt6>=6.6.1"
    if errorlevel 1 (
        echo ❌ Error: Failed to install PyQt6.
        echo Check your internet connection and try again.
        pause
        exit /b 1
    )
)

REM Check if other dependencies are installed
python -c "import pydantic" 2>nul
if errorlevel 1 (
    echo 📥 Installing core dependencies...
    python -m pip install "pydantic>=2.5.3" dataclasses-json
    if errorlevel 1 (
        echo ❌ Error: Failed to install core dependencies.
        echo Check your internet connection and try again.
        pause
        exit /b 1
    )
)

REM Run the GUI
echo 🚀 Starting MythWeave GUI...
echo.
echo 💡 Tips:
echo    - Load sample data: Click 'Load' → Select examples/sample_lore.json
echo    - Create worlds in the 'Worlds' tab
echo    - Add characters with abilities in the 'Characters' tab
echo    - Save your work with 'Save' or 'Save As'
echo.
echo 📚 For help, see QUICKSTART_GUI.md
echo.

python run_gui.py
goto :eof

:need_python
    echo ❌ Python not found in PATH. Checking common installation locations...

    REM Check common Python installation paths
    set "PYTHON_FOUND="
    for %%p in (
        "C:\Python311\python.exe"
        "C:\Python312\python.exe"
        "C:\Python310\python.exe"
        "C:\Python39\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "%PROGRAMFILES%\Python311\python.exe"
        "%PROGRAMFILES%\Python312\python.exe"
    ) do (
        if exist %%p (
            echo ✅ Found Python at: %%p
            set "PYTHON_EXE=%%p"
            set "PYTHON_FOUND=1"
            goto :python_found
        )
    )

    REM If not found in common locations, offer automatic installation
    echo ❌ Python not found in common locations either.

    if defined AUTO_INSTALL (
        echo Auto-install flag detected, attempting automatic installation...
        goto :auto_install
    )

    echo.
    echo Choose installation method:
    echo [1] Automatic installation (requires administrator privileges)
    echo [2] Manual installation instructions
    echo [3] Skip and use existing Python path (if you know where it is)
    echo.

    set /p "choice=Enter choice (1-3): "
    if "%choice%"=="1" goto :auto_install
    if "%choice%"=="2" goto :manual_install
    if "%choice%"=="3" goto :custom_path
    REM If no valid choice made, default to manual instructions
    goto :manual_install

    :auto_install
    REM Check if running as administrator
    net session >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Running as administrator - proceeding with automatic installation
    ) else (
        echo ⚠️  Administrator privileges required for automatic Python installation.
        echo Please run this batch file as administrator to use automatic installation.
        goto :manual_install
    )

    REM Download Python installer using PowerShell
    echo 📥 Downloading Python installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'}"

    if not exist "python-installer.exe" (
        echo ❌ Failed to download Python installer.
        goto :manual_install
    )

    REM Install Python silently
    echo 🔧 Installing Python silently...
    python-installer.exe /quiet /passive InstallAllUsers=0 PrependPath=1 Include_test=0

    REM Clean up installer
    del python-installer.exe

    REM Refresh environment variables
    echo 🔄 Refreshing environment variables...
    call refreshenv.cmd >nul 2>&1 || (
        REM Fallback: restart this script
        echo ✅ Python installed. Please run this script again.
        pause
        exit /b 0
    )

    REM Verify installation
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python installation verification failed.
        goto :manual_install
    )

    echo ✅ Python installed successfully!
    set "PYTHON_CMD=python"
    echo.
    goto :python_ready

    :manual_install
    echo.
    echo 📋 Manual Python Installation Instructions:
    echo 1. Visit https://python.org/downloads/
    echo 2. Download the latest Python installer for Windows
    echo 3. Run the installer and make sure to check "Add Python to PATH"
    echo 4. Restart your command prompt and run this script again
    echo.
    echo Or download and run this installer manually:
    echo https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    echo.
    pause
    exit /b 1

    :custom_path
    echo.
    set /p "PYTHON_EXE=Enter full path to python.exe: "
    if not exist "%PYTHON_EXE%" (
        echo ❌ Python not found at specified path.
        goto :manual_install
    )
    goto :python_found

    :python_found
    REM Use the found/custom Python path for all python commands
    set "PYTHON_CMD=%PYTHON_EXE%"
    echo Using Python: %PYTHON_CMD%
    goto :python_ready

    :python_ready