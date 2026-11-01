# Architecture et développement

Pour une utilisation sous Windows, utilisez l'installateur du [README](../README.md). Ce guide décrit le fonctionnement de Traducteur 1.2.0 depuis les sources.

## Architecture

`translate.py` contient la validation des configurations, les adaptateurs Ollama/OpenAI, les traitements de texte enrichi et la classe `TranslatorApp`. CustomTkinter fournit l'interface principale ; ttk est utilisé comme solution de repli. Pystray et Pynput assurent l'icône et les raccourcis globaux lorsque le système les prend en charge. Requests gère le réseau, Pdfplumber les PDF et Python-docx les documents Word.

Les requêtes de traduction, d'alternatives et de rafraîchissement des modèles utilisent des threads et une file de messages. Les mises à jour de widgets passent par le thread Tk. Le chargement initial de la liste des modèles s'effectue pendant l'initialisation de la fenêtre, avec un délai maximal réseau.

Chaque requête conserve un instantané du serveur, de ses identifiants et des paramètres utilisés. Une bascule de configuration invalide les anciennes générations de messages : leurs réponses tardives et leurs actions différées ne modifient plus la nouvelle configuration. L'arrêt d'affichage ne garantit pas l'annulation d'un calcul déjà reçu par le serveur distant.

## Lancer depuis les sources

Python 3.11 minimum est requis. Dans un environnement virtuel :

```bash
python -m pip install -r requirements.txt
python translate.py
```

Copiez `.translator_config.example.json` en `.translator_config.json`, à côté de `translate.py`, puis renseignez le serveur. Un sélecteur s'ouvre lorsqu'aucune configuration utilisable n'est disponible. Une API Ollama ou compatible OpenAI doit être accessible pour les traitements.

La distribution et les essais d'interface ciblent Windows 10/11 x64. Une exécution Linux depuis les sources dépend du bureau, de Tk et des permissions de clavier ; aucun paquet Ubuntu ni build Linux validé n'est fourni.

## Configurations et état utilisateur

Le fichier actif est chargé depuis le dernier chemin mémorisé, puis, en l'absence de préférence, depuis `.translator_config.json` près de l'exécutable ou de `translate.py`. Un chemin mémorisé devenu invalide ouvre le sélecteur au lieu de choisir un autre serveur automatiquement. **Fichier > Ouvrir une configuration...** valide un autre fichier avant la bascule.

Le JSON complet contient `api_format`, `server_url`, les langues et les quatre prompts. Au moins `default_model` ou `models_url` doit être renseigné. Les paramètres sont appliqués tels qu'ils sont configurés ; aucun endpoint n'est reconstruit implicitement. Les modèles sont lus dans `models[].name` pour Ollama ou `data[].id` pour OpenAI/vLLM.

- `.translator_preferences.json` conserve le dernier chemin choisi, près de l'application.
- `.translator_state.json` conserve le dernier modèle, son backend et le pourcentage d'interface, dans le dossier du fichier actif. Plusieurs configurations d'un même dossier partagent ce fichier ; le dernier modèle n'est restauré que si son backend correspond.
- Les fichiers d'état et les enregistrements de configuration utilisent un remplacement atomique. Les clés API restent dans les configurations JSON ; elles ne sont pas copiées dans les préférences de démarrage.
- Le fichier actif est surveillé chaque seconde. Une édition invalide laisse la dernière configuration valide en mémoire.

Les menus intégrés, les widgets CTk et les textes Tk suivent le pourcentage d'interface. CustomTkinter détecte la mise à l'échelle Windows ; la géométrie initiale est limitée à la zone disponible du moniteur, hors barre des tâches. Le réglage de 100 % représente la taille normale avec le DPI système.

## Structure du dépôt

| Chemin | Usage |
| --- | --- |
| `translate.py` | Application, adaptateurs d'API et interface |
| `requirements.txt` | Dépendances et versions minimales de sécurité |
| `.translator_config.example.json` | Configuration complète sans secret |
| `tests/` | Tests automatisés |
| `scripts/` | Compilation de l'exécutable et de l'installateur |
| `installer/traducteur.iss` | Assistant Windows Inno Setup |
| `docs/`, `img/` | Guides et capture d'écran |
| `bin/traducteur-setup.exe` | Binaire de distribution suivi par Git |
| `build/`, `bin/traducteur.exe` | Fichiers de travail et exécutable interne ignorés par Git |

## Vérifier et construire

Depuis la racine du projet :

```bash
python -m unittest discover -s tests
git diff --check
```

Les essais de l'interface Windows complètent les tests unitaires : presse-papier, menus, taille, changement de fichier et redémarrage. Les tests unitaires ne nécessitent pas de service de modèles réel.

Voir les [instructions de compilation](BUILD_INSTRUCTIONS.md), le [guide IT](IT_GUIDE.md), les [fonctionnalités](FEATURES.md), le [dépannage Windows](DEPLOY_WINDOWS.md) et la [publication d'une release](RELEASE.md).
