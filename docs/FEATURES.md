# Guide des nouvelles fonctionnalités

## System Tray

L'application reste active dans la barre des tâches (system tray) même quand vous fermez la fenêtre.

### Utilisation
1. Fermez la fenêtre → l'application continue en arrière-plan
2. Cliquez sur l'icône dans le tray pour réafficher la fenêtre
3. Menu du tray : Afficher, Traduire Clipboard, Quitter

### Prérequis
```bash
pip install pystray pillow
```

## Raccourcis globaux

Traduisez n'importe quel texte en copiant puis en utilisant double Ctrl+C ou Ctrl+Shift+C.

### Fonctionnement
1. Copiez du texte (CTRL+C)
2. Appuyez sur **CTRL+C** une deuxième fois rapidement, ou sur **CTRL+Shift+C**
3. L'application s'affiche avec le texte dans la zone source
4. La traduction démarre automatiquement

### Prérequis
```bash
pip install pynput
```

## Configuration recommandée

Pour profiter de toutes les fonctionnalités :
```bash
pip install -r requirements.txt
```

Cela installe :
- customtkinter : Interface moderne
- pystray + pillow : System tray
- pynput : Raccourcis globaux
- pdfplumber + python-docx : Support fichiers
- requests : API Ollama

## Configuration serveur

L'application exige une configuration indiquant le serveur local ou distant et le modèle :

```json
{
  "server_url": "http://localhost:11434/api/chat",
  "api_key": "",
  "api_key_header": "Authorization",
  "think": false,
  "default_model": "ministral-3:3b"
}
```

Copiez `.translator_config.example.json` vers `.translator_config.json`, puis configurez `server_url`, `default_model`, `languages` et les quatre prompts requis. Les langues de base `fr`, `en`, `de`, `it`, `es` et `pt`, ainsi que `auto`, doivent rester présentes; d'autres langues peuvent être ajoutées librement. Si aucun fichier n'est détecté, l'application demande de le sélectionner. Le fichier local `.translator_config.json` est ignoré par Git.
Le modèle indiqué est un exemple multilingue compact, pas un prérequis. Tout modèle exposé par le serveur compatible Ollama peut être utilisé.
La clé historique `model` est encore acceptée, mais `default_model` est la clé recommandée.
Si le serveur exige une clé API, renseignez `api_key`. Par défaut elle est envoyée en `Authorization: Bearer <api_key>` ; utilisez `api_key_header` pour choisir un autre nom d'en-tête.
`think` est désactivé par défaut pour éviter la latence inutile des modèles de raisonnement pendant les traductions.
Pour forcer un fichier précis, définissez la variable d'environnement `TRANSLATOR_CONFIG`.

## Dépannage

### System Tray ne fonctionne pas
- Linux : Assurez-vous d'avoir un système de notification (libnotify)
- macOS : Nécessite Tkinter compilé avec support D-Bus
- Windows : Devrait fonctionner avec pystray

### Raccourci global ne répond pas
- Linux : Nécessite les permissions d'accès au clavier
- macOS : Accordez les permissions dans Préférences Système → Sécurité
- Windows : Devrait fonctionner sans configuration

## Limitations

- Raccourci global : Dépend des permissions clavier du système
- System Tray : Dépend du système d'exploitation et de l'environnement de bureau
