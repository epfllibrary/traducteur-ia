# Instructions de déploiement Windows

## ⚠️ **Important : Cross-compilation**

**L'exécutable créé sur Linux ne fonctionne pas sur Windows !**
- PyInstaller crée des binaires spécifiques à l'OS/architecture
- Un exe Linux ne peut pas tourner sur Windows
- Il faut compiler sur le système cible

## Solutions

### Solution 1 : Compiler sur Windows natif (Recommandée)
```cmd
REM Sur Windows, ouvrir PowerShell/Command Prompt
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --name traducteur translate.py
```

### Solution 2 : Utiliser Docker (Cross-compilation)
```bash
# Depuis Linux/WSL
docker run --rm -v $(pwd):/app -w /app python:3.9-windowsservercore pyinstaller --onefile --windowed --name traducteur translate.py
```

### Solution 3 : Machine virtuelle Windows
- Installer Windows dans VirtualBox/VMware
- Compiler l'exécutable dans la VM
- Récupérer le fichier .exe généré

## Prérequis
- Windows 10/11
- Python 3.8+ installé
- Un serveur compatible Ollama, local ou distant

## Installation des dépendances
```cmd
pip install -r requirements.txt
```

## Création de l'exécutable
```cmd
REM Installer PyInstaller
pip install pyinstaller

REM Créer l'exécutable
pyinstaller --onefile --windowed --name traducteur translate.py
```

## Distribution
- Copier `dist/traducteur.exe` sur le système cible
- Copier obligatoirement `.translator_config.json` à côté de l'exécutable et y définir le serveur et le modèle
- Pour un usage local : installer Ollama séparément et télécharger le modèle configuré

## Utilisation
1. Pour un usage local, lancer Ollama : `ollama serve`
2. Vérifier que `.translator_config.json` se trouve à côté de l'exécutable
3. Exécuter `traducteur.exe`
4. Importer des fichiers .txt, .docx, .pdf puis traduire

## Dépannage
- **Erreur "application ne peut pas s'exécuter"** : L'exécutable a été créé sur le mauvais OS
- Si l'exécutable ne se lance pas : Vérifier les droits d'exécution
- Erreur de connexion : Vérifier `server_url` ; en local, vérifier qu'Ollama fonctionne (`ollama list`)
- Fichiers non supportés : Installer python-docx et pdfplumber

## Scripts de build automatisés

### Scripts disponibles (Corrigés)
- `scripts/build_windows.ps1` : Script PowerShell (recommandé)
- `scripts/build_windows.bat` : Script batch pour cmd
- `docs/BUILD_INSTRUCTIONS.md` : Instructions détaillées

### Utilisation
```cmd
REM Sur Windows, dans le dossier du projet
.\scripts\build_windows.ps1
```

### Dépannage des scripts
- **Erreur d'encodage** : Scripts corrigés avec caractères ASCII simples
- **requirements.txt introuvable** : Vérification explicite du fichier
- **PowerShell bloqué** : `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
