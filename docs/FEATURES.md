# Fonctionnalités et utilisation

Ce guide décrit Traducteur 1.2.0. Pour installer l'application, consultez le [README](../README.md).

## Travailler dans la fenêtre

Choisissez le mode **Traduire**, **Réécrire** ou **E-mail**, le modèle et les langues. Saisissez ou collez le texte à gauche, puis cliquez sur le bouton du mode choisi. Le résultat apparaît à droite. Une nouvelle pression pendant la génération demande son arrêt.

- **Effacer** vide les deux panneaux et remet les compteurs à zéro ; l'historique de la session reste disponible.
- **Copier** copie tout le résultat. Les liens, titres, gras et italiques sont pris en charge dans les panneaux ; l'export en fichier reste au format texte.
- **Alternatives** propose des formulations pour un passage sélectionné, avec le texte source et le résultat comme contexte.
- **Fichier > Importer** lit les fichiers `.txt`, `.docx` et les PDF contenant du texte extractible. L'application ne fait pas d'OCR.
- **Fichier > Exporter** enregistre le résultat dans un fichier `.txt`.
- **Fichier > Historique** permet de reprendre un résultat de la session.

## Menus et taille de l'interface

**Affichage > Taille de l'interface** propose 80, 90, 100, 110, 125 et 150 %. Le réglage s'ajoute à la mise à l'échelle Windows et s'applique aux menus, aux contrôles et aux textes. Il est mémorisé. La fenêtre initiale vise 1100 × 720 et réduit ses dimensions selon le zoom et l'espace disponible hors barre des tâches.

**Aide > Utilisation et raccourcis...** présente les fonctions et les raccourcis. **Aide > À propos...** affiche l'auteur, son profil EPFL, le dépôt, les rappels d'utilisation et la licence complète consultable hors ligne.

## Changer de configuration

**Fichier > Ouvrir une configuration...** ouvre un autre fichier JSON complet, par exemple `EPFL.json` ou `Ollama.json`. Son nom reste visible en haut de la fenêtre. Les textes et l'historique sont conservés ; les traitements de la configuration précédente sont interrompus et leurs réponses tardives ignorées. Un fichier invalide ou une sélection annulée laisse la configuration actuelle active.

Le dernier fichier choisi est retrouvé au prochain lancement. S'il est devenu inaccessible ou invalide, l'application demande un autre fichier. L'éditeur ouvert doit être enregistré ou fermé avant de changer de configuration. Le choix d'un fichier passe actuellement par le sélecteur de fichiers ; il n'y a pas encore de liste de configurations récentes.

**Fichier > Modifier la configuration...** édite le fichier actif. Le JSON est validé avant enregistrement. Le fichier est aussi surveillé toutes les secondes : une modification externe valide est appliquée automatiquement.

Pour créer un nouveau fichier, partez de [`.translator_config.example.json`](../.translator_config.example.json). Il faut conserver `api_format`, `server_url`, les langues obligatoires et les quatre prompts. Les paramètres de connexion seuls ne constituent pas une configuration complète. Voir le [README](../README.md) pour les exemples et les règles de validation.

Ollama local propose initialement `ministral-3:3b`. Le profil EPFL de l'installateur propose `swiss-ai/Apertus-v1.5-8B`. Le dernier modèle utilisé reste prioritaire au lancement si son serveur correspond. Les modes et les alternatives utilisent les consignes du fichier actif.

## Raccourcis

| Raccourci | Action |
| --- | --- |
| Ctrl+Entrée | Lancer le mode choisi ou demander l'arrêt de la génération |
| Ctrl+Alt+C | Copier le résultat complet |
| Ctrl+L | Proposer des alternatives au passage sélectionné |
| Ctrl+O | Importer un fichier |
| Ctrl+S | Exporter le résultat en texte |
| Ctrl+, | Modifier la configuration active |
| F1 | Afficher l'aide |
| F10 | Donner le focus au premier menu |
| Ctrl+C, Ctrl+X, Ctrl+V | Copier, couper, coller dans les panneaux |
| Ctrl+Z, Ctrl+Y | Annuler et rétablir une modification du texte source sous Windows |
| Échap | Fermer l'aide, À propos ou l'éditeur de configuration |

Depuis une autre application, **double Ctrl+C** (deux pressions espacées de moins de 0,6 seconde) ou **Ctrl+Maj+C** affiche Traducteur et traite le presse-papier. Traducteur doit rester lancé et les raccourcis globaux doivent être disponibles.

## Arrière-plan et limites

La croix masque la fenêtre. L'icône près de l'horloge permet de la réafficher, de traiter le presse-papier ou de quitter. **Fichier > Quitter** ferme réellement l'application. Le démarrage masqué et le lancement automatique avec Windows sont deux réglages distincts dans l'installateur.

La distribution fournie et les vérifications de l'interface ciblent Windows 10/11. Il n'y a actuellement ni paquet Ubuntu publié, ni interface ou installateur bilingue FR/EN. L'exécution depuis les sources sur d'autres systèmes dépend notamment de Tk, du bureau et des permissions de clavier ; elle ne garantit pas le fonctionnement de l'icône et des raccourcis globaux.

Les réponses du modèle peuvent contenir des erreurs. Avec un serveur distant, les textes lui sont envoyés ; l'application ne les anonymise pas automatiquement. La clé API reste dans le fichier JSON local. Consultez les [précautions du README](../README.md).
