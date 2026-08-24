# Architecture et développement

Ce guide rassemble les informations techniques destinées aux personnes qui souhaitent comprendre, modifier ou exécuter Traducteur depuis les sources. Pour une utilisation normale sous Windows, utilisez l'installateur indiqué dans le [README](../README.md).

## Architecture

- **Tkinter et CustomTkinter** : interface graphique.
- **Threading et Queue** : appels au modèle en arrière-plan et mises à jour sûres de l'interface.
- **Requests** : communication avec les API Ollama et OpenAI/vLLM, locales ou distantes.
- **Pystray et Pynput** : icône de notification et raccourcis clavier globaux.
- **Pdfplumber et Python-docx** : import de documents PDF et Word.

La classe `TranslatorApp` gère l'interface et les interactions utilisateur. La configuration, la validation des endpoints, les prompts et les adaptateurs d'API sont regroupés dans `translate.py`. Les appels réseau sont exécutés hors du thread graphique afin de conserver une interface réactive.

## Prérequis de développement

- Python 3.8 ou version ultérieure ;
- un accès à une API Ollama ou compatible OpenAI, locale ou distante ;
- Ollama et un modèle téléchargé si l'inférence doit fonctionner localement.

Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement depuis les sources

```bash
python translate.py
```

Le fichier de configuration de l'application (`.translator_config.json`) doit être placé à côté de `translate.py`, sélectionné au démarrage ou indiqué avec la variable d'environnement `TRANSLATOR_CONFIG`.

## Structure du dépôt

- `translate.py` : application principale ;
- `requirements.txt` : dépendances Python ;
- `.translator_config.example.json` : modèle de configuration sans secret ;
- `installer/` : script Inno Setup de l'installateur Windows ;
- `scripts/` : scripts de compilation ;
- `tests/` : tests automatisés ;
- `img/` : captures d'écran ;
- `docs/` : documentation complémentaire ;
- `bin/traducteur-setup.exe` : seul binaire destiné à la distribution.

## Compilation, déploiement et dépannage

- [Instructions de compilation](BUILD_INSTRUCTIONS.md)
- [Déploiement et dépannage sous Windows](DEPLOY_WINDOWS.md)
- [Guide destiné à l'IT](IT_GUIDE.md)
- [Fonctionnalités et limitations](FEATURES.md)

Un exécutable PyInstaller doit être produit sur le système d'exploitation cible. Pour Windows, les scripts fournis génèrent d'abord `bin/traducteur.exe` localement, puis l'intègrent à `bin/traducteur-setup.exe`. Seul l'installateur est suivi par Git et publié.

## Dépannage de développement

- **Module introuvable** : réinstallez les dépendances avec `pip install -r requirements.txt`.
- **Connexion refusée** : vérifiez l'endpoint exact dans `server_url` et, en local, le fonctionnement d'Ollama avec `ollama list`.
- **Raccourci global inactif** : vérifiez l'installation de `pynput` et les permissions d'accès au clavier.
- **Import PDF ou Word vide** : vérifiez que le document contient du texte extractible ; l'application n'effectue pas d'OCR.
