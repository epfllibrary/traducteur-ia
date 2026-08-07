# Traducteur 1.0 - Interface Moderne

Une interface moderne et intuitive pour la traduction de texte utilisant des modèles d'IA locaux ou distants via une API compatible Ollama.

## 🖼️ Aperçu

![Aperçu de l'interface du Traducteur 1.0](img/Exemple_interface.png)

## 🤖 Principe de fonctionnement

Cette application fournit l'interface de traduction, mais n'embarque pas elle-même de grand modèle de langage (LLM). Elle envoie le texte au modèle défini dans `.translator_config.json` :

- **LLM local** : Ollama et le modèle fonctionnent sur votre ordinateur. Les textes restent sur la machine, mais les performances dépendent de son processeur, de sa mémoire et éventuellement de sa carte graphique.
- **LLM distant** : le modèle fonctionne sur un autre serveur accessible par le réseau. Configurez alors son adresse et, si nécessaire, sa clé API.

Dans les deux cas, le serveur doit proposer une API compatible Ollama. L'application ne télécharge et ne démarre pas le modèle automatiquement. Pour installer Ollama, lancer un premier modèle ou comprendre son API, consultez le [guide de démarrage officiel](https://docs.ollama.com/quickstart) et la [documentation de l'API Ollama](https://docs.ollama.com/api/introduction).

## 🚀 Démarrage rapide sous Windows

L'utilisation de l'exécutable fourni est la méthode recommandée. Python et les dépendances du projet ne sont pas nécessaires.

1. Téléchargez [`dist/traducteur.exe`](dist/traducteur.exe).
2. Téléchargez [`.translator_config.example.json`](.translator_config.example.json), copiez-le dans le même dossier que l'exécutable et renommez la copie en `.translator_config.json`.
3. Ouvrez `.translator_config.json` dans un éditeur de texte et adaptez au minimum `server_url` et `default_model`. Renseignez aussi `api_key` si le serveur distant en exige une.
4. Si le modèle est local, installez Ollama, téléchargez le modèle configuré et démarrez Ollama.
5. Lancez `traducteur.exe`.

Le dossier utilisé doit donc contenir au minimum :

```text
Traducteur/
├── traducteur.exe
└── .translator_config.json
```

> **Configuration obligatoire :** l'exécutable n'intègre volontairement aucune adresse de serveur ni clé API. Si `.translator_config.json` n'est pas placé à côté de l'exécutable, l'application demandera de sélectionner un fichier de configuration à chaque démarrage.

Pour un serveur local Ollama, `server_url` peut rester sur `http://localhost:11434/api/chat`. Pour un serveur distant, remplacez cette adresse et vérifiez les paramètres d'authentification avant de lancer l'application. Ne publiez jamais le fichier `.translator_config.json` contenant vos réglages réels.

## ✨ Fonctionnalités

### Interface Moderne
- **Design professionnel** : Interface inspirée de DeepL avec CustomTkinter
- **Thème moderne** : Couleurs et polices optimisées pour une expérience utilisateur fluide
- **Layout équilibré** : Division 50/50 des zones de texte source et traduction
- **Mode veille** : La croix masque la fenêtre, l'application reste active en arrière-plan
- **System Tray** : L'application reste active en arrière-plan dans la barre des tâches
- **Raccourcis globaux** : Double Ctrl+C ou Ctrl+Shift+C pour afficher la fenêtre et traduire automatiquement le presse-papier

### Traduction Avancée
- **Streaming en temps réel** : Affichage progressif de la traduction
- **Modes multiples** : Traduction, réécriture, emails professionnels
- **Action contextuelle** : Le bouton principal reprend automatiquement le mode sélectionné (`Traduire`, `Réécrire` ou `E-mail`)
- **Copie rapide** : Bouton `Copier` pour envoyer la traduction dans le presse-papier
- **Inversion intelligente** : Le bouton d'inversion reprend la traduction comme nouveau texte source quand elle existe, puis relance la traduction automatiquement
- **Alternatives contextuelles** : Sélectionnez un mot ou une phrase dans la traduction pour afficher `Alternatives`; clic droit ou `Ctrl+L` restent disponibles
- **Liens préservés** : Les prompts demandent explicitement de conserver les liens, URL et destinations Markdown/HTML
- **Liens cliquables** : Les URL visibles et les liens HTML copiés depuis le presse-papiers restent cliquables; le Markdown est utilisé en interne pour préserver les liens pendant la traduction
- **Styles préservés** : Les titres `h1` à `h6`, le gras et l'italique du presse-papiers HTML sont conservés, transmis au modèle en Markdown puis rendus dans la traduction
- **Langues configurables** : 36 langues préconfigurées; français, anglais, allemand, italien, espagnol et portugais constituent la base obligatoire
- **Détection automatique** : Langue source détectée automatiquement

### Gestion de Fichiers
- **Import multi-formats** : Support pour .txt, .docx (Word), .pdf
- **Export rapide** : Sauvegarde des traductions
- **Historique intelligent** : 10 dernières traductions conservées

### Métriques & Performance
- **Compteur de mots** : Suivi en temps réel du nombre de mots
- **Chronomètre** : Mesure précise du temps de traduction
- **Threading optimisé** : Interface réactive pendant la traduction

## ⚙️ Configuration et utilisation

### Configuration locale avec Ollama
1. Installez Ollama en suivant le [guide officiel](https://docs.ollama.com/quickstart).
2. Téléchargez un modèle, par exemple : `ollama pull ministral-3:3b`
3. Lancez le serveur: `ollama serve`

`ministral-3:3b` n'est qu'un exemple actuel de petit modèle multilingue adapté à une exécution locale; l'application ne l'impose pas. Il appartient à la même catégorie 3B que `llama3.2:3b`, mais son téléchargement Ollama est un peu plus volumineux (environ 3 Go contre 2 Go). `qwen3:4b` constitue également une alternative multilingue compacte. La qualité varie selon les langues, les textes et le matériel : comparez idéalement quelques traductions représentatives avant de fixer `default_model`.

Utilisez un tag de taille explicite, comme `ministral-3:3b`, plutôt que `ministral-3:latest` : le tag `latest` peut désigner une variante plus lourde et évoluer ultérieurement. Consultez les fiches Ollama de [Ministral 3](https://ollama.com/library/ministral-3), [Llama 3.2](https://ollama.com/library/llama3.2) et [Qwen 3](https://ollama.com/library/qwen3) pour vérifier les variantes disponibles.

### Configuration de l'application
La connexion à un modèle local ou distant se configure obligatoirement dans `.translator_config.json`. Les champs `server_url`, `default_model` (ou son ancien alias `model`), `languages` et les quatre prompts `traduire`, `réécrire`, `email` et `lookup` sont requis.

L'application cherche automatiquement ce fichier dans cet ordre :
- le chemin défini par la variable d'environnement `TRANSLATOR_CONFIG` ;
- le dossier du script ou de l'exécutable ;
- le dossier courant.

Si aucun fichier n'est trouvé, un sélecteur demande de choisir une configuration JSON. L'application ne démarre pas si la sélection est annulée ou si le fichier est invalide. Pour éviter de le sélectionner à chaque lancement, placez-le à côté du script ou de l'exécutable, ou définissez `TRANSLATOR_CONFIG`.

Exemple :
```json
{
  "server_url": "http://localhost:11434/api/chat",
  "api_key": "",
  "api_key_header": "Authorization",
  "think": false,
  "hide_window_on_start": false,
  "default_model": "ministral-3:3b",
  "_comment_languages": "auto et les langues fr, en, de, it, es et pt sont obligatoires. Les autres langues peuvent être ajoutées, modifiées ou supprimées.",
  "languages": {
    "auto": "Auto",
    "fr": "Français",
    "en": "Anglais",
    "de": "Allemand",
    "it": "Italien",
    "es": "Espagnol",
    "pt": "Portugais"
  },
  "prompts": {
    "traduire": "Tu es un traducteur professionnel. Traduis le texte suivant de {source_language} vers {target_language}.\n\nContraintes:\n- Préserve fidèlement le sens, le ton, la mise en forme et les sauts de ligne.\n- Préserve tous les liens, URL et destinations Markdown/HTML exactement tels qu'ils apparaissent.\n- Préserve les titres et leurs niveaux, le gras, l'italique et leurs marqueurs Markdown/HTML.\n- N'ajoute aucune explication, note ou variante.\n- Si la langue source vaut Auto, détecte-la naturellement.\n\nTexte:\n{text}",
    "réécrire": "Tu es un réviseur éditorial franc, précis et naturel. Réécris le texte suivant en {target_language}.\n\nObjectif:\n- Améliorer la clarté, la fluidité, le style et la correction.\n- Conserver l'intention, les informations importantes et le niveau de formalité.\n- Préserver tous les liens, URL et destinations Markdown/HTML exactement tels qu'ils apparaissent.\n- Préserver les titres et leurs niveaux, le gras, l'italique et leurs marqueurs Markdown/HTML.\n- Ne pas rendre le texte artificiel ni trop emphatique.\n- Répondre uniquement avec la version réécrite.\n\nTexte:\n{text}",
    "email": "Tu es un assistant de rédaction spécialisé dans les e-mails professionnels. Transforme le texte suivant en e-mail en {target_language}.\n\nStyle attendu:\n- Cordial, professionnel, fluide et humain.\n- Naturel, direct, sans tournures trop typiques de l'IA.\n- Poli sans être excessivement formel.\n- Structure claire avec salutation et formule de clôture si pertinent.\n- Préserver tous les liens, URL et destinations Markdown/HTML exactement tels qu'ils apparaissent.\n- Préserver les titres et leurs niveaux, le gras, l'italique et leurs marqueurs Markdown/HTML.\n- Répondre uniquement avec l'e-mail final.\n\nTexte:\n{text}",
    "lookup": "Tu es un assistant terminologique pour la traduction et la réécriture. Propose des alternatives naturelles pour le segment sélectionné, en tenant compte du contexte.\n\nContraintes:\n- Propose 5 à 8 alternatives utiles dans la langue du segment sélectionné.\n- Explique très brièvement la nuance ou le contexte d'usage de chaque alternative.\n- Si une alternative change le registre, indique-le.\n- Ne réécris pas tout le texte.\n- Réponds en français, sauf pour les alternatives elles-mêmes.\n\nLangue source: {source_language}\nLangue cible: {target_language}\n\nTexte source:\n{text}\n\nTraduction actuelle:\n{translation}\n\nSegment sélectionné:\n{selection}"
  }
}
```

`server_url` peut désigner un serveur local ou distant compatible avec l'API Ollama. Il accepte aussi l'URL de base du serveur, par exemple `http://localhost:11434`; l'application ajoutera `/api/chat`.
La clé historique `model` reste acceptée, mais `default_model` est préférée pour 1.0.
La liste des modèles est chargée dynamiquement depuis l'endpoint Ollama `/api/tags`. Si cet appel échoue, seul `default_model` est proposé; aucune clé `models` n'est nécessaire.
Si `api_key` est renseignée, elle est envoyée avec chaque requête. Par défaut l'en-tête est `Authorization: Bearer <api_key>`. Pour un endpoint qui attend un autre en-tête, mettez par exemple `"api_key_header": "X-API-Key"`.
`think` est désactivé par défaut car la traduction bénéficie surtout d'une réponse directe et rapide. Mettez `"think": true` seulement si vous voulez explicitement activer le raisonnement des modèles compatibles.
`hide_window_on_start` permet de lancer l'application directement en arrière-plan. L'alias français `masquer_fenetre_au_lancement` est aussi accepté.
Les prompts utilisent les variables `{source_language}`, `{target_language}` et `{text}`. Le prompt `lookup` peut aussi utiliser `{translation}` et `{selection}`. Les clés anglaises `translate` et `rewrite` restent acceptées.
Tous les textes de prompt proviennent du fichier JSON : aucun prompt de repli n'est intégré dans `translate.py`.
`languages` associe chaque code affiché dans l'interface au libellé injecté dans les prompts. Les codes utilisent de préférence le format ISO 639-1 (`fr`, `en`, `de`, etc.). `auto` est réservé à la détection automatique de la langue source.

`auto`, `fr`, `en`, `de`, `it`, `es` et `pt` sont obligatoires. Les autres entrées peuvent être ajoutées, renommées ou supprimées. Par exemple, ajoutez `"ca": "Catalan"` pour proposer le catalan. Le fichier `.translator_config.example.json` contient la liste préconfigurée complète.

Le JSON standard ne prenant pas en charge les commentaires, `_comment_languages` sert de note documentaire et est ignorée par l'application.
Ne commitez pas `.translator_config.json` avec une vraie clé API ; ce fichier est ignoré par Git.

### Import de fichiers
- **Texte (.txt)** : Support natif UTF-8
- **Word (.docx)** : Extraction automatique du texte
- **PDF** : Extraction du texte incorporé avec `pdfplumber` (sans OCR)

### Mise en forme depuis le presse-papiers
Lorsque du contenu rendu est copié depuis un navigateur ou une application compatible HTML, l'application reconnaît les titres (`h1` à `h6`), le gras et l'italique provenant des balises (`strong`, `b`, `em`, `i`), des styles en ligne et des classes CSS définies dans une balise `style`. Les niveaux de titre sont transmis au modèle avec les marqueurs Markdown `#` à `######`, puis rendus avec une taille adaptée dans l'interface. Le code HTML copié comme simple texte n'est pas interprété : il faut copier le résultat affiché par le navigateur.

### Mode veille et raccourcis globaux
- Cliquer sur la croix masque la fenêtre sans arrêter l'application.
- Double Ctrl+C réaffiche la fenêtre, récupère le presse-papier et lance la traduction automatiquement.
- Ctrl+Shift+C conserve le même comportement de traduction automatique du presse-papier.
- Le menu **Fichier > Quitter** ou **Quitter** depuis le tray ferme réellement l'application.

## 🏗️ Architecture

### Technologies
- **Tkinter/CustomTkinter** : Interface graphique
- **Threading** : Traduction asynchrone
- **Queue** : Communication thread-safe
- **Requests** : appels à une API HTTP compatible Ollama, locale ou distante

### Structure du code
- `TranslatorApp` : Classe principale gérant l'interface
- Méthodes thread-safe pour les mises à jour d'interface
- Gestion d'erreurs robuste et messages utilisateur informatifs

## 📦 Déploiement

### ⚠️ **Important : Cross-compilation**

**Un exécutable créé sur Linux ne fonctionne pas sur Windows !**
PyInstaller crée des binaires spécifiques à l'architecture et au système d'exploitation.

### Création d'un exécutable Windows

#### Solution recommandée : Compiler sur Windows natif
```cmd
REM Sur Windows, ouvrir PowerShell/Command Prompt
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --name traducteur translate.py
```

#### Scripts automatisés
- `scripts/build_windows.ps1` : Script PowerShell (recommandé)
- `scripts/build_windows.bat` : Script batch pour cmd

#### Utilisation des scripts
```cmd
REM Télécharger/cloner le projet sur Windows
REM Ouvrir PowerShell en tant qu'administrateur
.\scripts\build_windows.ps1
```

### Distribution
- **Exécutable inclus** : `dist/traducteur.exe` (~40-50 Mo)
- **Test sans environnement de dev** : sur Windows, récupérez le dossier `dist/` depuis le dépôt, puis lancez `traducteur.exe`.
- **Python non requis** : l'exécutable est autonome ; il n'est pas nécessaire d'installer Python, pip ou les dépendances du projet.
- **Dépendances externes** : Ollama doit être installé séparément uniquement si le modèle est exécuté localement
- **Compatibilité** : L'exécutable est spécifique au système d'exploitation

Avant de distribuer l'application, copiez `.translator_config.example.json` en `.translator_config.json` dans le dossier `dist/`, puis adaptez le serveur et le modèle. Sans ce fichier, l'exécutable demandera à l'utilisateur d'en sélectionner un. Le fichier `.translator_config.json` local n'est pas versionné afin d'éviter de publier des clés ou des réglages internes.

#### Alternatives si pas d'accès Windows
- **Auto Py to Exe** : Interface graphique locale pour créer des exe sur Windows
- **IT Guide** : `docs/IT_GUIDE.md` pour expliquer à votre équipe IT

### Scripts de build
- `scripts/build_windows.ps1` : PowerShell (recommandé)
- `scripts/build_windows.bat` : Command prompt
- `docs/BUILD_INSTRUCTIONS.md` : Guide détaillé

#### Services en ligne
- **Auto Py to Exe** : Interface graphique locale sur Windows
- **GitHub Actions** : CI/CD pour compilation multi-plateforme

### Optimisations PyInstaller
- `--onefile` : Exécutable unique
- `--windowed` : Pas de console (interface graphique uniquement)
- `--name` : Nom personnalisé de l'exécutable

## 🔧 Dépannage

### Problèmes courants
- **"Connexion refusée"** : Vérifiez l'adresse `server_url` et l'accessibilité du serveur ; en local, vérifiez qu'Ollama est lancé (`ollama serve`)
- **"Module non trouvé"** : Installez les dépendances avec `pip install -r requirements.txt`
- **"Erreur d'encodage"** : Les fichiers PDF/Word doivent contenir du texte extractible
- **Double Ctrl+C sans effet** : Vérifiez que `pynput` est installé et relancez l'application après installation

### Support fichiers
- **PDF** : Nécessite `pdfplumber` pour l'extraction de texte
- **DOCX** : Nécessite `python-docx` pour la lecture Word
- **TXT** : Support UTF-8 natif

## 📋 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique complet des versions.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou proposer une pull request.

## 🛠️ Développement depuis les sources (optionnel)

Cette section concerne les personnes qui souhaitent modifier ou reconstruire l'application. Pour une utilisation normale sous Windows, privilégiez l'exécutable présenté au début du README.

### Prérequis de développement

- **Python 3.8+**
- **Un accès à une API compatible Ollama**, locale ou distante
- Pour une utilisation locale : **Ollama** installé avec le modèle de votre choix

### Installation des dépendances

```bash
pip install -r requirements.txt
```

Les composants facultatifs peuvent aussi être installés séparément :

```bash
pip install customtkinter  # Interface moderne
pip install pystray pillow # System tray
pip install pynput         # Raccourcis globaux
pip install pdfplumber python-docx  # Support fichiers PDF/Word
```

### Lancement depuis les sources

```bash
python translate.py
```

La configuration `.translator_config.json` reste obligatoire et doit être placée à côté de `translate.py`, sélectionnée au démarrage ou indiquée avec `TRANSLATOR_CONFIG`.

### Structure du dépôt

- `translate.py` : application principale actuelle.
- `requirements.txt` : dépendances Python de la version 1.0.
- `.translator_config.example.json` : modèle de configuration sans secret.
- `img/` : captures d'écran utilisées dans la documentation.
- `scripts/` : scripts de build Windows.
- `docs/` : guides détaillés et documentation complémentaire.

## Réalisation

Ce projet a été réalisé avec l'aide de l'IA ChatGPT 5.5 et mené par :

Sylvain Vuilleumier  
Documentary engineering specialist -- EPFL  
sylvain.vuilleumier@epfl.ch

## 📄 Licence

GNU General Public License v3.0 or later (GPL-3.0-or-later). Voir le fichier [LICENSE](LICENSE) pour plus de détails.
