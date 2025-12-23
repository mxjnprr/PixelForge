"""
Configuration management for PixelForge Studio.
Handles saving/loading user preferences and secure API key storage.
"""

import json
import os
from pathlib import Path
from typing import Optional


class SecureKeyStorage:
    """
    Secure storage for API keys using system keyring.
    Falls back to encrypted file if keyring is not available.
    """
    
    SERVICE_NAME = "pixelforge-studio"
    KEY_NAME = "gemini_api_key"
    
    def __init__(self, config_dir: Path):
        self._config_dir = config_dir
        self._keyring_available = False
        self._fallback_file = config_dir / ".credentials"
        
        # Try to import keyring
        try:
            import keyring
            self._keyring = keyring
            # Test if keyring backend is available
            try:
                keyring.get_keyring()
                self._keyring_available = True
            except Exception:
                self._keyring_available = False
        except ImportError:
            self._keyring = None
            self._keyring_available = False
    
    def _get_machine_key(self) -> bytes:
        """Generate a machine-specific key for fallback encryption."""
        import hashlib
        import platform
        
        # Create a key from machine-specific info
        machine_info = f"{platform.node()}-{os.getlogin() if hasattr(os, 'getlogin') else 'user'}-pixelforge"
        return hashlib.sha256(machine_info.encode()).digest()
    
    def _encrypt_simple(self, data: str) -> str:
        """Simple XOR encryption for fallback (not cryptographically secure but better than plaintext)."""
        import base64
        key = self._get_machine_key()
        encrypted = bytes([ord(c) ^ key[i % len(key)] for i, c in enumerate(data)])
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_simple(self, encrypted_data: str) -> str:
        """Simple XOR decryption for fallback."""
        import base64
        key = self._get_machine_key()
        data = base64.b64decode(encrypted_data.encode())
        decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
        return decrypted.decode()
    
    def get_api_key(self) -> str:
        """Retrieve the API key from secure storage."""
        # Try keyring first
        if self._keyring_available:
            try:
                key = self._keyring.get_password(self.SERVICE_NAME, self.KEY_NAME)
                if key:
                    return key
            except Exception:
                pass
        
        # Fallback to encrypted file
        if self._fallback_file.exists():
            try:
                with open(self._fallback_file, 'r') as f:
                    encrypted = f.read().strip()
                    if encrypted:
                        return self._decrypt_simple(encrypted)
            except Exception:
                pass
        
        return ""
    
    def set_api_key(self, api_key: str) -> bool:
        """Store the API key in secure storage."""
        success = False
        
        # Try keyring first
        if self._keyring_available:
            try:
                if api_key:
                    self._keyring.set_password(self.SERVICE_NAME, self.KEY_NAME, api_key)
                else:
                    try:
                        self._keyring.delete_password(self.SERVICE_NAME, self.KEY_NAME)
                    except Exception:
                        pass
                success = True
            except Exception as e:
                print(f"Keyring error: {e}")
                success = False
        
        # Always save to fallback as well (in case keyring becomes unavailable)
        try:
            if api_key:
                encrypted = self._encrypt_simple(api_key)
                with open(self._fallback_file, 'w') as f:
                    f.write(encrypted)
                # Set restrictive permissions (owner read/write only)
                os.chmod(self._fallback_file, 0o600)
            else:
                if self._fallback_file.exists():
                    self._fallback_file.unlink()
            success = True
        except Exception as e:
            print(f"Fallback storage error: {e}")
        
        return success
    
    def delete_api_key(self) -> None:
        """Remove the API key from all storage."""
        # Remove from keyring
        if self._keyring_available:
            try:
                self._keyring.delete_password(self.SERVICE_NAME, self.KEY_NAME)
            except Exception:
                pass
        
        # Remove fallback file
        if self._fallback_file.exists():
            try:
                self._fallback_file.unlink()
            except Exception:
                pass
    
    @property
    def storage_method(self) -> str:
        """Return the current storage method being used."""
        if self._keyring_available:
            return "Trousseau système (sécurisé)"
        return "Fichier chiffré local"


