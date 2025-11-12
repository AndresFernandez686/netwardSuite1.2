@echo off
echo ========================================
echo    🏢 BusinessSuite - Iniciando...
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar si pip está disponible  
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip no está disponible
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo.

REM Verificar si existe entorno virtual
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activando entorno virtual existente...
    call .venv\Scripts\activate.bat
) else (
    echo 🔧 Creando entorno virtual...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo ✅ Entorno virtual creado y activado
)

echo.
echo 📦 Instalando/Verificando dependencias...
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente
echo.

REM Ejecutar configuración inicial
echo 🔧 Ejecutando configuración inicial...
python config.py

echo.
echo � Verificando sistema...
python verificar_sistema.py

if %errorlevel% neq 0 (
    echo ❌ Error en la verificación del sistema
    echo Revisa los mensajes anteriores para solucionar los problemas
    pause
    exit /b 1
)

echo.
echo �🚀 Iniciando BusinessSuite...
echo.
echo ========================================
echo    📱 Abriendo en el navegador...
echo    🌐 URL: http://localhost:8501
echo ========================================
echo.
echo Para cerrar la aplicación, presiona Ctrl+C
echo.

REM Ejecutar Streamlit
streamlit run main.py

echo.
echo 👋 BusinessSuite cerrado
pause