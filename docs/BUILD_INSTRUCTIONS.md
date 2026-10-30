# Instructions pour créer l'exécutable Windows

## Problèmes résolus
- ❌ Caractères spéciaux (accents, emojis) causaient des erreurs d'encodage
- ❌ Script .bat ne trouvait pas requirements.txt
- ✅ Scripts corrigés avec caractères ASCII simples
- ✅ Vérification explicite du fichier requirements.txt

## Utilisation

Python 3.11 minimum est requis pour les versions corrigées de Pillow. Les scripts
créent un environnement isolé dans `build/venv-windows`, actualisent les dépendances,
vérifient leur compatibilité avec `pip check` et lancent `pip-audit` sur les paquets
installés avant PyInstaller. Une vulnérabilité connue ou un échec de l'audit bloque
la compilation ; un accès Internet est nécessaire pour cette vérification.

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
- Dossier `bin/` créé avec `traducteur.exe`
- Taille approximative : 50 Mo
- Exécutable standalone (pas besoin de Python sur le système cible)

## Création de l'installateur guidé

Après avoir créé `bin/traducteur.exe` :

1. Installez [Inno Setup 6](https://jrsoftware.org/isinfo.php), ou exécutez `winget install --id JRSoftware.InnoSetup -e`.
2. Lancez `.\scripts\build_installer.ps1` depuis PowerShell.
3. Récupérez `bin\traducteur-setup.exe`. C'est le seul fichier destiné à être publié.

L'assistant demande d'abord de choisir entre l'environnement EPFL/RCP et un autre serveur. Pour un autre serveur, il propose ensuite Ollama ou OpenAI/vLLM, puis préremplit directement les URL exactes d'inférence et de modèles; elles restent modifiables. Une installation existante est recherchée dans le registre et dans le dossier par défaut; l'utilisateur choisit entre réinstaller et désinstaller, avec une case indépendante pour conserver la configuration et le dernier modèle utilisé. Une instance active peut être arrêtée automatiquement après confirmation. L'assistant ajoute au menu Démarrer un raccourci vers le désinstalleur, qui demande à son tour si les données utilisateur doivent être supprimées. Il sépare le réglage d'affichage en arrière-plan de la création du raccourci dans le dossier de démarrage Windows. Avec Ollama local, `ministral-3:3b` est proposé par défaut. Si Ollama est absent, l'assistant affiche la progression de son téléchargement avant de lancer l'installateur officiel. Il démarre ensuite le service s'il ne répond pas déjà et exécute `ollama pull` avec sa progression visible lorsque le modèle manque.

Le profil **EPFL (Service RCP)** préconfigure `https://inference.rcp.epfl.ch/v1/chat/completions`, `https://inference.rcp.epfl.ch/v1/models` et le modèle `swiss-ai/Apertus-v1.5-8B`. Une clé doit être créée lors de la première utilisation sur [portal.rcp.epfl.ch/aiaas/keys](https://portal.rcp.epfl.ch/aiaas/keys). RCP étant réservé aux membres de l'EPFL, les utilisateurs externes doivent choisir **Autre serveur**.

Le même `AppId` doit être conservé entre les versions : Inno Setup et la détection explicite reconnaissent ainsi l'installation existante. Les mutex empêchent plusieurs instances de l'application ou de l'installateur; l'installateur gère lui-même la fermeture de l'application.

L'installateur et l'exécutable ne sont pas encore signés. Une alerte SmartScreen est donc possible jusqu'à l'ajout d'un certificat de signature de code.

Le téléchargement automatique d'Ollama utilise une URL versionnée et vérifie son
SHA-256 avant toute exécution. Pour actualiser Ollama, modifier ensemble
`OllamaSetupURL` et `OllamaSetupSHA256` dans `installer/traducteur.iss`, à partir du
fichier `sha256sum.txt` de la [publication officielle](https://github.com/ollama/ollama/releases).
Ne pas remplacer l'URL par une adresse « latest » sans mettre à jour l'empreinte.

Après une mise à jour de sécurité, reconstruire d'abord `traducteur.exe`, puis
`traducteur-setup.exe` : modifier `requirements.txt` ne corrige pas les exécutables
déjà générés ou installés.

## Utilisation de l'exécutable
1. Copiez `.translator_config.example.json` en `bin/.translator_config.json` et adaptez le serveur et le modèle.
2. Pour un usage local manuel, installez Ollama, téléchargez le modèle configuré et lancez `ollama serve` uniquement si le service n'est pas déjà actif.
3. Double-cliquez sur `traducteur.exe`.

## Configuration obligatoire
Le fichier `.translator_config.json` doit définir `server_url`, les langues et les quatre prompts, puis être placé à côté de l'exécutable. S'il est absent, l'application demande de sélectionner une configuration valide.
`server_url` doit contenir l'endpoint complet : l'application l'utilise sans ajouter `/api/chat`. `default_model` est facultatif si `models_url` est renseignée; au moins l'une de ces deux valeurs est nécessaire.
Utilisez `"api_format": "openai"` pour un endpoint vLLM `/v1/chat/completions`, ou `"api_format": "ollama"` pour `/api/chat`.
Si le serveur exige une clé, renseignez `api_key` dans `.translator_config.json`. Ne partagez pas ce fichier avec une vraie clé.
