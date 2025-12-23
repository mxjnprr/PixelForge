# 🔥 PixelForge Studio

Application de traitement et génération d'images utilisant l'API Nano Banana (Gemini) de Google.

## ✨ Fonctionnalités

### 📷 Édition en Masse
- Appliquez le même prompt à plusieurs images simultanément
- Interface glisser-déposer pour ajouter des images
- Progression visuelle en temps réel
- Styles prédéfinis (Aquarelle, Cartoon, Cyberpunk, etc.)

### ✨ Génération d'Images
- Créez des images à partir de descriptions textuelles
- Génération par lot (jusqu'à 10 images)
- Aperçus interactifs cliquables

### 🌐 Édition Ciblée
- **Dessinez directement** sur l'image pour indiquer la zone à modifier
- **Outils de sélection** : Rectangle, Ellipse, Sélection libre
- **Pinceau** avec 10 couleurs + couleur personnalisée
- **Taille de pinceau ajustable** (2-50px)
- L'IA modifie uniquement la zone dessinée

### 🎨 Transfert de Style (NOUVEAU)
- **Mixez le style** d'une image de référence sur votre image source
- **Intensité réglable** : Subtil, Modéré, Fort
- Appliquez textures, couleurs et ambiances d'une photo à une autre

### ⚙️ Général
- Configuration persistante automatique
- Stockage sécurisé de la clé API (trousseau système)
- Cross-platform : Linux et Windows

## 📋 Prérequis

- Python 3.9 ou supérieur
- Une clé API Gemini (gratuite sur [Google AI Studio](https://aistudio.google.com/app/apikey))

## 🚀 Installation

### Option A : Installation rapide (recommandée)

```bash
# 1. Cloner le dépôt
git clone https://github.com/mxjnprr/PixelForge.git
cd PixelForge

# 2. Lancer le script d'installation
# Linux/Mac :
chmod +x install_linux.sh && ./install_linux.sh

# Windows :
install_windows.bat
```

### Option B : Installation manuelle

```bash
# Cloner et créer l'environnement
git clone https://github.com/mxjnprr/PixelForge.git
cd PixelForge
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## 📖 Utilisation

Voir la [documentation complète](docs/USAGE.md) pour des instructions détaillées.

### Lancement rapide

```bash
./run_linux.sh      # Linux
run_windows.bat     # Windows
```

### Configuration initiale

1. Onglet **⚙️ Paramètres** → Entrez votre clé API Gemini
2. Cliquez **Tester** pour vérifier la connexion

## 🛠️ Modèles disponibles

| Modèle | Description |
|--------|-------------|
| **Nano Banana (Fast)** | Rapide, idéal pour le traitement en masse |
| **Nano Banana Pro** | Haute qualité, meilleur pour les détails |

## 📁 Structure du projet

```
PixelForge/
├── main.py                 # Point d'entrée
├── api_client.py           # Client API Gemini
├── batch_processor.py      # Logique de traitement
├── gui/
│   ├── main_window.py      # Fenêtre principale
│   ├── targeted_edit_tab.py # Édition ciblée avec dessin
│   ├── style_transfer_tab.py # Transfert de style
│   ├── image_list.py       # Liste d'images
│   └── ...
├── docs/
│   └── USAGE.md            # Documentation d'utilisation
└── utils/
    ├── config.py           # Configuration
    └── secure_storage.py   # Stockage sécurisé
```

## 🔧 Dépannage

| Problème | Solution |
|----------|----------|
| Clé API invalide | Vérifiez la clé sur [Google AI Studio](https://aistudio.google.com/app/apikey) |
| L'API n'a pas généré d'image | Reformulez votre prompt |
| Erreur d'initialisation | Vérifiez votre connexion internet |

## 📜 Licence

Ce projet est fourni tel quel pour un usage personnel et éducatif.