class Config:
    """Manages application configuration."""
    
    # Application name
    APP_NAME = "PixelForge Studio"
    
    # Default configuration values (API key stored separately in secure storage)
    DEFAULTS = {
        "output_folder": "",
        "model": "gemini-2.5-flash-image",
        "aspect_ratio": "original",
        "output_quality": "standard",
        "style_preset": "none",
        "rename_pattern": "{original}_processed",
        "last_input_folder": "",
    }
    
    # Available models
    MODELS = [
        ("gemini-2.5-flash-image", "Gemini Flash (Rapide)"),
        ("gemini-3-pro-image-preview", "Gemini Pro (Haute Qualité)"),
    ]
    
    # Available aspect ratios
    ASPECT_RATIOS = [
        ("original", "Format d'origine"),
        ("1:1", "Carré (1:1)"),
        ("16:9", "Paysage large (16:9)"),
        ("9:16", "Portrait (9:16)"),
        ("4:3", "Standard (4:3)"),
        ("3:4", "Portrait (3:4)"),
    ]
    
    # Output quality options
    OUTPUT_QUALITIES = [
        ("standard", "Standard"),
        ("2K", "Haute définition (2K)"),
        ("4K", "Très haute définition (4K)"),
    ]
    
    # Style presets
    STYLE_PRESETS = [
        ("none", "Aucun (prompt libre)"),
        ("photorealistic", "📷 Photoréaliste"),
        ("cartoon", "🎨 Cartoon / Animation"),
        ("anime", "🌸 Anime / Manga"),
        ("oil_painting", "🖼️ Peinture à l'huile"),
        ("watercolor", "💧 Aquarelle"),
        ("sketch", "✏️ Croquis / Dessin"),
        ("3d_render", "🎮 Rendu 3D"),
        ("pixel_art", "👾 Pixel Art"),
        ("minimalist", "◻️ Minimaliste"),
        ("surreal", "🌀 Surréaliste"),
        ("vintage", "📜 Vintage / Rétro"),
        ("neon", "💜 Néon / Cyberpunk"),
    ]
    
    # Style prompt suffixes
    STYLE_PROMPTS = {
        "none": "",
        "photorealistic": ", photorealistic, highly detailed, professional photography, 8K resolution",
        "cartoon": ", cartoon style, vibrant colors, bold outlines, animated look",
        "anime": ", anime style, manga art, Japanese animation, detailed eyes",
        "oil_painting": ", oil painting style, brushstrokes visible, classical art, rich colors",
        "watercolor": ", watercolor painting, soft edges, flowing colors, artistic",
        "sketch": ", pencil sketch, hand-drawn, black and white, artistic drawing",
        "3d_render": ", 3D render, CGI, Blender style, octane render, realistic lighting",
        "pixel_art": ", pixel art, 8-bit style, retro game graphics, pixelated",
        "minimalist": ", minimalist design, clean lines, simple shapes, modern",
        "surreal": ", surrealist art, dreamlike, Salvador Dali style, impossible scenes",
        "vintage": ", vintage style, retro, old photograph, sepia tones, nostalgic",
        "neon": ", neon lights, cyberpunk style, glowing colors, dark background, futuristic",
    }
    
    # Rename pattern placeholders
    RENAME_PLACEHOLDERS = {
        "{original}": "Nom original de l'image",
        "{num}": "Numéro séquentiel (001, 002...)",
        "{date}": "Date du traitement (YYYYMMDD)",
        "{time}": "Heure du traitement (HHMMSS)",
    }

    
    def __init__(self):
        """Initialize configuration."""
        self._config_dir = self._get_config_dir()
        self._config_file = self._config_dir / "config.json"
        self._config = self.DEFAULTS.copy()
        self._secure_storage = SecureKeyStorage(self._config_dir)
        self.load()
    
    def _get_config_dir(self) -> Path:
        """Get the configuration directory path (cross-platform)."""
        if os.name == 'nt':  # Windows
            base = Path(os.environ.get('APPDATA', Path.home()))
        else:  # Linux/Mac
            base = Path.home() / ".config"
        
        config_dir = base / "pixelforge-studio"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load(self) -> None:
        """Load configuration from file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Remove api_key from loaded config if present (migrating from old version)
                    loaded.pop("api_key", None)
                    # Merge with defaults to handle new config keys
                    self._config = {**self.DEFAULTS, **loaded}
            except (json.JSONDecodeError, IOError):
                self._config = self.DEFAULTS.copy()
    
    def save(self) -> None:
        """Save configuration to file (API key is stored separately)."""
        try:
            # Never save API key to config file
            save_config = {k: v for k, v in self._config.items() if k != "api_key"}
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self._config.get(key, default if default is not None else self.DEFAULTS.get(key))
    
    def set(self, key: str, value) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    @property
    def api_key(self) -> str:
        """Get the API key from secure storage."""
        return self._secure_storage.get_api_key()
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        """Set the API key in secure storage."""
        self._secure_storage.set_api_key(value)
    
    @property
    def api_key_storage_method(self) -> str:
        """Get the method used to store the API key."""
        return self._secure_storage.storage_method
    
    @property
    def output_folder(self) -> str:
        """Get the output folder path."""
        return self.get("output_folder", "")
    
    @output_folder.setter
    def output_folder(self, value: str) -> None:
        """Set the output folder path."""
        self.set("output_folder", value)
    
    @property
    def model(self) -> str:
        """Get the selected model."""
        return self.get("model", "gemini-2.5-flash-image")
    
    @model.setter
    def model(self, value: str) -> None:
        """Set the selected model."""
        self.set("model", value)
    
    @property
    def aspect_ratio(self) -> str:
        """Get the selected aspect ratio."""
        return self.get("aspect_ratio", "1:1")
    
    @aspect_ratio.setter
    def aspect_ratio(self, value: str) -> None:
        """Set the selected aspect ratio."""
        self.set("aspect_ratio", value)
    
    @property
    def last_input_folder(self) -> str:
        """Get the last used input folder."""
        return self.get("last_input_folder", "")
    
    @last_input_folder.setter
    def last_input_folder(self, value: str) -> None:
        """Set the last used input folder."""
        self.set("last_input_folder", value)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
