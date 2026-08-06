@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git no esta instalado o no esta en PATH.
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH.
    exit /b 1
)

echo [1/4] Activando soporte de Git LFS...
git lfs install

echo [2/4] Creando entorno virtual...
if not exist ".venv" python -m venv .venv

echo [3/4] Instalando dependencias...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [4/4] Preparando ejecucion del servidor...
echo.
echo Instalacion completada.
echo Para iniciar el proyecto usa:
echo   .venv\Scripts\activate
echo   cd _MaxArm_Playground
echo   python -m uvicorn server:app --host 127.0.0.1 --port 8000
echo.
pause