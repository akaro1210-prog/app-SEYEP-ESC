@echo off
chcp 65001 >nul
title Servidor Generador de Informes SEYEP S.A.S.
echo =====================================================================
echo   INICIANDO SERVIDOR WEB - GENERADOR DE INFORMES SEYEP S.A.S.
echo =====================================================================
echo.
echo Direcciones IP de este equipo para compartir con tus companeros:
ipconfig | findstr /i "IPv4"
echo.
echo Tus companeros en la misma red Wi-Fi / LAN o VPN pueden entrar desde
echo su navegador Chrome o Edge escribiendo:
echo    http://TU_DIRECCION_IPV4:8501
echo.
echo (No cierres esta ventana mientras tus companeros esten usando la app)
echo =====================================================================
echo.

cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
pause
