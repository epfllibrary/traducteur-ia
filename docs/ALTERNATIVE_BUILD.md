# Solution alternative : Utiliser auto-py-to-exe

Si vous préférez une interface graphique sur Windows, utilisez auto-py-to-exe.

## Auto Py to Exe

### Étape 1 : Préparer les fichiers
Placez ces fichiers dans le même dossier sur Windows :
- `translate.py`
- `requirements.txt`
- `.translator_config.example.json`

### Étape 2 : Utiliser l'outil
1. Installez auto-py-to-exe sur Windows : `pip install auto-py-to-exe`
2. Lancez l'interface : `auto-py-to-exe`
3. Configurez :
   - Script Location : `translate.py`
   - Onefile : ✅
   - Windowed : ✅
   - Name : `traducteur`

### Étape 3 : Récupérez l'exécutable
- L'outil génère un exe Windows dans le dossier de sortie choisi
- Copiez `.translator_config.example.json` à côté de l'exécutable sous le nom `.translator_config.json`, puis adaptez le serveur et le modèle
- Testez l'exécutable sur Windows

## Alternative : PythonAnywhere

Attention : PythonAnywhere construit un binaire Linux, pas un `.exe` Windows. Cette option sert seulement à tester le packaging Linux.

### Créer un compte
1. Allez sur https://www.pythonanywhere.com/
2. Créez un compte gratuit
3. Uploadez vos fichiers

### Installation et build
```bash
# Dans PythonAnywhere (Linux)
pip install --user pyinstaller
pip install --user -r requirements.txt
pyinstaller --onefile --windowed --name traducteur translate.py
```

### Téléchargement
- Téléchargez `dist/traducteur` depuis PythonAnywhere pour un usage Linux uniquement

## Vérification finale

Testez l'exécutable sur un PC Windows :
```cmd
REM Sur Windows
traducteur.exe
```

Si ça ne marche toujours pas, le problème vient de :
- Antivirus bloquant l'exe
- Droits d'exécution insuffisants
- Exécutable corrompu lors du transfert
