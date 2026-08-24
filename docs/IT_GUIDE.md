# Guide pour l'IT - Déploiement Traducteur

## Problème
L'application Python doit être compilée sur Windows pour créer un exécutable Windows.

## Solution simple
1. **Machine Windows** : Utiliser un PC Windows (même temporaire)
2. **Scripts fournis** : `scripts/build_windows.ps1` ou `scripts/build_windows.bat`
3. **Résultat** : Installateur `traducteur-setup.exe` prêt à être distribué

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
- Dossier `bin/` créé
- Fichier interne `traducteur.exe`, puis installateur public `traducteur-setup.exe`
- Taille : ~50 Mo
- Standalone (pas besoin de Python)

### Déploiement
- Distribuer uniquement `bin/traducteur-setup.exe`; ne pas publier séparément l'exécutable interne
- Laisser l'assistant créer le fichier de configuration avec le serveur et soit `default_model`, soit `models_url`
- Pour un modèle local uniquement : laisser l'assistant installer et démarrer Ollama, puis télécharger automatiquement le modèle configuré; `ministral-3:3b` est proposé initialement
- Pour un serveur distant Ollama ou OpenAI/vLLM protégé : renseigner la clé API dans la configuration

## Sécurité
- L'exe est créé avec PyInstaller (outil standard)
- Pas de code malveillant
- Dépendances : requests, customtkinter, pystray, pillow, pynput, pdfplumber, python-docx

## Support
Si problème, utiliser les alternatives :
- auto-py-to-exe (outil web)
- PythonAnywhere (cloud)
- Machine virtuelle Windows
