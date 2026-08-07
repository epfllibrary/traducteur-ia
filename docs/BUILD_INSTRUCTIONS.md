# Instructions pour créer l'exécutable Windows

## Problèmes résolus
- ❌ Caractères spéciaux (accents, emojis) causaient des erreurs d'encodage
- ❌ Script .bat ne trouvait pas requirements.txt
- ✅ Scripts corrigés avec caractères ASCII simples
- ✅ Vérification explicite du fichier requirements.txt

## Utilisation

### Sur Windows avec PowerShell (Recommandé)
1. Copiez tous les fichiers du projet sur Windows
2. Ouvrez PowerShell en tant qu'administrateur
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

## Utilisation de l'exécutable
1. Copiez `.translator_config.example.json` en `dist/.translator_config.json` et adaptez le serveur et le modèle.
2. Pour un usage local, installez Ollama, téléchargez le modèle configuré et lancez `ollama serve`.
3. Double-cliquez sur `traducteur.exe`.

## Configuration obligatoire
Le fichier `.translator_config.json` doit définir `server_url`, `default_model`, les langues et les quatre prompts, puis être placé à côté de l'exécutable. S'il est absent, l'application demande de sélectionner une configuration valide.
Si le serveur exige une clé, renseignez `api_key` dans `.translator_config.json`. Ne partagez pas ce fichier avec une vraie clé.
