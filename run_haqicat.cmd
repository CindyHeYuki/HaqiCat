@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo HaqiCat virtual environment is missing. Install dependencies first.
    exit /b 1
)

set "PYTHONPATH=%PROJECT_ROOT%src"
"%PYTHON_EXE%" -m haqicat.app %*
exit /b %ERRORLEVEL%

