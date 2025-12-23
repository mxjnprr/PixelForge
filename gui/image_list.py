"""
Image list widget for displaying and managing images to process.
"""

from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFileDialog, QMenu, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent

from utils.image_utils import (
    create_thumbnail, get_supported_extensions, 
    filter_supported_images, validate_image
)
from utils.config import get_config
from batch_processor import ImageItem, ImageStatus


class ImageListWidget(QWidget):
    """Widget for displaying and managing a list of images."""
    
    images_changed = pyqtSignal()  # Emitted when images are added/removed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._images: Dict[str, ImageItem] = {}  # path -> ImageItem
        self._thumbnails: Dict[str, QIcon] = {}  # path -> thumbnail icon
        self._config = get_config()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        
        self._add_btn = QPushButton("➕ Ajouter des images")
        self._add_btn.clicked.connect(self._add_images)
        header_layout.addWidget(self._add_btn)
        
        self._clear_btn = QPushButton("🗑️ Vider la liste")
        self._clear_btn.clicked.connect(self.clear_images)
        header_layout.addWidget(self._clear_btn)
        
        header_layout.addStretch()
        
        self._count_label = QLabel("0 images")
        header_layout.addWidget(self._count_label)
        
        layout.addLayout(header_layout)
        
        # Image list
        self._list_widget = QListWidget()
        self._list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self._list_widget.setIconSize(QSize(120, 120))
        self._list_widget.setSpacing(10)
        self._list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_widget.customContextMenuRequested.connect(self._show_context_menu)
        
        # Enable drag and drop
        self._list_widget.setAcceptDrops(True)
        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        
        # Override drag/drop events
        self._list_widget.dragEnterEvent = self._drag_enter_event
        self._list_widget.dragMoveEvent = self._drag_move_event
        self._list_widget.dropEvent = self._drop_event
        
        layout.addWidget(self._list_widget)
        
        # Instructions label
        self._instructions_label = QLabel(
            "Glissez-déposez des images ici ou cliquez sur 'Ajouter des images'"
        )
        self._instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._instructions_label.setStyleSheet("color: #888; padding: 20px;")
        layout.addWidget(self._instructions_label)
        
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Update UI based on current state."""
        count = len(self._images)
        self._count_label.setText(f"{count} image{'s' if count != 1 else ''}")
        self._clear_btn.setEnabled(count > 0)
        self._instructions_label.setVisible(count == 0)
        self._list_widget.setVisible(count > 0)
    
    def _add_images(self):
        """Open file dialog to add images."""
        last_folder = self._config.last_input_folder or ""
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner des images",
            last_folder,
            get_supported_extensions()
        )
        
        if files:
            # Remember the folder
            self._config.last_input_folder = str(Path(files[0]).parent)
            self._config.save()
            
            self.add_images(files)
    
    def add_images(self, paths: List[str]):
        """
        Add images to the list.
        
        Args:
            paths: List of image file paths
        """
        valid_paths = filter_supported_images(paths)
        
        for path in valid_paths:
            if path in self._images:
                continue  # Skip duplicates
            
            is_valid, error = validate_image(path)
            if not is_valid:
                print(f"Skipping invalid image {path}: {error}")
                continue
            
            # Create image item
            image_item = ImageItem(path=path)
            self._images[path] = image_item
            
            # Create list item with thumbnail
            list_item = QListWidgetItem()
            list_item.setText(Path(path).name)
            list_item.setData(Qt.ItemDataRole.UserRole, path)
            list_item.setToolTip(path)
            
            # Generate thumbnail
            thumbnail_bytes = create_thumbnail(path, (120, 120))
            if thumbnail_bytes:
                pixmap = QPixmap()
                pixmap.loadFromData(thumbnail_bytes)
                icon = QIcon(pixmap)
                list_item.setIcon(icon)
                self._thumbnails[path] = icon
            
            self._list_widget.addItem(list_item)
        
        self._update_ui_state()
        self.images_changed.emit()
    
    def clear_images(self):
        """Remove all images from the list."""
        self._images.clear()
        self._thumbnails.clear()
        self._list_widget.clear()
        self._update_ui_state()
        self.images_changed.emit()
    
    def remove_selected(self):
        """Remove selected images from the list."""
        selected_items = self._list_widget.selectedItems()
        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path in self._images:
                del self._images[path]
            if path in self._thumbnails:
                del self._thumbnails[path]
            self._list_widget.takeItem(self._list_widget.row(item))
        
        self._update_ui_state()
        self.images_changed.emit()
    
    def get_image_items(self) -> List[ImageItem]:
        """Get all image items in order."""
        items = []
        for i in range(self._list_widget.count()):
            list_item = self._list_widget.item(i)
            path = list_item.data(Qt.ItemDataRole.UserRole)
            if path in self._images:
                items.append(self._images[path])
        return items
    
    def get_image_count(self) -> int:
        """Get the number of images."""
        return len(self._images)
    
    def update_image_status(self, path: str, status: ImageStatus, message: str = ""):
        """
        Update the status of an image.
        
        Args:
            path: Image path
            status: New status
            message: Optional status message
        """
        if path in self._images:
            self._images[path].status = status
            if status == ImageStatus.ERROR:
                self._images[path].error_message = message
            elif status == ImageStatus.SUCCESS:
                self._images[path].output_path = message
            
            # Update visual indicator
            for i in range(self._list_widget.count()):
                list_item = self._list_widget.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == path:
                    if status == ImageStatus.PROCESSING:
                        list_item.setText(f"⏳ {Path(path).name}")
                    elif status == ImageStatus.SUCCESS:
                        list_item.setText(f"✅ {Path(path).name}")
                    elif status == ImageStatus.ERROR:
                        list_item.setText(f"❌ {Path(path).name}")
                        list_item.setToolTip(f"{path}\nErreur: {message}")
                    elif status == ImageStatus.CANCELLED:
                        list_item.setText(f"⏹️ {Path(path).name}")
                    break
    
    def reset_all_statuses(self):
        """Reset all image statuses to pending."""
        for path, item in self._images.items():
            item.status = ImageStatus.PENDING
            item.error_message = ""
            item.output_path = ""
        
        # Update visual
        for i in range(self._list_widget.count()):
            list_item = self._list_widget.item(i)
            path = list_item.data(Qt.ItemDataRole.UserRole)
            list_item.setText(Path(path).name)
            list_item.setToolTip(path)
    
    def _show_context_menu(self, position):
        """Show context menu for selected items."""
        if not self._list_widget.selectedItems():
            return
        
        menu = QMenu(self)
        remove_action = menu.addAction("🗑️ Supprimer")
        remove_action.triggered.connect(self.remove_selected)
        
        menu.exec(self._list_widget.mapToGlobal(position))
    
    def _drag_enter_event(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drag_move_event(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drop_event(self, event: QDropEvent):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    paths.append(url.toLocalFile())
            
            if paths:
                self.add_images(paths)
            event.acceptProposedAction()
        else:
            event.ignore()
