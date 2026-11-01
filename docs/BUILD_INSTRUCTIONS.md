# Compiler Traducteur pour Windows

## Prérequis

La machine de construction nécessite Windows 10/11 x64, Python 3.11+, Inno Setup 6 et un accès Internet pour les dépendances et l'audit. Les utilisateurs du setup n'ont pas besoin de Python. Conservez l'arborescence complète du dépôt, notamment `LICENSE`, `requirements.txt`, `scripts/`, `installer/` et `.translator_config.example.json`.

Les scripts s'exécutent depuis une session Windows. Depuis WSL, utilisez un interpréteur Python Windows ; un interpréteur Linux produit un binaire Linux. Aucun build Linux/Ubuntu n'est distribué actuellement.

## Construire l'exécutable puis le setup

Depuis PowerShell, à la racine du dépôt :

```powershell
.\scripts\build_windows.ps1
.\scripts\build_installer.ps1
```

Depuis CMD, le premier script peut être remplacé par `scripts\build_windows.bat`. Le script de l'installateur reste un script PowerShell. Inno Setup 6 peut être installé avec `winget install --id JRSoftware.InnoSetup -e`.

Le premier script crée `build/venv-windows`, met à jour les dépendances et PyInstaller, exécute `pip check` puis `pip-audit`, et construit `bin/traducteur.exe`. Une incompatibilité ou une vulnérabilité connue bloque ce script. Le second script intègre cet exécutable dans `bin/traducteur-setup.exe`. Il faut exécuter les deux : le premier ne reconstruit pas automatiquement le setup.

Les scripts embarquent le fichier `LICENSE` avec `--add-data "../LICENSE:."`. Le chemin source est relatif au dossier `build` du fichier `.spec`. La licence complète est ainsi accessible hors ligne dans **Aide > À propos...**.

Les sorties font environ 45 Mo, selon les dépendances. Seul `bin/traducteur-setup.exe` est destiné à la distribution et suivi par Git. Une modification de code, de dépendances ou de version exige de reconstruire l'exécutable puis le setup.

## Vérifier avant distribution

```powershell
python -m unittest discover -s tests
git diff --check
```

Vérifiez aussi la fenêtre Windows, les menus, les raccourcis et la bascule de configuration. Les versions de `APP_VERSION` dans `translate.py`, `MyAppVersion` dans `installer/traducteur.iss`, `VersionInfoVersion`, le README et les bannières de construction doivent correspondre. Pour 1.2.0, la version Windows est `1.2.0.0` et le tag prévu est `v1.2.0`.

Le script `python scripts/prepare_release.py` prépare les notes, l'empreinte du setup et le JSON de publication localement. La [procédure de release](RELEASE.md) décrit ensuite le commit, le tag et la publication GitLab.

## Assistant d'installation

L'installation est faite pour l'utilisateur courant. L'assistant distingue l'environnement EPFL/RCP d'un autre serveur Ollama ou OpenAI/vLLM. Il crée `.translator_config.json` et permet de régler les URL exactes, le modèle, la clé API et les options de démarrage.

Ollama local propose `ministral-3:3b`. La préparation facultative peut télécharger Ollama, démarrer le service et télécharger le modèle manquant. Le profil EPFL propose `swiss-ai/Apertus-v1.5-8B` ; une clé personnelle RCP est nécessaire. Les deux services sont décrits dans le [README](../README.md).

Conservez le même `AppId` entre versions. Une installation existante est détectée et peut être réinstallée ou désinstallée, avec conservation facultative des réglages. Les mutex empêchent plusieurs instances ; l'assistant peut demander la fermeture de l'application. Le désinstalleur est également disponible dans le menu Démarrer.

## Sécurité et mises à jour d'Ollama

Le téléchargement d'Ollama utilise une URL versionnée et un SHA-256 vérifié avant exécution. Lors d'une mise à jour, modifier ensemble `OllamaSetupURL` et `OllamaSetupSHA256` dans `installer/traducteur.iss`, à partir de `sha256sum.txt` de la [publication officielle](https://github.com/ollama/ollama/releases).

L'exécutable et l'installateur ne sont pas encore signés. Une alerte Windows/SmartScreen est possible ; voir le [guide de déploiement](DEPLOY_WINDOWS.md).

## Dépannage de construction

- **Python introuvable** : installer Python 3.11+ et vérifier son accès dans le terminal Windows.
- **Script PowerShell bloqué** : utiliser une politique d'exécution autorisée par votre organisation ; aucune session administrateur n'est requise pour construire Traducteur dans un dossier utilisateur.
- **Fichier introuvable** : récupérer tout le dépôt et conserver les chemins relatifs.
- **Audit en échec** : examiner les dépendances signalées et reconstruire après correction.
- **Inno Setup introuvable** : l'installer ou utiliser le paramètre `-InnoCompiler` de `build_installer.ps1`.

## Exécuter l'artefact interne pour un essai

Copiez `.translator_config.example.json` en `bin/.translator_config.json` et adaptez les paramètres avant de lancer `bin/traducteur.exe`. Un autre fichier complet peut être choisi au démarrage ou par **Fichier > Ouvrir une configuration...**. Le dernier chemin choisi est mémorisé. Ne distribuez pas les configurations contenant des clés API.
