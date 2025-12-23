"""
Progress dialog for batch processing.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Dialog showing batch processing progress."""
    
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Traitement en cours...")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        # Prevent closing with X button during processing
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(self)
        
        # Status label
        self._status_label = QLabel("Initialisation...")
        self._status_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(self._status_label)
        
        # Current image label
        self._current_image_label = QLabel("")
        self._current_image_label.setWordWrap(True)
        layout.addWidget(self._current_image_label)
        
        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)
        
        # Progress text
        self._progress_text = QLabel("0 / 0")
        self._progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._progress_text)
        
        # Log area
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(150)
        self._log_text.setStyleSheet("font-family: monospace; font-size: 10px;")
        layout.addWidget(self._log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self._cancel_btn = QPushButton("Annuler")
        self._cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self._cancel_btn)
        
        self._close_btn = QPushButton("Fermer")
        self._close_btn.clicked.connect(self.accept)
        self._close_btn.setVisible(False)
        button_layout.addWidget(self._close_btn)
        
        layout.addLayout(button_layout)
    
    def set_total(self, total: int):
        """Set the total number of items to process."""
        self._progress_bar.setMaximum(total)
        self._progress_text.setText(f"0 / {total}")
    
    def update_progress(self, current: int, total: int):
        """Update the progress bar."""
        self._progress_bar.setValue(current)
        self._progress_text.setText(f"{current} / {total}")
        percent = int((current / total) * 100) if total > 0 else 0
        self.setWindowTitle(f"Traitement en cours... ({percent}%)")
    
    def set_current_image(self, path: str):
        """Set the currently processing image."""
        self._current_image_label.setText(f"Image en cours: {path}")
        self._status_label.setText("Traitement en cours...")
    
    def log_message(self, message: str, is_error: bool = False):
        """Add a message to the log."""
        if is_error:
            self._log_text.append(f"❌ {message}")
        else:
            self._log_text.append(f"✅ {message}")
        
        # Scroll to bottom
        scrollbar = self._log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_completed(self, success_count: int, error_count: int):
        """Mark the processing as completed."""
        total = success_count + error_count
        self._status_label.setText("Traitement terminé!")
        self._current_image_label.setText(
            f"Résultat: {success_count} réussites, {error_count} erreurs sur {total} images"
        )
        self._progress_bar.setValue(self._progress_bar.maximum())
        
        self._cancel_btn.setVisible(False)
        self._close_btn.setVisible(True)
        
        # Allow closing
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowCloseButtonHint
        )
        self.show()  # Refresh window flags
    
    def set_error(self, message: str):
        """Set an error state."""
        self._status_label.setText("Erreur!")
        self._current_image_label.setText(message)
        
        self._cancel_btn.setVisible(False)
        self._close_btn.setVisible(True)
        
        # Allow closing
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowCloseButtonHint
        )
        self.show()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self._is_cancelled = True
        self._status_label.setText("Annulation en cours...")
        self._cancel_btn.setEnabled(False)
        self.cancel_requested.emit()
    
    @property
    def is_cancelled(self) -> bool:
        """Check if processing was cancelled."""
        return self._is_cancelled
