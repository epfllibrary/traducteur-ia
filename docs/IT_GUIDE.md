# Guide pour l'IT - Déploiement Traducteur

## Problème
L'application Python doit être compilée sur Windows pour créer un exécutable Windows.

## Solution simple
1. **Machine Windows** : Utiliser un PC Windows (même temporaire)
2. **Scripts fournis** : `scripts/build_windows.ps1` ou `scripts/build_windows.bat`
3. **Résultat** : Exécutable `traducteur.exe` (~50 Mo)

## Instructions pour l'IT

### Prérequis sur le PC Windows
- Windows 10/11
- Python 3.8+ installé
- Connexion internet

### Étapes
```cmd
# 1. Copier les fichiers du projet
# 2. Ouvrir PowerShell en admin
# 3. Aller dans le dossier
# 4. Exécuter le script
.\scripts\build_windows.ps1
```

### Résultat attendu
- Dossier `dist/` créé
- Fichier `traducteur.exe`
- Taille : ~50 Mo
- Standalone (pas besoin de Python)

### Déploiement
- Copier l'exe sur les PCs utilisateurs
- Déposer obligatoirement `.translator_config.json` à côté de l'exe, avec le serveur et le modèle à utiliser
- Pour un modèle local uniquement : installer Ollama et télécharger le modèle configuré
- Pour un serveur distant protégé : renseigner la clé API dans la configuration

## Sécurité
- L'exe est créé avec PyInstaller (outil standard)
- Pas de code malveillant
- Dépendances : requests, customtkinter, pystray, pillow, pynput, pdfplumber, python-docx

## Support
Si problème, utiliser les alternatives :
- auto-py-to-exe (outil web)
- PythonAnywhere (cloud)
- Machine virtuelle Windows
