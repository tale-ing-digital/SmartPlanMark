@echo off
echo ========================================
echo SmartPlanMark - Inicio Rapido
echo TalePlanHub (c) 2025
echo ========================================
echo.

echo [1/3] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado
    echo Descargalo desde: https://nodejs.org/
    pause
    exit /b 1
)
echo OK - Node.js detectado

echo.
echo [2/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Descargalo desde: https://www.python.org/
    pause
    exit /b 1
)
echo OK - Python detectado

echo.
echo [3/3] Verificando Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Tesseract OCR no esta en el PATH
    echo Descargalo desde: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo El sistema puede no funcionar correctamente sin Tesseract.
    echo Presiona cualquier tecla para continuar de todos modos...
    pause >nul
) else (
    echo OK - Tesseract OCR detectado
)

echo.
echo ========================================
echo Iniciando servidor...
echo ========================================
echo.
echo Accede a: http://localhost:3000
echo.

npm start
