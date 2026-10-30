# Script de build pour Windows
# A executer sur Windows natif

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $repoRoot

Write-Host "=== Build Traducteur 1.1.1 pour Windows ===" -ForegroundColor Green

# Verifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK Python trouve: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR Python n'est pas installe ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Telechargez Python depuis https://python.org" -ForegroundColor Yellow
    exit 1
}

# Installer les dependances
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR Python 3.11 minimum est requis" -ForegroundColor Red
    exit 1
}

# Isoler les paquets embarques dans l'executable.
python -m venv build/venv-windows
if ($LASTEXITCODE -ne 0) { exit 1 }
$buildPython = Join-Path $repoRoot "build/venv-windows/Scripts/python.exe"

Write-Host "Installation des dependances..." -ForegroundColor Blue
& $buildPython -m pip install --upgrade --upgrade-strategy eager -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation des dependances" -ForegroundColor Red
    exit 1
}

# Installer PyInstaller
Write-Host "Installation de PyInstaller..." -ForegroundColor Blue
& $buildPython -m pip install --upgrade pip setuptools pyinstaller pip-audit

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation de PyInstaller" -ForegroundColor Red
    exit 1
}

# Creer l'executable
& $buildPython -m pip check
if ($LASTEXITCODE -ne 0) { exit 1 }
& $buildPython -m pip_audit
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR audit des dependances : compilation annulee" -ForegroundColor Red
    exit 1
}

Write-Host "Creation de l'executable..." -ForegroundColor Blue
& $buildPython -m PyInstaller --clean --onefile --windowed --distpath bin --specpath build --name traducteur translate.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la creation de l'executable" -ForegroundColor Red
    exit 1
}

# Verifier le resultat
$exePath = "bin/traducteur.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "OK Executable cree avec succes: $exePath" -ForegroundColor Green
    Write-Host "Taille: $([math]::Round($size, 1)) Mo" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "Pour utiliser l'application:" -ForegroundColor Green
    Write-Host "1. Copiez .translator_config.example.json vers bin/.translator_config.json" -ForegroundColor White
    Write-Host "2. Configurez le serveur et le modele" -ForegroundColor White
    Write-Host "3. Executez $exePath" -ForegroundColor White
} else {
    Write-Host "ERREUR L'executable n'a pas ete cree" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "Build termine avec succes !" -ForegroundColor Green
