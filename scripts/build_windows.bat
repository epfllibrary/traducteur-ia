@echo off
pushd "%~dp0.."
echo === Build Traducteur 1.1.0 pour Windows ===
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
echo Installation des dependances...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances
    pause
    exit /b 1
)

REM Installer PyInstaller
echo Installation de PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERREUR lors de l'installation de PyInstaller
    pause
    exit /b 1
)

REM Creer l'executable
echo Creation de l'executable...
pyinstaller --onefile --windowed --name traducteur translate.py
if errorlevel 1 (
    echo ERREUR lors de la creation de l'executable
    pause
    exit /b 1
)

REM Verifier le resultat
if exist "dist/traducteur.exe" (
    for %%A in ("dist/traducteur.exe") do set size=%%~zA
    set /a size_mb=%size%/1048576
    echo OK Executable cree avec succes: dist/traducteur.exe
    echo Taille: %size_mb% Mo
    echo.
    echo Pour utiliser l'application:
    echo 1. Copiez .translator_config.example.json vers dist/.translator_config.json
    echo 2. Configurez le serveur et le modele
    echo 3. Executez dist/traducteur.exe
) else (
    echo ERREUR L'executable n'a pas ete cree
    pause
    exit /b 1
)

echo.
echo Build termine avec succes !
popd
pause
