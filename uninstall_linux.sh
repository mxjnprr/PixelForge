#!/bin/bash
# Uninstall script for PixelForge Studio on Linux

APP_NAME="pixelforge-studio"
APP_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

echo "🗑️ Désinstallation de PixelForge Studio..."

# Remove files
rm -rf "$APP_DIR"
rm -f "$BIN_DIR/$APP_NAME"
rm -f "$DESKTOP_DIR/$APP_NAME.desktop"
rm -f "$ICON_DIR/$APP_NAME.png"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "✅ Désinstallation terminée !"
echo ""
echo "Note: Les fichiers de configuration dans ~/.config/pixelforge-studio"
echo "n'ont pas été supprimés. Supprimez-les manuellement si nécessaire."
