# Déploiement et dépannage sous Windows

## Installer et distribuer

Pour une utilisation normale, téléchargez `traducteur-setup.exe` depuis le [dépôt officiel](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/raw/main/bin/traducteur-setup.exe?inline=false) ou les [releases](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/releases), puis suivez l'assistant. Aucun Python n'est nécessaire sur le poste utilisateur.

Traducteur s'installe pour l'utilisateur courant sous Windows 10/11 x64. Le profil EPFL configure RCP ; les utilisateurs externes choisissent **Autre serveur**, avec Ollama ou OpenAI/vLLM. Le modèle Ollama proposé est `ministral-3:3b`. Le service distant ou local et le modèle doivent être accessibles pour traduire.

Ne distribuez que l'installateur. `bin/traducteur.exe` est un artefact de construction interne. Les paramètres de lancement automatique et d'affichage masqué sont indépendants. Le menu Démarrer contient aussi le désinstalleur.

## Compiler sous Windows

Depuis PowerShell, à la racine du projet :

```powershell
.\scripts\build_windows.ps1
.\scripts\build_installer.ps1
```

Installez Python 3.11+ et Inno Setup 6 sur cette machine, avec un accès Internet pour les dépendances et l'audit. Les scripts créent un environnement isolé dans `build/venv-windows` et refusent la compilation si `pip check` ou `pip-audit` échoue. Voir le [guide de compilation](BUILD_INSTRUCTIONS.md).

PyInstaller produit un binaire pour le système sur lequel son interpréteur s'exécute. Un build Python Linux ne produit pas un exécutable Windows. Une machine ou une VM Windows convient ; depuis WSL, il faut utiliser un interpréteur **Windows**. Les scripts PowerShell et batch sont destinés à Windows. Il n'y a pas de procédure Docker de compilation croisée prise en charge dans ce projet.

## Configuration et mise à jour

L'assistant crée `.translator_config.json` à côté de l'application. L'utilisateur peut ensuite ouvrir un autre JSON complet par **Fichier > Ouvrir une configuration...**, ou modifier celui qui est actif par **Fichier > Modifier la configuration...**. Le nom actif reste affiché ; les textes sont conservés lors d'une bascule. Le dernier chemin choisi est prioritaire au prochain démarrage.

Les fichiers locaux sont :

- `.translator_config.json`, ou un autre fichier choisi : serveur, clé API, langues et consignes ;
- `.translator_state.json`, dans le dossier de la configuration active : dernier modèle utilisé et taille de l'interface ;
- `.translator_preferences.json`, dans le dossier de l'application : chemin de la dernière configuration.

Le désinstalleur peut supprimer les fichiers internes de l'installation si l'utilisateur le choisit. Les configurations nommées ou placées dans d'autres dossiers ne sont pas supprimées automatiquement. Une réinstallation propose de conserver les réglages. Avant un déploiement institutionnel, sauvegardez les configurations nécessaires sans exposer leurs clés API.

## Dépannage

| Symptôme | Vérification |
| --- | --- |
| Windows refuse le lancement | Utiliser le build Windows x64 et vérifier la provenance du setup |
| Alerte SmartScreen ou éditeur inconnu | Le projet n'est pas encore signé ; ne poursuivre qu'après vérification de la provenance |
| Connexion refusée | Vérifier `server_url`, le réseau et le service ; avec Ollama local, vérifier `ollama list` |
| Modèle inattendu | Vérifier le fichier actif et le dernier modèle sélectionné ; le défaut Ollama proposé est `ministral-3:3b` |
| Configuration introuvable au lancement | Sélectionner un fichier valide ; le dernier chemin mémorisé est devenu inaccessible |
| Bas de fenêtre ou texte trop petit | Utiliser **Affichage > Taille de l'interface** ; la taille initiale tient compte du zoom et de l'écran |
| La croix ne ferme pas l'application | Utiliser **Fichier > Quitter** ou **Quitter** depuis l'icône près de l'horloge |
| PDF importé vide | Le document doit contenir du texte extractible ; aucune reconnaissance OCR n'est intégrée |
| Dépendance manquante dans un build | Reconstruire dans l'environnement isolé avec `requirements.txt`, puis reconstruire le setup |

## Téléchargement d'une version

La [procédure de release](RELEASE.md) décrit le tag versionné et le lien permanent vers le setup de la dernière release. Les archives de code source générées par GitLab ne sont pas des installateurs Windows.
