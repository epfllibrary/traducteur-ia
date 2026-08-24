# Changelog - Traducteur

## 1.1.0 (2026-08-24)

### Nouvelles fonctionnalités

- **API OpenAI/vLLM** : prise en charge de Chat Completions et Completions, du streaming SSE, des réponses non streamées et de la découverte des modèles via `/v1/models`.
- **Configuration modifiable et surveillée** : le menu `Fichier > Modifier la configuration...` permet d'éditer le JSON actif; les modifications externes valides rafraîchissent automatiquement l'interface sans redémarrage.
- **Choix de modèle simplifié** : `default_model` devient facultatif lorsqu'une URL de découverte est définie, et le dernier modèle réellement utilisé est restauré au lancement suivant.
- **Profil EPFL (Service RCP)** : configuration automatique des endpoints RCP, modèle initial `swiss-ai/Apertus-v1.5-8B` et validation de la clé API créée sur le portail RCP.
- **Parcours externe séparé** : les utilisateurs sans accès RCP choisissent Ollama ou leur propre serveur OpenAI/vLLM sans recevoir de paramètres EPFL.
- **Configuration d'installation guidée** : les URL, le modèle et la clé API sont préparés selon l'environnement choisi, avec proposition d'installation d'Ollama uniquement lorsqu'il est sélectionné et absent.

### Améliorations

- **Installateur plus lisible** : une installation existante propose simplement de réinstaller ou désinstaller l'application, avec une case indépendante pour conserver la configuration et le dernier modèle utilisé.
- **Arrêt automatique** : l'installateur propose de fermer proprement une instance de Traducteur encore active avant de poursuivre.
- **Désinstallation complète** : un raccourci est ajouté au menu Démarrer et le désinstalleur permet de conserver ou supprimer les données utilisateur.
- **Erreurs exploitables** : les erreurs HTTP incluent le détail renvoyé par le serveur et le format OpenAI utilisé; une configuration invalide ne remplace pas la dernière configuration fonctionnelle.
- **Documentation réorganisée** : les parcours EPFL/RCP, externe, Ollama et OpenAI/vLLM sont distingués et la création initiale de la clé RCP est documentée.
- **Distribution simplifiée** : le dossier de sortie public devient `bin` et seul `traducteur-setup.exe` est versionné; l'exécutable intermédiaire reste local.
- **Confidentialité clarifiée** : la documentation présente le fonctionnement entièrement local et autonome avec Ollama, distingue le traitement distant et précise que les contenus sensibles doivent être anonymisés avant leur envoi.
- **Personnalisation mise en avant** : le README présente les prompts modifiables comme une fonction centrale et donne des exemples d'adaptation des modes Traduire, Réécrire, E-mail et Alternatives.
- **README recentré** : la comparaison ponctuelle de tailles de modèles a été retirée, la fonction `lookup` est expliquée comme la recherche d'alternatives et les sections d'architecture, de compilation et de dépannage sont regroupées dans la documentation technique.
- **Configuration simplifiée** : suppression du chemin imposé par variable d'environnement; l'application utilise le fichier créé à côté de l'exécutable ou le sélecteur lorsqu'aucune configuration n'est trouvée.
- **Compatibilité historique retirée** : suppression des anciennes clés et variantes de configuration non utilisées, de la recherche dans le dossier courant et de deux fonctions de conversion Markdown devenues inaccessibles.
- **Découverte vLLM explicitée** : la documentation et l'éditeur de configuration indiquent que `models_url` accepte aussi le format OpenAI/vLLM de `/v1/models`.
- **Format d'API obligatoire** : `api_format` doit désormais être explicitement défini sur `ollama` ou `openai`; aucun fournisseur n'est choisi silencieusement.
- **Artefacts inutilisés retirés** : suppression du fichier PyInstaller généré `traducteur.spec` et du guide alternatif orphelin consacré à PythonAnywhere.

### Corrections

