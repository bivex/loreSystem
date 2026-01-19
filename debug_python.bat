@echo off
echo Testing Python detection...

echo Running: python --version
python --version
echo ErrorLevel: %errorlevel%

echo.
echo Testing with redirection: python --version ^>nul 2^>^&1
python --version >nul 2>&1
echo ErrorLevel after redirection: %errorlevel%

echo.
echo Testing where python:
where python
echo ErrorLevel: %errorlevel%

pause