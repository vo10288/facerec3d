@echo off
echo ========================================
echo Comparatore Biometrico Volti 3D
echo Installazione Dipendenze per Windows
echo ========================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato!
    echo Scarica Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python trovato
python --version
echo.

echo [INFO] Aggiornamento pip...
python -m pip install --upgrade pip
echo.

echo [INFO] Installazione dipendenze...
echo.

echo [1/4] Installazione opencv-python...
pip install opencv-python
echo.

echo [2/4] Installazione mediapipe...
pip install mediapipe
echo.

echo [3/4] Installazione pillow...
pip install pillow
echo.

echo [4/4] Installazione numpy...
pip install numpy
echo.

echo ========================================
echo [OK] Installazione completata!
echo ========================================
echo.
echo Per avviare l'applicazione:
echo   python comparatore_volti_gui.py
echo.
pause
