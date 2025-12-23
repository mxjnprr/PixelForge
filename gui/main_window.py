"""
Main window for PixelForge Studio.
"""

from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QTextEdit, QPushButton, QTabWidget, QLineEdit, QComboBox,
    QMessageBox, QStatusBar, QGroupBox, QFileDialog, QSpinBox,
    QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap

from gui.image_list import ImageListWidget
from gui.settings_panel import SettingsPanel
from gui.progress_dialog import ProgressDialog
from api_client import NanoBananaClient
from batch_processor import BatchProcessor, BatchJob, ImageStatus, ImageItem
from utils.config import get_config, Config


class ImagePreviewWidget(QFrame):
    """Widget to display a generated image preview."""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ImagePreviewWidget {
                background-color: #2a2a2a; 
                border-radius: 8px; 
                padding: 5px;
            }
            ImagePreviewWidget:hover {
                background-color: #3a3a3a;
                border: 1px solid #ff6b35;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Image
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumSize(150, 150)
        self._image_label.setMaximumSize(200, 200)
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                180, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._image_label.setPixmap(scaled)
        
        layout.addWidget(self._image_label)
        
        # Filename
        filename = Path(image_path).name
        name_label = QLabel(filename[:20] + "..." if len(filename) > 20 else filename)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(name_label)
    
    def mousePressEvent(self, event):
        """Open the image with the system default viewer."""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.image_path])
            elif platform.system() == 'Windows':
                subprocess.run(['start', '', self.image_path], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.image_path])
        except Exception as e:
            print(f"Error opening image: {e}")
        
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self._config = get_config()
        self._client: Optional[NanoBananaClient] = None
        self._processor = BatchProcessor(self)
        self._progress_dialog: Optional[ProgressDialog] = None
        self._generated_previews: List[ImagePreviewWidget] = []
        
        self._setup_ui()
        self._connect_signals()
        self._initialize_client()
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(f"🔥 {Config.APP_NAME}")
        self.setMinimumSize(1100, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"🔥 {Config.APP_NAME}")
        title_label.setFont(QFont("", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ff6b35;")
        header_layout.addWidget(title_label)
        
        subtitle = QLabel("Éditez et générez des images avec Nano Banana de Google")
        subtitle.setStyleSheet("color: #888; font-size: 12px;")
        header_layout.addWidget(subtitle)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self._tab_widget = QTabWidget()
        
        # === Processing Tab (Edit Images) ===
        self._setup_processing_tab()
        
        # === Generation Tab ===
        self._setup_generation_tab()
        
        # === Settings Tab (API only) ===
        self._settings_panel = SettingsPanel()
        self._tab_widget.addTab(self._settings_panel, "⚙️ Paramètres")
        
        main_layout.addWidget(self._tab_widget)
        
        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._update_status("Prêt")
    
    def _setup_processing_tab(self):
        """Set up the image processing tab."""
        processing_tab = QWidget()
        processing_layout = QHBoxLayout(processing_tab)
        processing_layout.setContentsMargins(10, 10, 10, 10)
        processing_layout.setSpacing(15)
        
        # Left side: Images + Prompt
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Image list
        self._image_list = ImageListWidget()
        left_layout.addWidget(self._image_list, stretch=3)
        
        # Prompt section
        prompt_group = QGroupBox("Prompt (appliqué à toutes les images)")
        prompt_group_layout = QVBoxLayout(prompt_group)
        
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlaceholderText(
            "Décrivez la transformation à appliquer...\n\n"
            "Exemples:\n"
            "• Transforme en style aquarelle\n"
            "• Ajoute un arrière-plan de coucher de soleil\n"
            "• Change le style en illustration cartoon"
        )
        self._prompt_edit.setMaximumHeight(100)
        prompt_group_layout.addWidget(self._prompt_edit)
        
        left_layout.addWidget(prompt_group)
        
        processing_layout.addWidget(left_widget, stretch=2)
        
        # Right side: Output configuration
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Output config group
        output_group = QGroupBox("Configuration de sortie")
        output_form = QFormLayout(output_group)
        
        # Model
        self._model_combo = QComboBox()
        for model_id, model_name in Config.MODELS:
            self._model_combo.addItem(model_name, model_id)
        model_index = self._model_combo.findData(self._config.model)
        if model_index >= 0:
            self._model_combo.setCurrentIndex(model_index)
        output_form.addRow("Modèle:", self._model_combo)
        
        # Style preset
        self._style_combo = QComboBox()
        for style_id, style_name in Config.STYLE_PRESETS:
            self._style_combo.addItem(style_name, style_id)
        output_form.addRow("Style:", self._style_combo)
        
        # Aspect ratio
        self._aspect_ratio_combo = QComboBox()
        for ratio_id, ratio_name in Config.ASPECT_RATIOS:
            self._aspect_ratio_combo.addItem(ratio_name, ratio_id)
        ratio_index = self._aspect_ratio_combo.findData(self._config.aspect_ratio)
        if ratio_index >= 0:
            self._aspect_ratio_combo.setCurrentIndex(ratio_index)
        output_form.addRow("Ratio:", self._aspect_ratio_combo)
        
        # Quality
        self._quality_combo = QComboBox()
        for quality_id, quality_name in Config.OUTPUT_QUALITIES:
            self._quality_combo.addItem(quality_name, quality_id)
        quality_index = self._quality_combo.findData(self._config.get("output_quality", "standard"))
        if quality_index >= 0:
            self._quality_combo.setCurrentIndex(quality_index)
        output_form.addRow("Qualité:", self._quality_combo)
        
        # Rename pattern
        self._rename_edit = QLineEdit()
        self._rename_edit.setText(self._config.get("rename_pattern", "{original}_processed"))
        self._rename_edit.setPlaceholderText("{original}_processed")
        rename_help = QLabel("{original}, {num}, {date}, {time}")
        rename_help.setStyleSheet("color: #888; font-size: 9px;")
        rename_layout = QVBoxLayout()
        rename_layout.setSpacing(2)
        rename_layout.addWidget(self._rename_edit)
        rename_layout.addWidget(rename_help)
        output_form.addRow("Renommage:", rename_layout)
        
        # Output folder
        folder_layout = QHBoxLayout()
        self._output_folder_edit = QLineEdit()
        self._output_folder_edit.setText(self._config.output_folder)
        self._output_folder_edit.setPlaceholderText("À côté des originaux")
        folder_layout.addWidget(self._output_folder_edit)
        
        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(30)
        browse_btn.clicked.connect(self._browse_output_folder)
        folder_layout.addWidget(browse_btn)
        output_form.addRow("Dossier:", folder_layout)
        
        right_layout.addWidget(output_group)
        
        # Process button
        self._process_btn = QPushButton("🚀 Lancer le traitement")
        self._process_btn.setFont(QFont("", 12, QFont.Weight.Bold))
        self._process_btn.setMinimumHeight(50)
        self._process_btn.clicked.connect(self._start_processing)
        self._process_btn.setEnabled(False)
        right_layout.addWidget(self._process_btn)
        
        right_layout.addStretch()
        
        processing_layout.addWidget(right_widget, stretch=1)
        
        self._tab_widget.addTab(processing_tab, "📷 Édition")
    
    def _setup_generation_tab(self):
        """Set up the image generation tab."""
        generation_tab = QWidget()
        generation_layout = QVBoxLayout(generation_tab)
        generation_layout.setContentsMargins(10, 10, 10, 10)
        generation_layout.setSpacing(15)
        
        # Top: Config and Prompt
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Prompt
        prompt_group = QGroupBox("Prompt de génération")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self._gen_prompt_edit = QTextEdit()
        self._gen_prompt_edit.setPlaceholderText(
            "Décrivez l'image à générer...\n\n"
            "Exemples:\n"
            "• Un chat astronaute sur la lune\n"
            "• Une forêt enchantée au coucher du soleil\n"
            "• Logo minimaliste pour une startup tech"
        )
        self._gen_prompt_edit.setMaximumHeight(120)
        prompt_layout.addWidget(self._gen_prompt_edit)
        
        top_layout.addWidget(prompt_group, stretch=2)
        
        # Right: Config
        config_group = QGroupBox("Configuration")
        config_form = QFormLayout(config_group)
        
        # Style preset for generation
        self._gen_style_combo = QComboBox()
        for style_id, style_name in Config.STYLE_PRESETS:
            self._gen_style_combo.addItem(style_name, style_id)
        config_form.addRow("Style:", self._gen_style_combo)
        
        # Model for generation
        self._gen_model_combo = QComboBox()
        for model_id, model_name in Config.MODELS:
            self._gen_model_combo.addItem(model_name, model_id)
        config_form.addRow("Modèle:", self._gen_model_combo)
        
        # Aspect ratio for generation
        self._gen_aspect_combo = QComboBox()
        for ratio_id, ratio_name in Config.ASPECT_RATIOS:
            if ratio_id != "original":
                self._gen_aspect_combo.addItem(ratio_name, ratio_id)
        config_form.addRow("Ratio:", self._gen_aspect_combo)
        
        # Quality for generation
        self._gen_quality_combo = QComboBox()
        for quality_id, quality_name in Config.OUTPUT_QUALITIES:
            self._gen_quality_combo.addItem(quality_name, quality_id)
        config_form.addRow("Qualité:", self._gen_quality_combo)
        
        # Number of images
        self._gen_count_spin = QSpinBox()
        self._gen_count_spin.setMinimum(1)
        self._gen_count_spin.setMaximum(10)
        self._gen_count_spin.setValue(1)
        config_form.addRow("Nombre:", self._gen_count_spin)
        
        # Output folder
        gen_folder_layout = QHBoxLayout()
        self._gen_output_folder_edit = QLineEdit()
        self._gen_output_folder_edit.setPlaceholderText("Dossier de sortie...")
        gen_folder_layout.addWidget(self._gen_output_folder_edit)
        
        gen_browse_btn = QPushButton("...")
        gen_browse_btn.setFixedWidth(30)
        gen_browse_btn.clicked.connect(self._browse_gen_output_folder)
        gen_folder_layout.addWidget(gen_browse_btn)
        config_form.addRow("Dossier:", gen_folder_layout)
        
        # Filename prefix
        self._gen_prefix_edit = QLineEdit()
        self._gen_prefix_edit.setText("generated")
        config_form.addRow("Préfixe:", self._gen_prefix_edit)
        
        top_layout.addWidget(config_group, stretch=1)
        
        generation_layout.addWidget(top_widget)
        
        # Generate button
        btn_layout = QHBoxLayout()
        self._generate_btn = QPushButton("✨ Générer les images")
        self._generate_btn.setFont(QFont("", 12, QFont.Weight.Bold))
        self._generate_btn.setMinimumHeight(45)
        self._generate_btn.setMinimumWidth(200)
        self._generate_btn.clicked.connect(self._start_generation)
        btn_layout.addStretch()
        btn_layout.addWidget(self._generate_btn)
        btn_layout.addStretch()
        generation_layout.addLayout(btn_layout)
        
        # Preview area
        preview_group = QGroupBox("Aperçus des images générées")
        preview_group_layout = QVBoxLayout(preview_group)
        
        self._preview_scroll = QScrollArea()
        self._preview_scroll.setWidgetResizable(True)
        self._preview_scroll.setMinimumHeight(250)
        self._preview_scroll.setStyleSheet("background-color: #1a1a1a; border-radius: 8px;")
        
        self._preview_container = QWidget()
        self._preview_grid = QGridLayout(self._preview_container)
        self._preview_grid.setSpacing(10)
        self._preview_grid.setContentsMargins(10, 10, 10, 10)
        
        # Placeholder
        self._preview_placeholder = QLabel("Les images générées apparaîtront ici")
        self._preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_placeholder.setStyleSheet("color: #666; font-size: 14px;")
        self._preview_grid.addWidget(self._preview_placeholder, 0, 0)
        
        self._preview_scroll.setWidget(self._preview_container)
        preview_group_layout.addWidget(self._preview_scroll)
        
        generation_layout.addWidget(preview_group, stretch=1)
        
        self._tab_widget.addTab(generation_tab, "✨ Génération")
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self._image_list.images_changed.connect(self._on_images_changed)
        self._settings_panel.settings_changed.connect(self._on_settings_changed)
        self._processor.progress.connect(self._on_progress)
        self._processor.image_started.connect(self._on_image_started)
        self._processor.image_completed.connect(self._on_image_completed)
        self._processor.batch_completed.connect(self._on_batch_completed)
        self._processor.error.connect(self._on_error)
    
    def _initialize_client(self):
        """Initialize the API client if we have an API key."""
        api_key = self._config.api_key
        if api_key:
            try:
                self._client = NanoBananaClient(api_key)
                self._processor.set_client(self._client)
                self._update_status("Client API initialisé")
            except Exception as e:
                self._update_status(f"Erreur d'initialisation: {e}")
        else:
            self._update_status("⚠️ Clé API non configurée - Allez dans Paramètres")
    
    def _on_images_changed(self):
        """Handle image list changes."""
        count = self._image_list.get_image_count()
        has_images = count > 0
        has_api_key = bool(self._settings_panel.api_key)
        
        self._process_btn.setEnabled(has_images and has_api_key)
        
        if has_images:
            self._update_status(f"{count} image(s) sélectionnée(s)")
        else:
            self._update_status("Prêt")
    
    def _on_settings_changed(self):
        """Handle settings changes."""
        self._initialize_client()
        self._on_images_changed()
    
    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier de sortie",
            self._output_folder_edit.text()
        )
        if folder:
            self._output_folder_edit.setText(folder)
    
    def _browse_gen_output_folder(self):
        """Browse for generation output folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Sélectionner le dossier de sortie",
            self._gen_output_folder_edit.text()
        )
        if folder:
            self._gen_output_folder_edit.setText(folder)
    
    def _get_styled_prompt(self, prompt: str, style_id: str) -> str:
        """Add style suffix to prompt if a style is selected."""
        style_suffix = Config.STYLE_PROMPTS.get(style_id, "")
        return prompt + style_suffix
    
    def _start_processing(self):
        """Start batch processing."""
        prompt = self._prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un prompt.")
            return
        
        if not self._settings_panel.api_key:
            QMessageBox.warning(
                self, "Attention", 
                "Clé API non configurée. Allez dans l'onglet Paramètres."
            )
            self._tab_widget.setCurrentIndex(2)
            return
        
        # Apply style to prompt
        style_id = self._style_combo.currentData()
        styled_prompt = self._get_styled_prompt(prompt, style_id)
        
        # Reinitialize client
        try:
            self._client = NanoBananaClient(self._settings_panel.api_key)
            self._processor.set_client(self._client)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'initialisation: {e}")
            return
        
        images = self._image_list.get_image_items()
        if not images:
            QMessageBox.warning(self, "Attention", "Aucune image à traiter.")
            return
        
        self._image_list.reset_all_statuses()
        
        job = BatchJob(
            images=images,
            prompt=styled_prompt,
            model=self._model_combo.currentData(),
            aspect_ratio=self._aspect_ratio_combo.currentData(),
            output_quality=self._quality_combo.currentData(),
            rename_pattern=self._rename_edit.text().strip() or "{original}_processed",
            output_folder=self._output_folder_edit.text().strip()
        )
        
        self._progress_dialog = ProgressDialog(self)
        self._progress_dialog.set_total(len(images))
        self._progress_dialog.cancel_requested.connect(self._processor.cancel)
        
        if self._processor.start_batch(job):
            self._process_btn.setEnabled(False)
            self._progress_dialog.show()
        else:
            self._progress_dialog = None
    
    def _clear_previews(self):
        """Clear all preview widgets."""
        for preview in self._generated_previews:
            preview.deleteLater()
        self._generated_previews.clear()
        
        # Re-add placeholder
        self._preview_placeholder = QLabel("Les images générées apparaîtront ici")
        self._preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_placeholder.setStyleSheet("color: #666; font-size: 14px;")
        self._preview_grid.addWidget(self._preview_placeholder, 0, 0)
    
    def _add_preview(self, image_path: str):
        """Add a preview widget for a generated image."""
        # Remove placeholder if present
        if self._preview_placeholder:
            self._preview_placeholder.deleteLater()
            self._preview_placeholder = None
        
        preview = ImagePreviewWidget(image_path)
        self._generated_previews.append(preview)
        
        # Calculate grid position
        count = len(self._generated_previews)
        cols = 5
        row = (count - 1) // cols
        col = (count - 1) % cols
        
        self._preview_grid.addWidget(preview, row, col)
    
    def _start_generation(self):
        """Start image generation."""
        prompt = self._gen_prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un prompt.")
            return
        
        if not self._settings_panel.api_key:
            QMessageBox.warning(
                self, "Attention", 
                "Clé API non configurée. Allez dans l'onglet Paramètres."
            )
            self._tab_widget.setCurrentIndex(2)
            return
        
        output_folder = self._gen_output_folder_edit.text().strip()
        if not output_folder:
            QMessageBox.warning(self, "Attention", "Veuillez choisir un dossier de sortie.")
            return
        
        # Apply style to prompt
        style_id = self._gen_style_combo.currentData()
        styled_prompt = self._get_styled_prompt(prompt, style_id)
        
        # Initialize client
        try:
            self._client = NanoBananaClient(self._settings_panel.api_key)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur d'initialisation: {e}")
            return
        
        count = self._gen_count_spin.value()
        model = self._gen_model_combo.currentData()
        aspect_ratio = self._gen_aspect_combo.currentData()
        quality = self._gen_quality_combo.currentData()
        prefix = self._gen_prefix_edit.text().strip() or "generated"
        
        # Create output folder
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Clear previous previews
        self._clear_previews()
        
        # Show progress
        self._progress_dialog = ProgressDialog(self)
        self._progress_dialog.set_total(count)
        self._generate_btn.setEnabled(False)
        self._progress_dialog.show()
        
        # Generate images
        from datetime import datetime
        from PyQt6.QtWidgets import QApplication
        
        success_count = 0
        error_count = 0
        
        for i in range(count):
            if self._progress_dialog.is_cancelled:
                break
            
            self._progress_dialog.update_progress(i + 1, count)
            self._progress_dialog.set_current_image(f"Génération {i + 1}/{count}...")
            QApplication.processEvents()
            
            result_bytes, error_msg = self._client.generate_image(
                prompt=styled_prompt,
                model=model,
                aspect_ratio=aspect_ratio,
                output_quality=quality
            )
            
            if result_bytes and not error_msg:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{prefix}_{timestamp}_{i+1:03d}.png"
                filepath = output_path / filename
                
                with open(filepath, 'wb') as f:
                    f.write(result_bytes)
                
                success_count += 1
                self._progress_dialog.log_message(f"✅ {filename}")
                
                # Add preview
                self._add_preview(str(filepath))
                QApplication.processEvents()
            else:
                error_count += 1
                self._progress_dialog.log_message(f"❌ Erreur: {error_msg}", is_error=True)
        
        self._progress_dialog.set_completed(success_count, error_count)
        self._generate_btn.setEnabled(True)
        self._update_status(f"Génération terminée: {success_count}/{count}")
    
    def _on_progress(self, current: int, total: int):
        if self._progress_dialog:
            self._progress_dialog.update_progress(current, total)
    
    def _on_image_started(self, path: str):
        self._image_list.update_image_status(path, ImageStatus.PROCESSING)
        if self._progress_dialog:
            self._progress_dialog.set_current_image(path)
    
    def _on_image_completed(self, path: str, success: bool, message: str):
        if success:
            self._image_list.update_image_status(path, ImageStatus.SUCCESS, message)
            if self._progress_dialog:
                self._progress_dialog.log_message(f"{Path(path).name} → {Path(message).name}")
        else:
            self._image_list.update_image_status(path, ImageStatus.ERROR, message)
            if self._progress_dialog:
                self._progress_dialog.log_message(f"{Path(path).name}: {message}", is_error=True)
    
    def _on_batch_completed(self, success_count: int, error_count: int):
        self._process_btn.setEnabled(True)
        if self._progress_dialog:
            self._progress_dialog.set_completed(success_count, error_count)
        total = success_count + error_count
        self._update_status(f"Terminé: {success_count}/{total} réussites")
    
    def _on_error(self, message: str):
        self._process_btn.setEnabled(True)
        if self._progress_dialog:
            self._progress_dialog.set_error(message)
        else:
            QMessageBox.critical(self, "Erreur", message)
        self._update_status(f"Erreur: {message}")
    
    def _update_status(self, message: str):
        self._status_bar.showMessage(message)
