#!/bin/bash
# Install script for PixelForge Studio on Linux

set -e

APP_NAME="pixelforge-studio"
APP_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔥 Installation de PixelForge Studio..."

# Create directories
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy application files
echo "📁 Copie des fichiers..."
cp -r "$SCRIPT_DIR"/*.py "$APP_DIR/"
cp -r "$SCRIPT_DIR"/gui "$APP_DIR/"
cp -r "$SCRIPT_DIR"/utils "$APP_DIR/"
cp "$SCRIPT_DIR"/requirements.txt "$APP_DIR/"

# Copy icon if exists
if [ -f "$SCRIPT_DIR/icon.png" ]; then
    cp "$SCRIPT_DIR/icon.png" "$ICON_DIR/$APP_NAME.png"
fi

# Create virtual environment
echo "🐍 Création de l'environnement Python..."
python3 -m venv "$APP_DIR/venv"

# Install dependencies
echo "📦 Installation des dépendances..."
"$APP_DIR/venv/bin/pip" install --upgrade pip -q
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q

# Create launcher script
echo "🚀 Création du lanceur..."
cat > "$BIN_DIR/$APP_NAME" << EOF
#!/bin/bash
cd "$APP_DIR"
source venv/bin/activate
python main.py "\$@"
EOF
chmod +x "$BIN_DIR/$APP_NAME"

# Install desktop entry
echo "🖥️ Installation du raccourci..."
cat > "$DESKTOP_DIR/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=PixelForge Studio
Comment=Éditez et générez des images avec l'IA
Exec=$BIN_DIR/$APP_NAME
Icon=$ICON_DIR/$APP_NAME.png
Terminal=false
Type=Application
Categories=Graphics;Photography;
Keywords=image;ai;generation;editing;
StartupWMClass=pixelforge-studio
EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Vous pouvez maintenant lancer PixelForge Studio depuis :"
echo "  • Le menu des applications"
echo "  • Le terminal : $APP_NAME"
echo ""
echo "Pour désinstaller : ./uninstall_linux.sh"
