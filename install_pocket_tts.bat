@echo off

title Install ComfyUI-Pocket-TTS

echo ================================================
echo Installing ComfyUI-Pocket-TTS Custom Node
echo ================================================
echo.

REM Navigate to ComfyUI directory
cd /d C:\ComfyUI

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call comfyui_venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Navigate to custom_nodes directory
echo [2/4] Navigating to custom_nodes directory...
cd custom_nodes
echo ✓ In custom_nodes directory
echo.

REM Clone the repository
echo [3/4] Cloning ComfyUI-Pocket-TTS repository...
git clone https://github.com/ai-joe-git/ComfyUI-Pocket-TTS
if %errorlevel% neq 0 (
    echo ✗ Error: Failed to clone repository
    pause
    exit /b 1
)

echo ✓ Repository cloned successfully
echo.

REM Install requirements
echo [4/4] Installing dependencies...
cd ComfyUI-Pocket-TTS
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ✗ Error: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully
echo.

echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo The ComfyUI-Pocket-TTS node has been installed.
echo Please restart ComfyUI to use the new nodes.
echo.
pause
