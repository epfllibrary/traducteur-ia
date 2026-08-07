param(
    [string]$InnoCompiler = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Executable = Join-Path $ProjectRoot "dist\traducteur.exe"
$InstallerScript = Join-Path $ProjectRoot "installer\traducteur.iss"
$Installer = Join-Path $ProjectRoot "dist\traducteur-setup.exe"

if (-not (Test-Path $Executable)) {
    throw "Executable introuvable : $Executable. Compilez d'abord traducteur.exe."
}

if (-not (Test-Path $InstallerScript)) {
    throw "Script Inno Setup introuvable : $InstallerScript"
}

if (-not $InnoCompiler) {
    $Candidates = @(
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
    )
    $InnoCompiler = $Candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
}

if (-not $InnoCompiler -or -not (Test-Path $InnoCompiler)) {
    throw "Inno Setup 6 est introuvable. Installez-le avec : winget install --id JRSoftware.InnoSetup -e"
}

Write-Host "Compilation de l'installateur avec $InnoCompiler"
& $InnoCompiler $InstallerScript
if ($LASTEXITCODE -ne 0) {
    throw "La compilation Inno Setup a échoué avec le code $LASTEXITCODE."
}

if (-not (Test-Path $Installer)) {
    throw "L'installateur attendu n'a pas été créé : $Installer"
}

$Signature = Get-AuthenticodeSignature $Installer
Write-Host "Installateur créé : $Installer"
Write-Host "Taille : $([math]::Round((Get-Item $Installer).Length / 1MB, 1)) Mo"
Write-Host "Signature : $($Signature.Status)"
if ($Signature.Status -ne "Valid") {
    Write-Warning "L'installateur n'est pas signé. Windows peut afficher une alerte SmartScreen."
}