- **Anciennes installations sans désinstalleur** : l'assistant peut désormais supprimer proprement une version portable ou incomplète lorsqu'aucun `uninsXXX.exe` n'est disponible; il reconnaît aussi les chemins de désinstallation contenant des paramètres et n'utilise plus la constante `{app}` avant son initialisation.
- **URL d'inférence exacte** : suppression de l'ajout automatique de `/api/chat`; `server_url` et `models_url` sont désormais utilisées exactement telles qu'elles sont configurées.
- **Compatibilité des endpoints OpenAI** : le corps de requête et le parsing utilisent automatiquement `messages` pour `/chat/completions` et `prompt` pour `/completions`.
- **Rafraîchissement des modèles** : la liste déroulante est mise à jour après une modification de configuration et ne conserve pas les modèles d'un ancien serveur.

---

## 1.0
### Nouvelles fonctionnalités
- **Installateur Windows guidé** : Ajout d'un assistant par utilisateur qui propose des valeurs modifiables pour le serveur, le modèle et la clé API, puis crée `.translator_config.json` sans écraser une configuration existante.
- **Accompagnement Ollama** : Lorsque Ollama n'est pas détecté, l'assistant demande avant de télécharger et lancer son installateur officiel; l'option peut être refusée pour un serveur distant.
- **Démarrage avec Windows** : L'installateur sépare le raccourci de démarrage automatique, activé par défaut, du choix de lancer Traducteur en arrière-plan.
- **Instance et mise à niveau sécurisées** : Ajout de mutex pour empêcher plusieurs instances de l'application ou de l'installateur et détection des mises à niveau par l'`AppId` stable.
- **Prompts configurables** : Ajout de prompts dédiés dans `.translator_config.json` pour `traduire`, `réécrire` et `email`.
- **Modes en français** : Les intitulés de l'interface affichent maintenant `Traduire`, `Réécrire` et `E-mail`.
- **Démarrage masqué optionnel** : Nouveau paramètre `hide_window_on_start` pour lancer l'application directement en arrière-plan.
- **Copie rapide** : Ajout d'un bouton `Copier` pour copier la traduction en un clic.
- **Alternatives contextuelles** : Ajout d'un lookup de synonymes/variantes sur le texte sélectionné.
- **Liens cliquables** : Conservation des liens HTML copiés depuis le presse-papiers avec affichage propre, clic direct et Markdown interne pour la traduction.
- **Configuration obligatoire** : Si `.translator_config.json` est introuvable, l'application demande de sélectionner un fichier JSON valide avant de démarrer.

### Améliorations
- **Prompts optimisés** : Traduction fidèle, réécriture naturelle, et e-mail cordial, professionnel, fluide, sans style trop artificiel.
- **Liens préservés** : Les prompts demandent de conserver les liens, URL et destinations Markdown/HTML.
- **Inversion améliorée** : Le bouton d'inversion reprend la traduction comme nouveau texte source quand elle existe, puis relance automatiquement la traduction.
- **Recherche de config simplifiée** : dossier de l'application, puis dossier courant.
- **Prompts externalisés** : Suppression de `DEFAULT_CONFIG` et des prompts de repli dans `translate.py`; les quatre prompts proviennent obligatoirement du JSON.
- **Langues configurables** : Déplacement des libellés de langues dans le JSON, avec conservation obligatoire de `auto`, `fr`, `en`, `de`, `it`, `es` et `pt`.
- **Modèles dynamiques** : Suppression de la clé `models`; la liste provient de l'API Ollama et `default_model` sert de repli.
- **Bouton d'action dynamique** : Son intitulé suit désormais le mode sélectionné : `Traduire`, `Réécrire` ou `E-mail`.
- **Presse-papiers enrichi** : Conservation des titres `h1` à `h6`, du gras et de l'italique HTML/CSS, conversion Markdown pour le modèle et rendu stylé dans l'interface.
- **Choix du modèle clarifié** : La documentation présente `ministral-3:3b` comme simple exemple local multilingue et rappelle que tout modèle compatible peut être configuré.
- **Démarrage Windows simplifié** : Le README met désormais l'exécutable en avant, détaille le placement obligatoire de `.translator_config.json` et reporte les instructions Python vers une section de développement en fin de document.
- **Dépendance LLM explicitée** : Le README distingue l'utilisation d'un modèle local ou distant et renvoie vers la documentation officielle d'Ollama.
- **Aperçu de l'interface** : Ajout d'une capture d'écran dans le README et conservation du dossier `img/` pour les illustrations de documentation.
- **Alerte Windows documentée** : Le README explique l'avertissement SmartScreen causé par l'absence actuelle de signature et déconseille de désactiver cette protection globalement.
- **Nettoyage du dépôt** : Suppression des dossiers `examples/` et `archive/legacy/`, désormais exclus du projet.
- **Préparation Git** : Ajout d'un fichier `LICENSE` et d'un exemple `.translator_config.example.json`.
- **Robustesse accrue** : Booléens de config normalisés, prompts personnalisés plus tolérants, et permutation de langues corrigée quand la source vaut `auto`.

