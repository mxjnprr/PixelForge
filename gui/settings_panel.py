"""
Settings panel for API configuration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from utils.config import get_config
from api_client import NanoBananaClient


class SettingsPanel(QWidget):
    """Panel for configuring API settings."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = get_config()
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # API Configuration Group
        api_group = QGroupBox("Configuration API")
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(15)
        
        # API Key
        api_key_layout = QHBoxLayout()
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("Entrez votre clé API Gemini...")
        api_key_layout.addWidget(self._api_key_edit)
        
        self._toggle_key_btn = QPushButton("👁")
        self._toggle_key_btn.setFixedWidth(35)
        self._toggle_key_btn.setCheckable(True)
        self._toggle_key_btn.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(self._toggle_key_btn)
        
        self._test_key_btn = QPushButton("Tester")
        self._test_key_btn.clicked.connect(self._test_api_key)
        api_key_layout.addWidget(self._test_key_btn)
        
        api_layout.addRow("Clé API:", api_key_layout)
        
        # Storage method indicator
        storage_method = self._config.api_key_storage_method
        storage_label = QLabel(f"🔒 {storage_method}")
        storage_label.setStyleSheet("color: #4a9; font-size: 11px;")
        api_layout.addRow("Stockage:", storage_label)
        
        layout.addWidget(api_group)
        
        # Info section
        info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            'Obtenez une clé API gratuite sur Google AI Studio:<br>'
            '<a href="https://aistudio.google.com/app/apikey" style="color: #ff6b35;">'
            'https://aistudio.google.com/app/apikey</a><br><br>'
            'Votre clé API est stockée de manière sécurisée<br>'
            'dans le trousseau de votre système.'
        )
        info_text.setStyleSheet("color: #888; font-size: 11px;")
        info_text.setWordWrap(True)
        info_text.setOpenExternalLinks(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        # Save button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self._save_btn = QPushButton("💾 Sauvegarder")
        self._save_btn.setMinimumWidth(150)
        self._save_btn.clicked.connect(self._save_settings)
        save_layout.addWidget(self._save_btn)
        
        layout.addLayout(save_layout)
        layout.addStretch()
    
    def _load_settings(self):
        """Load settings from config."""
        self._api_key_edit.setText(self._config.api_key)
    
    def _save_settings(self):
        """Save settings to config."""
        self._config.api_key = self._api_key_edit.text().strip()
        self._config.save()
        
        self.settings_changed.emit()
        QMessageBox.information(self, "Paramètres", "Clé API sauvegardée avec succès!")
    
    def _toggle_api_key_visibility(self, checked: bool):
        """Toggle API key visibility."""
        if checked:
            self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_key_btn.setText("🔒")
        else:
            self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_key_btn.setText("👁")
    
    def _test_api_key(self):
        """Test the API key."""
        api_key = self._api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Test API", "Veuillez entrer une clé API.")
            return
        
        self._test_key_btn.setEnabled(False)
        self._test_key_btn.setText("Test...")
        
        try:
            client = NanoBananaClient(api_key)
            success, message = client.test_connection()
            
            if success:
                QMessageBox.information(self, "Test API", f"✅ {message}")
            else:
                QMessageBox.warning(self, "Test API", f"❌ {message}")
        except Exception as e:
            QMessageBox.critical(self, "Test API", f"Erreur: {e}")
        finally:
            self._test_key_btn.setEnabled(True)
            self._test_key_btn.setText("Tester")
    
    # Public accessor for API key
    @property
    def api_key(self) -> str:
        return self._api_key_edit.text().strip()
