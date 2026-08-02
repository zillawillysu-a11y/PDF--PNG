@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python and enable "Add python.exe to PATH".
  pause
  exit /b 1
)

echo Creating virtual environment...
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto :error
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -U pip
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

echo Building PDF2PNG.exe ...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean pdf2png.spec
if errorlevel 1 goto :error

echo.
echo Done.
echo Output: %cd%\dist\PDF2PNG.exe
echo You can copy that file anywhere and double-click to run.
echo.
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
