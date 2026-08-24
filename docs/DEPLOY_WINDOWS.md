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
pyinstaller --onefile --windowed --distpath bin --name traducteur translate.py
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
- Un serveur Ollama ou compatible OpenAI/vLLM, local ou distant

## Installation des dépendances
```cmd
pip install -r requirements.txt
```

## Création de l'exécutable
```cmd
REM Installer PyInstaller
pip install pyinstaller

REM Créer l'exécutable
pyinstaller --onefile --windowed --distpath bin --name traducteur translate.py
```

## Distribution
- Distribuer uniquement `bin/traducteur-setup.exe`; son assistant crée la configuration et peut proposer l'installation officielle d'Ollama
- Avec Ollama et le modèle installés sur le poste, l'application peut fonctionner entièrement en local : les textes ne quittent pas la machine; Internet n'est requis que pour les téléchargements initiaux ou les mises à jour souhaitées
- Le profil EPFL préconfigure RCP avec `swiss-ai/Apertus-v1.5-8B`; l'utilisateur crée sa clé sur https://portal.rcp.epfl.ch/aiaas/keys
- RCP est réservé aux membres de l'EPFL; les utilisateurs externes sélectionnent **Autre serveur** et configurent Ollama ou leur propre endpoint OpenAI/vLLM
- Ne pas publier séparément `bin/traducteur.exe` : cet artefact interne est intégré à l'installateur
- Pour un usage local : installer Ollama séparément et télécharger le modèle configuré
- Le raccourci de démarrage automatique est proposé par défaut et peut être désélectionné indépendamment du réglage d'affichage en arrière-plan
- Une installation existante est détectée par le registre ou le dossier par défaut; l'assistant propose de réinstaller ou désinstaller, avec une case indépendante pour conserver la configuration
- Si l'application est en cours d'exécution, l'assistant propose de l'arrêter automatiquement
- Le menu Démarrer contient une entrée **Désinstaller Traducteur**
- Le désinstalleur demande si `.translator_config.json` et `.translator_state.json` doivent également être supprimés

## Utilisation
1. Pour un usage local, lancer Ollama : `ollama serve`
2. Vérifier que `.translator_config.json` se trouve à côté de l'exécutable
3. Exécuter `traducteur.exe`
4. Importer des fichiers .txt, .docx, .pdf puis traduire

## Dépannage
- **Erreur "application ne peut pas s'exécuter"** : L'exécutable a été créé sur le mauvais OS
- Si l'exécutable ne se lance pas : Vérifier les droits d'exécution
- Erreur de connexion : vérifier que `server_url` contient l'endpoint d'inférence complet ; en local, vérifier qu'Ollama fonctionne (`ollama list`)
- Fichiers non supportés : Installer python-docx et pdfplumber

## Scripts de build automatisés

### Scripts disponibles (Corrigés)
- `scripts/build_windows.ps1` : Script PowerShell (recommandé)
- `scripts/build_windows.bat` : Script batch pour cmd
- `scripts/build_installer.ps1` : Script PowerShell pour Inno Setup 6
- `docs/BUILD_INSTRUCTIONS.md` : Instructions détaillées

### Utilisation
```cmd
REM Sur Windows, dans le dossier du projet
.\scripts\build_windows.ps1

REM Puis, après installation d'Inno Setup 6
.\scripts\build_installer.ps1
```

## Alerte Windows actuelle

L'exécutable et l'installateur ne sont pas encore signés numériquement. Windows peut donc afficher « Éditeur inconnu » ou une alerte SmartScreen. Il ne faut jamais recommander de désactiver SmartScreen globalement; l'utilisateur ne doit poursuivre que si le fichier provient du dépôt officiel. Cette limitation sera levée lorsque le projet disposera d'un certificat de signature de code.

### Dépannage des scripts
- **Erreur d'encodage** : Scripts corrigés avec caractères ASCII simples
- **requirements.txt introuvable** : Vérification explicite du fichier
- **PowerShell bloqué** : `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