### Corrections
- **Config dist corrigée** : Correction d'un JSON invalide dans `dist/.translator_config.json`.
- **Classes CSS du presse-papiers** : Prise en charge de `font-weight` et `font-style` définis dans une balise `style`, avec correction des plages de style en fin de paragraphe.

---

## 0.12
### Nouvelles fonctionnalités
- **System Tray** : L'application reste active en arrière-plan dans la barre des tâches
- **Raccourci global CTRL+Shift+C** : Traduire automatiquement le contenu du presse-papier
- **Double Ctrl+C global** : Affiche la fenêtre, récupère le presse-papier et lance automatiquement la traduction
- **Mode veille par la croix** : Fermer la fenêtre masque l'application au lieu de quitter
- **Configuration JSON restaurée** : Chargement de `.translator_config.json` avec fallback localhost
- **Clé API optionnelle** : Support de `api_key` et `api_key_header` pour les endpoints protégés
- **Thinking désactivé par défaut** : Envoi de `think: false` pour accélérer les traductions avec les modèles compatibles
- **Support fichiers multiples** : Import de .txt, .docx (Word), .pdf avec extraction automatique
- **Dépendances conditionnelles** : Support PDF/DOCX/Tray/Keyboard activé automatiquement si les bibliothèques sont installées
- **Messages d'erreur améliorés** : Indications claires pour installer les dépendances manquantes
- **Documentation complète** : README.md, requirements.txt, instructions déploiement Windows
- **Exécutable standalone** : Création d'exécutable avec PyInstaller (~53 Mo)
- **docs/FEATURES.md** : Documentation des nouvelles fonctionnalités

### Améliorations techniques
- **System Tray intégré** : Menu contextuel avec Afficher, Traduire Clipboard, Quitter
- **Écoute des touches globales** : Raccourci clavier qui fonctionne partout
- **Temporisation presse-papier** : Attente courte avant lecture du presse-papier puis lancement automatique après réaffichage de la fenêtre
- **Recherche config multi-emplacements** : dossier script/exécutable, `dist`, anciens dossiers `tkinter`, puis dossier utilisateur
- **Extraction PDF** : Utilisation de pdfplumber pour extraction de texte précise
- **Lecture Word** : Utilisation de python-docx pour fichiers .docx
- **Gestion d'erreurs robuste** : Détection des formats non supportés et fichiers vides
- **Interface imports** : Filetypes dynamiques selon les bibliothèques disponibles

### Améliorations
- **Code optimisé** : Réduction de 38% de la taille du code (736 → 456 lignes)
- **Structure simplifiée** : Suppression du code dupliqué et méthodes helper
- **Imports nettoyés** : Regroupement et simplification des imports
- **Configuration simplifiée** : Suppression du code de chargement complexe
- **Interface plus confortable** : Boutons et menus plus grands (32px hauteur)
- **Polices augmentées** : Taille 12pt pour une meilleure lisibilité
- **Labels épurés** : "Texte source" et "Traduction" sans gras- **Affichage corrigé** : Division 50/50 dynamique des zones de texte avec stretch
- **Boutons épurés** : Suppression du gras sur "Traduire" et "<>" pour un look plus moderne
- **Labels menus simplifiés** : Suppression du gras sur "Mode:", "Modèle:", "De:", "Vers:"- **Layout équilibré** : Les zones source et cible ont maintenant la même largeur (50/50)

