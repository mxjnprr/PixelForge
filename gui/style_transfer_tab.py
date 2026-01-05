"""
Style transfer tab for applying the style of one image to another.
Allows users to load a source image and a style reference image.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QGroupBox, QFormLayout, QFileDialog,
    QFrame, QMessageBox, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont, QImage

from utils.config import get_config, Config


class ImageDropLabel(QLabel):
    """A label that displays an image and accepts drops."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._image_path: str = ""
        self._pixmap: Optional[QPixmap] = None
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(250, 250)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._show_placeholder()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _show_placeholder(self):
        """Show placeholder text."""
        self.setText(f"📷 {self._title}\n\nCliquez pour charger")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px dashed #444;
                border-radius: 8px;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #ff6b35;
            }
        """)
    
    def set_image(self, path: str) -> bool:
        """Load and display an image."""
        if not path or not Path(path).exists():
            return False
        
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return False
        
        self._image_path = path
        self._pixmap = pixmap
        self._update_display()
        return True
    
    def _update_display(self):
        """Update the displayed image."""
        if self._pixmap is None:
            return
        
        # Scale to fit
        scaled = self._pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 8px;
            }
            QLabel:hover {
                border-color: #ff6b35;
            }
        """)
    
    def get_image_path(self) -> str:
        """Get the path to the loaded image."""
        return self._image_path
    
    def has_image(self) -> bool:
        """Check if an image is loaded."""
        return self._pixmap is not None
    
    def clear(self):
        """Clear the image."""
        self._image_path = ""
        self._pixmap = None
        self._show_placeholder()
    
    def resizeEvent(self, event):
        """Handle resize."""
        super().resizeEvent(event)
        if self._pixmap is not None:
            self._update_display()


