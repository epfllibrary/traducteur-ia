@echo off
pushd "%~dp0.."
echo === Build Traducteur 1.2.0 pour Windows ===
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://python.org
    pause
    exit /b 1
)

echo OK Python trouve
echo.

REM Verifier requirements.txt
if not exist "requirements.txt" (
    echo ERREUR requirements.txt non trouve dans le repertoire actuel
    echo Repertoire actuel: %CD%
    dir
    pause
    exit /b 1
)

REM Installer les dependances
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo ERREUR Python 3.11 minimum est requis
    exit /b 1
)
python -m venv build\venv-windows
if errorlevel 1 exit /b 1
set "BUILD_PYTHON=build\venv-windows\Scripts\python.exe"

echo Installation des dependances...
"%BUILD_PYTHON%" -m pip install --upgrade --upgrade-strategy eager -r requirements.txt
if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances
    pause
    exit /b 1
)

REM Installer PyInstaller
echo Installation de PyInstaller...
"%BUILD_PYTHON%" -m pip install --upgrade pip setuptools pyinstaller pip-audit
if errorlevel 1 (
    echo ERREUR lors de l'installation de PyInstaller
    pause
    exit /b 1
)

REM Creer l'executable
"%BUILD_PYTHON%" -m pip check
if errorlevel 1 exit /b 1
"%BUILD_PYTHON%" -m pip_audit
if errorlevel 1 (
    echo ERREUR audit des dependances : compilation annulee
    exit /b 1
)
echo Creation de l'executable...
"%BUILD_PYTHON%" -m PyInstaller --clean --onefile --windowed --add-data "../LICENSE:." --distpath bin --specpath build --name traducteur translate.py
if errorlevel 1 (
    echo ERREUR lors de la creation de l'executable
    pause
    exit /b 1
)

REM Verifier le resultat
if exist "bin/traducteur.exe" (
    echo OK Executable cree avec succes: bin/traducteur.exe
    for %%A in ("bin/traducteur.exe") do echo Taille: %%~zA octets
    echo.
    echo Pour utiliser l'application:
    echo 1. Copiez .translator_config.example.json vers bin/.translator_config.json
    echo 2. Configurez le serveur et le modele
    echo 3. Executez bin/traducteur.exe
) else (
    echo ERREUR L'executable n'a pas ete cree
    pause
    exit /b 1
)

echo.
echo Build termine avec succes !
popd
pause