### Corrections
- **Bug CustomTkinter corrigé** : Méthodes `config()` remplacées par `configure()` pour compatibilité CTk
- **Layout PanedWindow corrigé** : Division 50/50 forcée pour les zones de texte
- **Lisibilité améliorée** : Contraste et tailles de polices optimisés pour les menus déroulants
- **Bug thread-safety CRITIQUE** : Utilisation d'une queue pour les mises à jour de l'interface (modifications des widgets Tkinter depuis le thread principal uniquement)
- **Affichage traduction corrigé** : Implémentation de `_process_queue()` qui traite les messages de traduction de manière thread-safe
- **API Ollama corrigée** : Passage du format `prompt` à `messages` pour la compatibilité avec les modèles récents
- **Parsing réponse corrigé** : Lecture des chunks depuis `data['message']['content']` au lieu de `data['response']`
- **Fermeture corrigée** : La croix met l'application en veille, tandis que les commandes Quitter nettoient le tray et le listener clavier
- **Détection Ctrl+C renforcée** : Prise en charge des variantes `c`, caractère de contrôle et code virtuel Windows
- **Anti-rebond raccourci global** : Évite qu'un double déclenchement stoppe immédiatement la traduction automatique
- **Préparation Git** : Ajout d'un `.gitignore` et d'un exemple `.translator_config.example.json`
- Méthode helper `set_status_text()` pour gérer les widgets CTk/ttk de manière uniforme

### Améliorations par rapport à 0.11
- Interface plus jolie et moderne avec CustomTkinter
- Métriques utiles pour l'utilisateur (mots et temps)
- Layout équilibré des zones de texte
- Design professionnel avec tooltips et icônes

---

## 0.11 (Première version avec historique)
### Nouvelles fonctionnalités
- **Historique des traductions** : Menu "Fichier > Historique" pour consulter et recharger les 10 dernières traductions
- **Interface moderne** : Style ttk amélioré avec padding et couleurs cohérentes
- **Support étendu des langues** : Ajout de 25+ langues supplémentaires (russe, chinois, arabe, etc.)
- **Menu principal** : Barre de menus avec accès aux fonctions d'import/export

### Améliorations
- Interface plus épurée avec menu en haut
- Historique intelligent qui évite les doublons
- Chargement rapide des traductions depuis l'historique
- **Suppression des boutons redondants** : Boutons Importer/Exporter retirés de la barre d'outils (accessibles via menu)

### Corrections
- Méthode `export_translation` manquante corrigée

---

## 0.10 (Première version avec fichiers)
### Nouvelles fonctionnalités
- **Streaming en temps réel** : Les traductions s'affichent au fur et à mesure (chunk par chunk)
- **Import de fichiers** : Support des fichiers texte, Word (.docx), PDF
- **Export de traduction** : Sauvegarde en fichier texte
- **Raccourcis étendus** : Ctrl+O (importer), Ctrl+S (exporter)

### Améliorations
- Parser de streaming corrigé pour Ollama API
- Support conditionnel des formats (si bibliothèques installées)

---

## 0.9 (Première version "propre")
### Nouvelles fonctionnalités
- **Interface simplifiée** inspirée de DeepL avec deux zones de texte (source/cible) côte à côte
- **Sélection de modèle** dans la barre d'outils
- **Chargement de configuration** depuis `.translator_config.json`
- **Trois modes** : Traduction, Réécriture, Email
- **Détection automatique de langue** avec basculement intelligent de la cible
- **Raccourcis clavier** :
  - Ctrl+Enter pour traduire
  - Ctrl+Shift+C pour copier la traduction

### Améliorations par rapport à 0.8
- Code simplifié et nettoyé
- Suppression des dépendances externes complexes (keyboard, pyperclip)
- Interface plus moderne et responsive
- PanedWindow pour redimensionner facilement les zones

### Corrections
- Erreur "startswith first arg must be bytes" corrigée
- Chargement du fichier config amélioré (cherche plusieurs emplacements)

---

## 0.8 (Détection + ajustement auto de langue)
### Nouvelles fonctionnalités
- **Détection de langue** au moment d'exécuter
- **Ajustement automatique de la cible** si source = "Auto" et français détecté → cible = anglais
- **Mode "Réécrit mon mail"** avec option "Forme inclusive"
- **Prompts multilingues** utilisant les noms de langues en toutes lettres