class StyleTransferTab(QWidget):
    """
    Tab for style transfer - applying style from one image to another.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = get_config()
        self._result_image_path: Optional[str] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("🎨 Transfert de Style")
        header.setFont(QFont("", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #ff6b35;")
        main_layout.addWidget(header)
        
        description = QLabel(
            "Appliquez la texture, la couleur et le style d'une image de référence sur votre image source. "
            "C'est le moyen le plus simple de tester différentes esthétiques."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #888; margin-bottom: 10px;")
        main_layout.addWidget(description)
        
        # Images row
        images_layout = QHBoxLayout()
        images_layout.setSpacing(20)
        
        # Source image
        source_group = QGroupBox("Image Source")
        source_layout = QVBoxLayout(source_group)
        
        self._source_label = ImageDropLabel("Image à transformer")
        source_layout.addWidget(self._source_label)
        
        self._load_source_btn = QPushButton("📂 Charger l'image source")
        self._load_source_btn.setMinimumHeight(35)
        source_layout.addWidget(self._load_source_btn)
        
        images_layout.addWidget(source_group)
        
        # Arrow
        arrow_label = QLabel("➜")
        arrow_label.setFont(QFont("", 24))
        arrow_label.setStyleSheet("color: #ff6b35;")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label.setFixedWidth(50)
        images_layout.addWidget(arrow_label)
        
        # Style image
        style_group = QGroupBox("Image de Style")
        style_layout = QVBoxLayout(style_group)
        
        self._style_label = ImageDropLabel("Style à appliquer")
        style_layout.addWidget(self._style_label)
        
        self._load_style_btn = QPushButton("📂 Charger l'image de style")
        self._load_style_btn.setMinimumHeight(35)
        style_layout.addWidget(self._load_style_btn)
        
        images_layout.addWidget(style_group)
        
        # Arrow
        arrow_label2 = QLabel("=")
        arrow_label2.setFont(QFont("", 24))
        arrow_label2.setStyleSheet("color: #ff6b35;")
        arrow_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label2.setFixedWidth(50)
        images_layout.addWidget(arrow_label2)
        
        # Result
        result_group = QGroupBox("Résultat")
        result_layout = QVBoxLayout(result_group)
        
        self._result_label = QLabel("Le résultat apparaîtra ici")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_label.setMinimumSize(250, 250)
        self._result_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._result_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px dashed #444;
                border-radius: 8px;
                color: #666;
            }
        """)
        self._result_label.setCursor(Qt.CursorShape.PointingHandCursor)
        result_layout.addWidget(self._result_label)
        
        images_layout.addWidget(result_group)
        
        main_layout.addLayout(images_layout, stretch=1)
        
        # Options row
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        
        # Prompt (optional)
        prompt_group = QGroupBox("Instructions supplémentaires (optionnel)")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlaceholderText(
            "Instructions supplémentaires pour guider le transfert de style...\n\n"
            "Exemples:\n"
            "• Garde les couleurs mais change la texture\n"
            "• Applique uniquement le style artistique\n"
            "• Conserve les détails du visage"
        )
        self._prompt_edit.setMaximumHeight(100)
        prompt_layout.addWidget(self._prompt_edit)
        
        options_layout.addWidget(prompt_group, stretch=2)
        
        # Config
        config_group = QGroupBox("Configuration")
        config_form = QFormLayout(config_group)
        
        self._model_combo = QComboBox()
        for model_id, model_name in Config.MODELS:
            self._model_combo.addItem(model_name, model_id)
        config_form.addRow("Modèle:", self._model_combo)
        
        self._quality_combo = QComboBox()
        for quality_id, quality_name in Config.OUTPUT_QUALITIES:
            self._quality_combo.addItem(quality_name, quality_id)
        config_form.addRow("Qualité:", self._quality_combo)
        
        self._strength_combo = QComboBox()
        self._strength_combo.addItem("Subtil (textures légères)", "subtle")
        self._strength_combo.addItem("Modéré (équilibré)", "moderate")
        self._strength_combo.addItem("Fort (style dominant)", "strong")
        self._strength_combo.setCurrentIndex(1)
        config_form.addRow("Intensité:", self._strength_combo)
        
        options_layout.addWidget(config_group, stretch=1)
        
        main_layout.addLayout(options_layout)
        
        # Apply button
        self._apply_btn = QPushButton("🎨 Appliquer le style")
        self._apply_btn.setFont(QFont("", 12, QFont.Weight.Bold))
        self._apply_btn.setMinimumHeight(50)
        self._apply_btn.setEnabled(False)
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #ff8555;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        main_layout.addWidget(self._apply_btn)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self._load_source_btn.clicked.connect(self._load_source_image)
        self._load_style_btn.clicked.connect(self._load_style_image)
        self._source_label.mousePressEvent = lambda e: self._load_source_image()
        self._style_label.mousePressEvent = lambda e: self._load_style_image()
        self._apply_btn.clicked.connect(self._apply_style_transfer)
        self._result_label.mousePressEvent = self._on_result_click
    
    def _update_apply_button(self):
        """Update the apply button state."""
        can_apply = self._source_label.has_image() and self._style_label.has_image()
        self._apply_btn.setEnabled(can_apply)
    
    def _load_source_image(self):
        """Load the source image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner l'image source",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Tous les fichiers (*)"
        )
        if file_path:
            if not self._source_label.set_image(file_path):
                QMessageBox.warning(self, "Erreur", "Impossible de charger l'image.")
            self._update_apply_button()
    
    def _load_style_image(self):
        """Load the style reference image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner l'image de style",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Tous les fichiers (*)"
        )
        if file_path:
            if not self._style_label.set_image(file_path):
                QMessageBox.warning(self, "Erreur", "Impossible de charger l'image.")
            self._update_apply_button()
    
    def _apply_style_transfer(self):
        """Apply style transfer using the API."""
        from api_client import NanoBananaClient
        from datetime import datetime
        
        # Get API key
        api_key = self._config.api_key
        if not api_key:
            QMessageBox.warning(
                self,
                "Attention",
                "Clé API non configurée. Allez dans l'onglet Paramètres."
            )
            return
        
        if not self._source_label.has_image() or not self._style_label.has_image():
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez charger les deux images (source et style)."
            )
            return
        
        # Build prompt based on strength
        strength = self._strength_combo.currentData()
        user_prompt = self._prompt_edit.toPlainText().strip()
        
        if strength == "subtle":
            base_prompt = (
                "Applique subtilement la texture et les nuances de couleur de la deuxième image "
                "sur la première image. Conserve la structure et les détails de l'image source, "
                "en ajoutant seulement une légère influence du style."
            )
        elif strength == "strong":
            base_prompt = (
                "Transforme complètement la première image en adoptant le style artistique, "
                "les couleurs, les textures et l'ambiance de la deuxième image. "
                "Le résultat doit être une fusion où le style domine fortement."
            )
        else:  # moderate
            base_prompt = (
                "Applique le style, les couleurs et la texture de la deuxième image "
                "sur la première image de manière équilibrée. "
                "Conserve les éléments reconnaissables de l'image source tout en adoptant l'esthétique du style."
            )
        
        if user_prompt:
            full_prompt = f"{base_prompt}\n\nInstructions supplémentaires: {user_prompt}"
        else:
            full_prompt = base_prompt
        
        # Disable button during processing
        self._apply_btn.setEnabled(False)
        self._apply_btn.setText("⏳ Traitement en cours...")
        QApplication.processEvents()
        
        try:
            client = NanoBananaClient(api_key)
            
            # Use style transfer method
            result_bytes, error_msg = client.style_transfer(
                source_image_path=self._source_label.get_image_path(),
                style_image_path=self._style_label.get_image_path(),
                prompt=full_prompt,
                model=self._model_combo.currentData(),
                output_quality=self._quality_combo.currentData()
            )
            
            if result_bytes and not error_msg:
                # Save result
                source_path = Path(self._source_label.get_image_path())
                output_dir = source_path.parent
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{source_path.stem}_styled_{timestamp}.png"
                output_path = output_dir / output_name
                
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                
                self._result_image_path = str(output_path)
                
                # Show preview
                result_pixmap = QPixmap(str(output_path))
                if not result_pixmap.isNull():
                    scaled = result_pixmap.scaled(
                        self._result_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self._result_label.setPixmap(scaled)
                    self._result_label.setStyleSheet("""
                        QLabel {
                            background-color: #1a1a1a;
                            border: 2px solid #ff6b35;
                            border-radius: 8px;
                        }
                    """)
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Image créée:\n{output_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors du transfert de style:\n{error_msg or 'Erreur inconnue'}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du traitement:\n{str(e)}"
            )
        
        finally:
            self._apply_btn.setEnabled(True)
            self._apply_btn.setText("🎨 Appliquer le style")
            self._update_apply_button()
    
    def _on_result_click(self, event):
        """Open result image in system viewer."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        if not self._result_image_path:
            return
        
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Darwin':
                subprocess.run(['open', self._result_image_path])
            elif platform.system() == 'Windows':
                subprocess.run(['start', '', self._result_image_path], shell=True)
            else:
                subprocess.run(['xdg-open', self._result_image_path])
        except Exception as e:
            print(f"Error opening image: {e}")
