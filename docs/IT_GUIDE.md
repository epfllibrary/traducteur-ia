# Guide IT : déployer Traducteur

## Installer sur un poste

Distribuez uniquement `traducteur-setup.exe`, depuis le [téléchargement direct du dépôt](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/raw/main/bin/traducteur-setup.exe?inline=false) ou une [release publiée](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/releases). Python et les dépendances ne sont pas nécessaires sur les postes utilisateurs.

L'installateur cible Windows 10/11 x64 et installe l'application pour l'utilisateur courant, sans élévation administrative requise pour Traducteur. Une installation séparée d'Ollama peut avoir ses propres exigences.

L'assistant propose :

- **EPFL (Service RCP)** : endpoints RCP, modèle initial `swiss-ai/Apertus-v1.5-8B` et clé API de l'utilisateur ;
- **Autre serveur / Ollama** : endpoints locaux et modèle initial `ministral-3:3b`, avec préparation locale facultative ;
- **Autre serveur / OpenAI/vLLM** : endpoints exacts et identifiants du service choisi.

Le choix d'afficher la fenêtre au lancement est indépendant du raccourci de démarrage automatique. En cas de réinstallation, l'assistant propose de conserver les réglages. Il peut demander l'arrêt d'une instance active. Le désinstalleur demande si les données locales gérées dans le dossier de l'application doivent aussi être supprimées ; les configurations choisies dans d'autres dossiers restent à leur emplacement.

## Préparer plusieurs configurations

Créez des copies complètes de `.translator_config.example.json`, par exemple `EPFL.json` et `Ollama.json`. Chaque utilisateur peut les ouvrir par **Fichier > Ouvrir une configuration...**. Le nom du fichier actif est visible et son chemin est mémorisé automatiquement. Le choix est individuel ; il n'y a pas de registre de profils à éditer manuellement.

La clé API est stockée en clair dans le JSON. Protégez les droits d'accès et les sauvegardes. Ne distribuez pas de clé personnelle dans une configuration commune. Les consignes, les langues et les endpoints sont des paramètres de confiance : vérifiez les fichiers distribués.

## Construire l'installateur

Utilisez une machine Windows ou un interpréteur Python Windows accessible depuis WSL. Depuis la racine du dépôt, dans PowerShell :

```powershell
.\scripts\build_windows.ps1
.\scripts\build_installer.ps1
```

La machine de compilation nécessite Python 3.11+, Internet et Inno Setup 6. Les dépendances sont isolées, mises à jour et auditées avant PyInstaller. L'exécutable interne puis l'installateur font environ 45 Mo ; la taille varie selon les dépendances.

Voir les [instructions complètes](BUILD_INSTRUCTIONS.md), le [dépannage Windows](DEPLOY_WINDOWS.md) et la [publication d'une release](RELEASE.md).

## Distribution et protection des données

L'exécutable et l'installateur ne sont pas encore signés : une alerte Windows peut apparaître. Distribuez les fichiers depuis le projet officiel et vérifiez leur provenance. La construction échoue si l'audit détecte une vulnérabilité connue ; cela ne constitue pas une garantie d'absence de défaut.

Un serveur de modèles doit être accessible après installation. Avec Ollama local, l'assistant peut installer Ollama, démarrer le service et télécharger le modèle. L'application n'administre pas ensuite ce service. Avec un serveur distant, les textes sont transmis à l'endpoint configuré, sans anonymisation automatique. Vérifiez les règles de votre organisation avant ce type d'usage.
