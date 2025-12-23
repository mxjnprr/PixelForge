# 🍌 Nano Banana Batch Processor

Application de traitement d'images en masse utilisant l'API Nano Banana (Gemini) de Google.

## Fonctionnalités

- **Traitement en masse** : Appliquez le même prompt à plusieurs images simultanément
- **Interface glisser-déposer** : Ajoutez facilement des images par drag & drop
- **Progression visuelle** : Suivez l'avancement du traitement en temps réel
- **Configuration persistante** : Vos paramètres sont sauvegardés automatiquement
- **Cross-platform** : Fonctionne sous Linux et Windows

## Prérequis

- Python 3.9 ou supérieur
- Une clé API Gemini (gratuite sur [Google AI Studio](https://aistudio.google.com/app/apikey))

## Installation

### Option A : Installation rapide (recommandée)

Cette méthode installe l'application sur votre système avec un raccourci dans le menu des applications.

#### 1. Cloner le dépôt GitHub

```bash
git clone https://github.com/mxjnprr/PixelForge.git
cd PixelForge
```

#### 2. Lancer le script d'installation

**Linux/Mac :**
```bash
chmod +x install_linux.sh
./install_linux.sh
```

**Windows :**
```batch
install_windows.bat
```

#### Ce que fait le script d'installation :

| Étape | Linux | Windows |
|-------|-------|---------|
| 📁 Copie des fichiers | `~/.local/share/pixelforge-studio/` | `%LOCALAPPDATA%\PixelForgeStudio\` |
| 🐍 Environnement Python | Crée un venv isolé | Crée un venv isolé |
| 📦 Dépendances | Installation automatique | Installation automatique |
| 🚀 Raccourci | Menu applications + commande `pixelforge-studio` | Menu Démarrer + Bureau |

---

### Option B : Installation manuelle (développeurs)

Si vous préférez gérer l'environnement vous-même :

#### 1. Cloner le dépôt GitHub

```bash
git clone https://github.com/mxjnprr/PixelForge.git
cd PixelForge
```

#### 2. Créer un environnement virtuel

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```batch
python -m venv venv
venv\Scripts\activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

### Désinstallation

**Linux/Mac :**
```bash
./uninstall_linux.sh
```

**Windows :**
```batch
uninstall_windows.bat
```

> **Note :** Les fichiers de configuration utilisateur ne sont pas supprimés automatiquement.
> - Linux : `~/.config/pixelforge-studio/`
> - Windows : `%APPDATA%\pixelforge-studio\`

## Utilisation

### Lancement

**Linux:**
```bash
./run_linux.sh
# ou
python3 main.py
```

**Windows:**
```batch
run_windows.bat
REM ou
python main.py
```

### Configuration initiale

1. Allez dans l'onglet **⚙️ Paramètres**
2. Entrez votre **clé API Gemini**
3. Cliquez sur **Tester** pour vérifier la connexion
4. Configurez le **dossier de sortie** (optionnel)
5. Choisissez le **modèle** et le **ratio d'aspect**
6. Cliquez sur **Sauvegarder les paramètres**

### Traitement d'images

1. Allez dans l'onglet **📷 Traitement**
2. **Ajoutez des images** :
   - Cliquez sur "➕ Ajouter des images"
   - Ou glissez-déposez des images directement
3. **Rédigez votre prompt** dans la zone de texte
4. Cliquez sur **🚀 Lancer le traitement**
5. Suivez la progression dans la fenêtre de dialogue

### Exemples de prompts

- `Transforme cette photo en style aquarelle`
- `Ajoute un arrière-plan de coucher de soleil`
- `Rends cette image plus lumineuse et ajoute des étoiles`
- `Change le style en illustration cartoon`
- `Supprime l'arrière-plan et remplace-le par un fond blanc`

## Modèles disponibles

| Modèle | Description |
|--------|-------------|
| **Nano Banana (Fast)** | `gemini-2.5-flash-image` - Rapide, idéal pour le traitement en masse |
| **Nano Banana Pro** | `gemini-3-pro-image-preview` - Haute qualité, meilleur pour les détails |

## Formats supportés

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)
- BMP (.bmp)

## Structure du projet

```
Traitement Masse Nano Banana/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances
├── api_client.py          # Client API Gemini
├── batch_processor.py     # Logique de traitement
├── gui/
│   ├── main_window.py     # Fenêtre principale
│   ├── image_list.py      # Liste d'images
│   ├── settings_panel.py  # Panneau de configuration
│   └── progress_dialog.py # Dialogue de progression
├── utils/
│   ├── config.py          # Gestion de configuration
│   └── image_utils.py     # Utilitaires d'images
├── run_linux.sh           # Lanceur Linux
└── run_windows.bat        # Lanceur Windows
```

## Configuration

La configuration est stockée automatiquement :
- **Linux/Mac** : `~/.config/nano-banana-processor/config.json`
- **Windows** : `%APPDATA%\nano-banana-processor\config.json`

## Dépannage

### "Clé API invalide"
- Vérifiez que votre clé API est correcte
- Assurez-vous que l'API Gemini est activée dans votre projet Google Cloud

### "L'API n'a pas généré d'image"
- Certains prompts peuvent être refusés par l'API pour des raisons de sécurité
- Essayez de reformuler votre prompt

### "Erreur d'initialisation du client"
- Vérifiez votre connexion internet
- Assurez-vous que le package `google-genai` est installé

## Licence

Ce projet est fourni tel quel pour un usage interne.
