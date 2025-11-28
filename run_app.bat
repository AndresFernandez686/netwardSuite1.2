@echo off
echo ==========================================
echo    BUSINESSSUITE - SUITE DE NEGOCIO
echo ==========================================
echo.
echo Iniciando aplicacion...
echo.

REM Cambiar al directorio de la aplicacion
cd /d "%~dp0"

REM Mostrar directorio actual
echo Directorio actual: %CD%
echo.

REM Verificar que main.py existe
if not exist "main.py" (
    echo ERROR: No se encontro main.py
    echo Archivos disponibles:
    dir *.py
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

REM Verificar Streamlit
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Streamlit no esta instalado
    echo Instalando Streamlit...
    pip install streamlit
)

echo.
echo Ejecutando BusinessSuite...
echo.
echo La aplicacion se abrira en tu navegador web
echo URL: http://localhost:8501
echo.
echo Para detener la aplicacion: Presiona Ctrl+C
echo.

REM Ejecutar la aplicacion
python -m streamlit run main.py --server.headless true --server.port 8501 --server.address localhost

pause