### Améliorations
- Barre d'outils compacte avec Mode/Source/Cible/Boutons
- Meilleure gestion des états et du threading

---

## 0.7 (Configuration JSON + Modes)
### Nouvelles fonctionnalités
- **Chargement de configuration** depuis `.translator_config.json`
- **Modes radio buttons** : Traduction ⟷ Réécriture
- **Combobox pour langues** (source et cible)
- **Bouton Permuter** (⇅) pour échanger contenus et langues

### Améliorations
- Session HTTP réutilisable avec retries
- Indicateur d'état et timer simple
- PanedWindow pour zones de texte

---

## 0.6 (Réécriture + Formes inclusives)
### Nouvelles fonctionnalités
- **Mode Réécriture professionnelle**
- **Option Forme inclusive** (boutons radio : Non/Oui)
- **Interface séparée** avec Frame principal et zones de texte

---

## 0.5 (Permutation et modes)
### Nouvelles fonctionnalités
- **Bouton ⇅ Permuter** : échange contenus et langues
- **Modes** : Traduction ⟷ Réécriture (radio buttons)
- **Combobox pour langues** : source (Auto) + cible (fr, en, de, it, es)
- **Streaming LLM** avec classes dédiées
- **Bouton Stop** + drapeau d'annulation
- **Raccourcis clavier** : Ctrl+Enter, Ctrl+Shift+C, Ctrl+L

### Améliorations
- Construction du prompt déplacée côté UI
- Session HTTP avec retries

---

## 0.4 (Premières versions Tkinter)
### Fonctionnalités basiques
- Interface Tkinter simple
- Zone de saisie et de résultat
- Boutons de base (Traduire, Arrêter, Copier)
- Hook global double Ctrl+C pour lancer l'app

---

## 0.1-0.3
- Interfaces Tkinter très basiques
- Boutons et zones de texte élémentaires
- Pas de configuration
- Pas de streaming

---

## Notes de migration

### Pour passer à 1.0
1. Utiliser `translate.py`.
2. Garder le fichier `.translator_config.json` existant si vous en avez un.
3. Sinon, copier `.translator_config.example.json` vers `.translator_config.json` uniquement si vous voulez personnaliser le serveur ou les modèles.

### Dépendances
```
requests
tkinter (built-in)
customtkinter, pystray, pillow, pynput, pdfplumber, python-docx (voir requirements.txt)
```

### Configuration exemple (.translator_config.json)
```json
{
  "server_url": "http://localhost:11434/api/chat",
  "api_key": "",
  "api_key_header": "Authorization",
  "think": false,
  "hide_window_on_start": false,
  "default_model": "ministral-3:3b",
  "prompts": {
    "traduire": "Tu es un traducteur professionnel. Traduis le texte suivant de {source_language} vers {target_language}.\n\nContraintes:\n- Préserve fidèlement le sens, le ton, la mise en forme et les sauts de ligne.\n- N'ajoute aucune explication, note ou variante.\n- Si la langue source vaut Auto, détecte-la naturellement.\n\nTexte:\n{text}",
    "réécrire": "Tu es un réviseur éditorial franc, précis et naturel. Réécris le texte suivant en {target_language}.\n\nObjectif:\n- Améliorer la clarté, la fluidité, le style et la correction.\n- Conserver l'intention, les informations importantes et le niveau de formalité.\n- Ne pas rendre le texte artificiel ni trop emphatique.\n- Répondre uniquement avec la version réécrite.\n\nTexte:\n{text}",
    "email": "Tu es un assistant de rédaction spécialisé dans les e-mails professionnels. Transforme le texte suivant en e-mail en {target_language}.\n\nStyle attendu:\n- Cordial, professionnel, fluide et humain.\n- Naturel, direct, sans tournures trop typiques de l'IA.\n- Poli sans être excessivement formel.\n- Structure claire avec salutation et formule de clôture si pertinent.\n- Répondre uniquement avec l'e-mail final.\n\nTexte:\n{text}"
  }
}
```
