@echo off
title Servidor MaxArm Robotics Studio
cls
echo ============================================================
echo      REINICIANDO SERVIDOR MAXARM (AUTO-RELOAD ACTIVADO)
echo ============================================================
echo.
echo [1/2] Liberando puerto 8000 y conexion serie COM6...
powershell -Command "Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force"
timeout /t 1 /nobreak >nul

echo.
echo [2/2] Iniciando servidor Uvicorn con recarga automatica (--reload)...
echo.
cd %~dp0\_MaxArm_Playground
..\\.venv\\Scripts\\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

pause
