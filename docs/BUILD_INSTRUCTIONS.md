# Instructions pour créer l'exécutable Windows

## Problèmes résolus
- ❌ Caractères spéciaux (accents, emojis) causaient des erreurs d'encodage
- ❌ Script .bat ne trouvait pas requirements.txt
- ✅ Scripts corrigés avec caractères ASCII simples
- ✅ Vérification explicite du fichier requirements.txt

## Utilisation

### Sur Windows avec PowerShell (Recommandé)
1. Copiez tous les fichiers du projet sur Windows
2. Ouvrez PowerShell
3. Allez dans le dossier du projet
4. Exécutez : `.\scripts\build_windows.ps1`

### Sur Windows avec CMD
1. Copiez tous les fichiers du projet sur Windows
2. Ouvrez l'invite de commande (cmd)
3. Allez dans le dossier du projet
4. Exécutez : `scripts\build_windows.bat`

## Dépannage

### Si PowerShell bloque l'exécution
```powershell
# Autoriser l'exécution de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Si pip n'est pas trouvé
- Assurez-vous que Python est installé et dans le PATH
- Utilisez `py -m pip` au lieu de `pip`

### Fichiers requis
Assurez-vous d'avoir ces fichiers dans le même dossier :
- `translate.py`
- `requirements.txt`
- `scripts/build_windows.ps1` ou `scripts/build_windows.bat`
- `.translator_config.example.json` pour préparer la configuration obligatoire

## Résultat attendu
- Dossier `dist/` créé avec `traducteur.exe`
- Taille approximative : 50 Mo
- Exécutable standalone (pas besoin de Python sur le système cible)

## Création de l'installateur guidé

Après avoir créé `dist/traducteur.exe` :

1. Installez [Inno Setup 6](https://jrsoftware.org/isinfo.php), ou exécutez `winget install --id JRSoftware.InnoSetup -e`.
2. Lancez `.\scripts\build_installer.ps1` depuis PowerShell.
3. Récupérez `dist\traducteur-setup.exe`.

L'assistant propose des valeurs modifiables pour le serveur et le modèle, crée la configuration si elle n'existe pas et conserve celle-ci lors d'une mise à niveau ou d'une désinstallation. Il sépare le réglage d'affichage en arrière-plan de la création du raccourci dans le dossier de démarrage Windows. Si Ollama n'est pas détecté, il demande avant de télécharger et lancer l'installateur officiel. Le modèle lui-même doit ensuite être téléchargé séparément avec `ollama pull <modèle>`.

Le même `AppId` doit être conservé entre les versions : Inno Setup reconnaît ainsi l'installation existante, réutilise son dossier et met les fichiers à jour sans désinstallation préalable. Les mutex de l'application et du programme d'installation empêchent les exécutions concurrentes.

L'installateur et l'exécutable ne sont pas encore signés. Une alerte SmartScreen est donc possible jusqu'à l'ajout d'un certificat de signature de code.

## Utilisation de l'exécutable
1. Copiez `.translator_config.example.json` en `dist/.translator_config.json` et adaptez le serveur et le modèle.
2. Pour un usage local, installez Ollama, téléchargez le modèle configuré et lancez `ollama serve`.
3. Double-cliquez sur `traducteur.exe`.

## Configuration obligatoire
Le fichier `.translator_config.json` doit définir `server_url`, `default_model`, les langues et les quatre prompts, puis être placé à côté de l'exécutable. S'il est absent, l'application demande de sélectionner une configuration valide.
Si le serveur exige une clé, renseignez `api_key` dans `.translator_config.json`. Ne partagez pas ce fichier avec une vraie clé.
