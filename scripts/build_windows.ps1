# Script de build pour Windows
# A executer sur Windows natif

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
Set-Location $repoRoot

Write-Host "=== Build Traducteur 1.1.0 pour Windows ===" -ForegroundColor Green

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
Write-Host "Installation des dependances..." -ForegroundColor Blue
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation des dependances" -ForegroundColor Red
    exit 1
}

# Installer PyInstaller
Write-Host "Installation de PyInstaller..." -ForegroundColor Blue
pip install pyinstaller

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de l'installation de PyInstaller" -ForegroundColor Red
    exit 1
}

# Creer l'executable
Write-Host "Creation de l'executable..." -ForegroundColor Blue
pyinstaller --onefile --windowed --name traducteur translate.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR lors de la creation de l'executable" -ForegroundColor Red
    exit 1
}

# Verifier le resultat
$exePath = "dist/traducteur.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "OK Executable cree avec succes: $exePath" -ForegroundColor Green
    Write-Host "Taille: $([math]::Round($size, 1)) Mo" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "Pour utiliser l'application:" -ForegroundColor Green
    Write-Host "1. Copiez .translator_config.example.json vers dist/.translator_config.json" -ForegroundColor White
    Write-Host "2. Configurez le serveur et le modele" -ForegroundColor White
    Write-Host "3. Executez $exePath" -ForegroundColor White
} else {
    Write-Host "ERREUR L'executable n'a pas ete cree" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "Build termine avec succes !" -ForegroundColor Green
