"""
Targeted image editing tab with zone selection and painting.
Allows users to load an image, select a specific zone or draw on it, and apply targeted edits.
"""

from pathlib import Path
from typing import Optional, List, Tuple
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QGroupBox, QFormLayout, QFileDialog,
    QScrollArea, QFrame, QButtonGroup, QToolButton, QMessageBox,
    QSplitter, QSizePolicy, QApplication, QSlider, QColorDialog
)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPixmap, QPainter, QPen, QColor, QBrush, QPainterPath,
    QFont, QPolygon, QImage
)

from utils.config import get_config, Config


class SelectionTool(Enum):
    """Available selection tools."""
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    FREEHAND = "freehand"
    PAINTBRUSH = "paintbrush"


class PaintStroke:
    """Represents a single paint stroke."""
    def __init__(self, color: QColor, brush_size: int):
        self.color = color
        self.brush_size = brush_size
        self.points: List[QPoint] = []


class ZoneSelectionCanvas(QLabel):
    """
    Interactive canvas for image display, zone selection, and painting.
    Supports rectangle, ellipse, freehand selection, and paintbrush tools.
    """
    
    selection_changed = pyqtSignal()
    
    # Colors for selection overlay
    SELECTION_COLOR = QColor(255, 107, 53, 200)  # Orange with transparency
    SELECTION_FILL = QColor(255, 107, 53, 50)    # Light orange fill
    
    # Default paint colors
    PAINT_COLORS = [
        QColor(255, 0, 0),      # Red
        QColor(0, 255, 0),      # Green
        QColor(0, 0, 255),      # Blue
        QColor(255, 255, 0),    # Yellow
        QColor(255, 0, 255),    # Magenta
        QColor(0, 255, 255),    # Cyan
        QColor(255, 165, 0),    # Orange
        QColor(128, 0, 128),    # Purple
        QColor(0, 0, 0),        # Black
        QColor(255, 255, 255),  # White
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path: str = ""
        self._original_pixmap: Optional[QPixmap] = None
        self._scaled_pixmap: Optional[QPixmap] = None
        self._scale_factor: float = 1.0
        
        self._tool: SelectionTool = SelectionTool.RECTANGLE
        self._is_drawing: bool = False
        self._start_point: Optional[QPoint] = None
        self._end_point: Optional[QPoint] = None
        self._freehand_points: List[QPoint] = []
        
        # Paint mode properties
        self._paint_color: QColor = QColor(255, 0, 0)  # Default red
        self._brush_size: int = 10
        self._paint_strokes: List[PaintStroke] = []
        self._current_stroke: Optional[PaintStroke] = None
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px dashed #444;
                border-radius: 8px;
            }
        """)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
        # Placeholder text
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text when no image is loaded."""
        self.setText("📷 Cliquez pour charger une image\nou glissez-déposez un fichier")
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px dashed #444;
                border-radius: 8px;
                color: #666;
                font-size: 14px;
            }
        """)
    
    def set_image(self, path: str) -> bool:
        """
        Load and display an image.
        
        Args:
            path: Path to the image file
            
        Returns:
            True if image was loaded successfully
        """
        if not path or not Path(path).exists():
            return False
        
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return False
        
        self._image_path = path
        self._original_pixmap = pixmap
        self._clear_selection_data()
        self._paint_strokes = []
        self._update_display()
        
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 8px;
            }
        """)
        
        return True
    
    def set_paint_color(self, color: QColor):
        """Set the paint brush color."""
        self._paint_color = color
    
    def set_brush_size(self, size: int):
        """Set the paint brush size."""
        self._brush_size = max(1, min(size, 100))
    
    def get_paint_color(self) -> QColor:
        """Get the current paint color."""
        return self._paint_color
    
    def get_brush_size(self) -> int:
        """Get the current brush size."""
        return self._brush_size
    
    def _update_display(self):
        """Update the displayed image, scaled to fit the widget."""
        if self._original_pixmap is None:
            return
        
        # Calculate scale to fit in widget while maintaining aspect ratio
        widget_size = self.size()
        img_size = self._original_pixmap.size()
        
        # Leave some margin
        available_width = widget_size.width() - 20
        available_height = widget_size.height() - 20
        
        scale_x = available_width / img_size.width() if img_size.width() > 0 else 1
        scale_y = available_height / img_size.height() if img_size.height() > 0 else 1
        self._scale_factor = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        new_width = int(img_size.width() * self._scale_factor)
        new_height = int(img_size.height() * self._scale_factor)
        
        self._scaled_pixmap = self._original_pixmap.scaled(
            new_width, new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Draw selection overlay and paint strokes
        display_pixmap = self._draw_overlays()
        self.setPixmap(display_pixmap)
    
    def _draw_overlays(self) -> QPixmap:
        """Draw the selection overlay and paint strokes on the scaled image."""
        if self._scaled_pixmap is None:
            return QPixmap()
        
        # Create a copy to draw on
        result = self._scaled_pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw paint strokes
        for stroke in self._paint_strokes:
            if len(stroke.points) > 1:
                pen = QPen(stroke.color, stroke.brush_size, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                for i in range(1, len(stroke.points)):
                    painter.drawLine(stroke.points[i-1], stroke.points[i])
        
        # Draw current stroke being drawn
        if self._current_stroke and len(self._current_stroke.points) > 1:
            pen = QPen(self._current_stroke.color, self._current_stroke.brush_size, 
                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            for i in range(1, len(self._current_stroke.points)):
                painter.drawLine(self._current_stroke.points[i-1], self._current_stroke.points[i])
        
        # Draw selection overlay
        pen = QPen(self.SELECTION_COLOR, 3, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.SELECTION_FILL))
        
        if self._tool == SelectionTool.RECTANGLE and self._start_point and self._end_point:
            rect = QRect(self._start_point, self._end_point).normalized()
            painter.drawRect(rect)
            
        elif self._tool == SelectionTool.ELLIPSE and self._start_point and self._end_point:
            rect = QRect(self._start_point, self._end_point).normalized()
            painter.drawEllipse(rect)
            
        elif self._tool == SelectionTool.FREEHAND and len(self._freehand_points) > 2:
            path = QPainterPath()
            path.moveTo(QPointF(self._freehand_points[0]))
            for point in self._freehand_points[1:]:
                path.lineTo(QPointF(point))
            path.closeSubpath()
            painter.drawPath(path)
        
        painter.end()
        return result
    
    def set_tool(self, tool: SelectionTool):
        """Set the current selection tool."""
        self._tool = tool
        if tool != SelectionTool.PAINTBRUSH:
            self._clear_selection_data()
        self._update_display()
    
    def _clear_selection_data(self):
        """Clear selection data without clearing the image or paint strokes."""
        self._start_point = None
        self._end_point = None
        self._freehand_points = []
        self._is_drawing = False
    
    def clear_selection(self):
        """Clear the current selection."""
        self._clear_selection_data()
        self._update_display()
        self.selection_changed.emit()
    
    def clear_paint(self):
        """Clear all paint strokes."""
        self._paint_strokes = []
        self._current_stroke = None
        self._update_display()
        self.selection_changed.emit()
    
    def clear_all(self):
        """Clear both selection and paint strokes."""
        self._clear_selection_data()
        self._paint_strokes = []
        self._current_stroke = None
        self._update_display()
        self.selection_changed.emit()
    
    def has_selection(self) -> bool:
        """Check if there is an active selection."""
        if self._tool == SelectionTool.FREEHAND:
            return len(self._freehand_points) > 2
        if self._tool == SelectionTool.PAINTBRUSH:
            return False  # Paintbrush doesn't count as selection
        return self._start_point is not None and self._end_point is not None
    
    def has_paint(self) -> bool:
        """Check if there are paint strokes."""
        return len(self._paint_strokes) > 0
    
    def has_any_drawing(self) -> bool:
        """Check if there is any selection or paint."""
        return self.has_selection() or self.has_paint()
    
    def get_image_with_overlay(self) -> Optional[QImage]:
        """
        Get the original image with the selection overlay and paint strokes drawn on it.
        This is what will be sent to the API.
        
        Returns:
            QImage with overlay, or None if no image
        """
        if self._original_pixmap is None:
            return None
        
        if not self.has_any_drawing():
            return None
        
        # Draw on the original resolution image
        result = self._original_pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Scale factor from display to original
        scale = 1.0 / self._scale_factor if self._scale_factor > 0 else 1.0
        
        # Draw paint strokes at original resolution
        for stroke in self._paint_strokes:
            if len(stroke.points) > 1:
                pen_width = max(1, int(stroke.brush_size * scale))
                pen = QPen(stroke.color, pen_width, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                for i in range(1, len(stroke.points)):
                    p1 = QPoint(int(stroke.points[i-1].x() * scale), int(stroke.points[i-1].y() * scale))
                    p2 = QPoint(int(stroke.points[i].x() * scale), int(stroke.points[i].y() * scale))
                    painter.drawLine(p1, p2)
        
        # Draw selection overlay
        pen_width = max(4, int(3 * scale))
        pen = QPen(self.SELECTION_COLOR, pen_width, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.SELECTION_FILL))
        
        if self._tool == SelectionTool.RECTANGLE and self._start_point and self._end_point:
            start = QPoint(int(self._start_point.x() * scale), int(self._start_point.y() * scale))
            end = QPoint(int(self._end_point.x() * scale), int(self._end_point.y() * scale))
            rect = QRect(start, end).normalized()
            painter.drawRect(rect)
            
        elif self._tool == SelectionTool.ELLIPSE and self._start_point and self._end_point:
            start = QPoint(int(self._start_point.x() * scale), int(self._start_point.y() * scale))
            end = QPoint(int(self._end_point.x() * scale), int(self._end_point.y() * scale))
            rect = QRect(start, end).normalized()
            painter.drawEllipse(rect)
            
        elif self._tool == SelectionTool.FREEHAND and len(self._freehand_points) > 2:
            path = QPainterPath()
            scaled_points = [
                QPointF(p.x() * scale, p.y() * scale)
                for p in self._freehand_points
            ]
            path.moveTo(scaled_points[0])
            for point in scaled_points[1:]:
                path.lineTo(point)
            path.closeSubpath()
            painter.drawPath(path)
        
        painter.end()
        return result.toImage()
    
    def get_sketch_only_image(self) -> Optional[QImage]:
        """
        Get an image showing ONLY the user's drawings/selections on a copy of the original.
        This is used to show the AI what zone to modify, while keeping the original separate.
        
        The sketch will have the drawings overlaid on the original image,
        which helps the AI understand the spatial context of the edit zone.
        
        Returns:
            QImage with sketch overlay, or None if no drawing
        """
        if self._original_pixmap is None:
            return None
        
        if not self.has_any_drawing():
            return None
        
        # Create a copy of the original to draw the sketch on
        result = self._original_pixmap.copy()
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Scale factor from display to original
        scale = 1.0 / self._scale_factor if self._scale_factor > 0 else 1.0
        
        # Draw paint strokes at original resolution with THICK, VISIBLE lines
        for stroke in self._paint_strokes:
            if len(stroke.points) > 1:
                # Make strokes extra visible
                pen_width = max(8, int(stroke.brush_size * scale * 1.5))
                pen = QPen(stroke.color, pen_width, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                for i in range(1, len(stroke.points)):
                    p1 = QPoint(int(stroke.points[i-1].x() * scale), int(stroke.points[i-1].y() * scale))
                    p2 = QPoint(int(stroke.points[i].x() * scale), int(stroke.points[i].y() * scale))
                    painter.drawLine(p1, p2)
        
        # Draw selection zone with thick, visible lines
        pen_width = max(8, int(6 * scale))
        pen = QPen(self.SELECTION_COLOR, pen_width, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.SELECTION_FILL))
        
        if self._tool == SelectionTool.RECTANGLE and self._start_point and self._end_point:
            start = QPoint(int(self._start_point.x() * scale), int(self._start_point.y() * scale))
            end = QPoint(int(self._end_point.x() * scale), int(self._end_point.y() * scale))
            rect = QRect(start, end).normalized()
            painter.drawRect(rect)
            
        elif self._tool == SelectionTool.ELLIPSE and self._start_point and self._end_point:
            start = QPoint(int(self._start_point.x() * scale), int(self._start_point.y() * scale))
            end = QPoint(int(self._end_point.x() * scale), int(self._end_point.y() * scale))
            rect = QRect(start, end).normalized()
            painter.drawEllipse(rect)
            
        elif self._tool == SelectionTool.FREEHAND and len(self._freehand_points) > 2:
            path = QPainterPath()
            scaled_points = [
                QPointF(p.x() * scale, p.y() * scale)
                for p in self._freehand_points
            ]
            path.moveTo(scaled_points[0])
            for point in scaled_points[1:]:
                path.lineTo(point)
            path.closeSubpath()
            painter.drawPath(path)
        
        painter.end()
        return result.toImage()
    
    def get_image_path(self) -> str:
        """Get the path to the loaded image."""
        return self._image_path
    
    def _get_image_point(self, widget_pos: QPoint) -> QPoint:
        """Convert widget coordinates to image coordinates."""
        if self._scaled_pixmap is None:
            return widget_pos
        
        # Calculate offset (image is centered in the widget)
        pixmap_rect = self._scaled_pixmap.rect()
        widget_rect = self.rect()
        
        offset_x = (widget_rect.width() - pixmap_rect.width()) // 2
        offset_y = (widget_rect.height() - pixmap_rect.height()) // 2
        
        # Adjust for offset
        img_x = widget_pos.x() - offset_x
        img_y = widget_pos.y() - offset_y
        
        # Clamp to image bounds
        img_x = max(0, min(img_x, pixmap_rect.width() - 1))
        img_y = max(0, min(img_y, pixmap_rect.height() - 1))
        
        return QPoint(img_x, img_y)
    
    def mousePressEvent(self, event):
        """Handle mouse press for starting selection or painting."""
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        
        if self._original_pixmap is None:
            # No image loaded, trigger file dialog
            return super().mousePressEvent(event)
        
        self._is_drawing = True
        point = self._get_image_point(event.pos())
        
        if self._tool == SelectionTool.PAINTBRUSH:
            self._current_stroke = PaintStroke(self._paint_color, self._brush_size)
            self._current_stroke.points.append(point)
        elif self._tool == SelectionTool.FREEHAND:
            self._freehand_points = [point]
        else:
            self._start_point = point
            self._end_point = point
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drawing selection or painting."""
        if not self._is_drawing or self._original_pixmap is None:
            return super().mouseMoveEvent(event)
        
        point = self._get_image_point(event.pos())
        
        if self._tool == SelectionTool.PAINTBRUSH:
            if self._current_stroke:
                self._current_stroke.points.append(point)
        elif self._tool == SelectionTool.FREEHAND:
            self._freehand_points.append(point)
        else:
            self._end_point = point
        
        self._update_display()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for completing selection or painting."""
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mouseReleaseEvent(event)
        
        self._is_drawing = False
        
        if self._tool == SelectionTool.PAINTBRUSH:
            if self._current_stroke and len(self._current_stroke.points) > 0:
                self._paint_strokes.append(self._current_stroke)
            self._current_stroke = None
            self.selection_changed.emit()
        elif self.has_selection():
            self.selection_changed.emit()
    
    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        if self._original_pixmap is not None:
            self._update_display()


class TargetedEditTab(QWidget):
    """
    Tab for targeted image editing with zone selection and painting.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = get_config()
        self._result_image_path: Optional[str] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # === Left: Canvas and tools ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Create canvas first (needed by paint toolbar)
        self._canvas = ZoneSelectionCanvas()
        
        # Toolbar
        toolbar = self._create_toolbar()
        left_layout.addLayout(toolbar)
        
        # Paint toolbar (color, brush size) - needs canvas to exist
        paint_toolbar = self._create_paint_toolbar()
        left_layout.addLayout(paint_toolbar)
        
        # Canvas in scroll area
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidgetResizable(True)
        canvas_scroll.setStyleSheet("QScrollArea { border: none; background-color: #1a1a1a; }")
        
        canvas_scroll.setWidget(self._canvas)
        
        left_layout.addWidget(canvas_scroll, stretch=1)
        
        main_layout.addWidget(left_widget, stretch=2)
        
        # === Right: Configuration and result ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Prompt group
        prompt_group = QGroupBox("Prompt de modification")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlaceholderText(
            "Décrivez la modification à appliquer...\n\n"
            "Exemples:\n"
            "• Dessinez un cercle rouge → \"Remplace par un chat\"\n"
            "• Entourez une zone → \"Supprime cet élément\"\n"
            "• Dessinez des traits → \"Ajoute des fleurs ici\"\n"
            "• Sans dessin → \"Change le fond en forêt\""
        )
        self._prompt_edit.setMaximumHeight(120)
        prompt_layout.addWidget(self._prompt_edit)
        
        # Hint about zone
        hint_label = QLabel(
            "💡 Dessinez sur l'image pour indiquer la zone à modifier. "
            "Le prompt sera enrichi automatiquement."
        )
        hint_label.setStyleSheet("color: #888; font-size: 10px;")
        hint_label.setWordWrap(True)
        prompt_layout.addWidget(hint_label)
        
        right_layout.addWidget(prompt_group)
        
        # Config group
        config_group = QGroupBox("Configuration")
        config_form = QFormLayout(config_group)
        
        # Model
        self._model_combo = QComboBox()
        for model_id, model_name in Config.MODELS:
            self._model_combo.addItem(model_name, model_id)
        config_form.addRow("Modèle:", self._model_combo)
        
        # Quality
        self._quality_combo = QComboBox()
        for quality_id, quality_name in Config.OUTPUT_QUALITIES:
            self._quality_combo.addItem(quality_name, quality_id)
        config_form.addRow("Qualité:", self._quality_combo)
        
        right_layout.addWidget(config_group)
        
        # Apply button
        self._apply_btn = QPushButton("🎯 Appliquer la modification")
        self._apply_btn.setFont(QFont("", 11, QFont.Weight.Bold))
        self._apply_btn.setMinimumHeight(45)
        self._apply_btn.setEnabled(False)
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b35;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #ff8555;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        right_layout.addWidget(self._apply_btn)
        
        # Result preview
        result_group = QGroupBox("Résultat")
        result_layout = QVBoxLayout(result_group)
        
        self._result_label = QLabel("Le résultat apparaîtra ici")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_label.setMinimumSize(200, 200)
        self._result_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px dashed #444;
                border-radius: 8px;
                color: #666;
            }
        """)
        self._result_label.setCursor(Qt.CursorShape.PointingHandCursor)
        result_layout.addWidget(self._result_label)
        
        right_layout.addWidget(result_group, stretch=1)
        
        main_layout.addWidget(right_widget, stretch=1)
    
    def _create_toolbar(self) -> QHBoxLayout:
        """Create the toolbar with tools and actions."""
        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        
        # Load image button
        self._load_btn = QPushButton("📂 Charger une image")
        self._load_btn.setMinimumHeight(35)
        toolbar.addWidget(self._load_btn)
        
        toolbar.addSpacing(20)
        
        # Tool selection
        tool_label = QLabel("Outil:")
        tool_label.setStyleSheet("color: #aaa;")
        toolbar.addWidget(tool_label)
        
        self._tool_group = QButtonGroup(self)
        
        self._paint_btn = QToolButton()
        self._paint_btn.setText("🖌️ Pinceau")
        self._paint_btn.setCheckable(True)
        self._paint_btn.setChecked(True)
        self._paint_btn.setMinimumHeight(35)
        self._tool_group.addButton(self._paint_btn, 3)
        toolbar.addWidget(self._paint_btn)
        
        self._rect_btn = QToolButton()
        self._rect_btn.setText("▢ Rectangle")
        self._rect_btn.setCheckable(True)
        self._rect_btn.setMinimumHeight(35)
        self._tool_group.addButton(self._rect_btn, 0)
        toolbar.addWidget(self._rect_btn)
        
        self._ellipse_btn = QToolButton()
        self._ellipse_btn.setText("○ Ellipse")
        self._ellipse_btn.setCheckable(True)
        self._ellipse_btn.setMinimumHeight(35)
        self._tool_group.addButton(self._ellipse_btn, 1)
        toolbar.addWidget(self._ellipse_btn)
        
        self._freehand_btn = QToolButton()
        self._freehand_btn.setText("✏️ Sélection libre")
        self._freehand_btn.setCheckable(True)
        self._freehand_btn.setMinimumHeight(35)
        self._tool_group.addButton(self._freehand_btn, 2)
        toolbar.addWidget(self._freehand_btn)
        
        toolbar.addSpacing(20)
        
        # Clear buttons
        self._clear_paint_btn = QPushButton("🧹 Effacer dessins")
        self._clear_paint_btn.setMinimumHeight(35)
        toolbar.addWidget(self._clear_paint_btn)
        
        self._clear_btn = QPushButton("🗑️ Tout effacer")
        self._clear_btn.setMinimumHeight(35)
        toolbar.addWidget(self._clear_btn)
        
        toolbar.addStretch()
        
        return toolbar
    
    def _create_paint_toolbar(self) -> QHBoxLayout:
        """Create the paint-specific toolbar."""
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        # Color label
        color_label = QLabel("Couleur:")
        color_label.setStyleSheet("color: #aaa;")
        toolbar.addWidget(color_label)
        
        # Color buttons
        self._color_buttons: List[QPushButton] = []
        for i, color in enumerate(ZoneSelectionCanvas.PAINT_COLORS):
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 2px solid #444;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid #888;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color, b=btn: self._on_color_selected(c, b))
            self._color_buttons.append(btn)
            toolbar.addWidget(btn)
        
        # Custom color button
        self._custom_color_btn = QPushButton("🎨")
        self._custom_color_btn.setFixedSize(28, 28)
        self._custom_color_btn.setToolTip("Couleur personnalisée")
        toolbar.addWidget(self._custom_color_btn)
        
        toolbar.addSpacing(20)
        
        # Brush size
        size_label = QLabel("Taille:")
        size_label.setStyleSheet("color: #aaa;")
        toolbar.addWidget(size_label)
        
        self._brush_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._brush_size_slider.setMinimum(2)
        self._brush_size_slider.setMaximum(50)
        self._brush_size_slider.setValue(10)
        self._brush_size_slider.setFixedWidth(120)
        toolbar.addWidget(self._brush_size_slider)
        
        self._brush_size_label = QLabel("10px")
        self._brush_size_label.setStyleSheet("color: #aaa; min-width: 40px;")
        toolbar.addWidget(self._brush_size_label)
        
        toolbar.addStretch()
        
        # Select first color
        if self._color_buttons:
            self._on_color_selected(ZoneSelectionCanvas.PAINT_COLORS[0], self._color_buttons[0])
        
        return toolbar
    
    def _connect_signals(self):
        """Connect all signals to slots."""
        self._load_btn.clicked.connect(self._load_image)
        self._clear_btn.clicked.connect(self._canvas.clear_all)
        self._clear_paint_btn.clicked.connect(self._canvas.clear_paint)
        self._apply_btn.clicked.connect(self._apply_edit)
        
        self._tool_group.idClicked.connect(self._on_tool_changed)
        self._canvas.selection_changed.connect(self._on_selection_changed)
        self._prompt_edit.textChanged.connect(self._on_selection_changed)
        self._canvas.mousePressEvent = self._on_canvas_click
        
        self._brush_size_slider.valueChanged.connect(self._on_brush_size_changed)
        self._custom_color_btn.clicked.connect(self._on_custom_color)
        
        self._result_label.mousePressEvent = self._on_result_click
        
        # Initialize with paintbrush tool
        self._canvas.set_tool(SelectionTool.PAINTBRUSH)
    
    def _on_color_selected(self, color: QColor, button: QPushButton):
        """Handle color selection."""
        # Update button borders
        for btn in self._color_buttons:
            current_style = btn.styleSheet()
            # Reset all borders
            btn.setStyleSheet(btn.styleSheet().replace("border: 3px solid #ff6b35;", "border: 2px solid #444;"))
        
        # Highlight selected
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 3px solid #ff6b35;
                border-radius: 4px;
            }}
        """)
        
        self._canvas.set_paint_color(color)
    
    def _on_custom_color(self):
        """Open color picker for custom color."""
        color = QColorDialog.getColor(self._canvas.get_paint_color(), self, "Choisir une couleur")
        if color.isValid():
            self._canvas.set_paint_color(color)
            # Deselect all color buttons
            for btn in self._color_buttons:
                btn.setStyleSheet(btn.styleSheet().replace("border: 3px solid #ff6b35;", "border: 2px solid #444;"))
    
    def _on_brush_size_changed(self, value: int):
        """Handle brush size change."""
        self._canvas.set_brush_size(value)
        self._brush_size_label.setText(f"{value}px")
    
    def _on_canvas_click(self, event):
        """Handle click on canvas - load image if empty."""
        if self._canvas._original_pixmap is None:
            if event.button() == Qt.MouseButton.LeftButton:
                self._load_image()
        else:
            # Call original handler
            ZoneSelectionCanvas.mousePressEvent(self._canvas, event)
    
    def _on_tool_changed(self, tool_id: int):
        """Handle tool selection change."""
        tools = {
            0: SelectionTool.RECTANGLE,
            1: SelectionTool.ELLIPSE,
            2: SelectionTool.FREEHAND,
            3: SelectionTool.PAINTBRUSH
        }
        if tool_id in tools:
            self._canvas.set_tool(tools[tool_id])
    
    def _on_selection_changed(self):
        """Handle selection or paint change."""
        has_drawing = self._canvas.has_any_drawing()
        has_prompt = bool(self._prompt_edit.toPlainText().strip())
        has_image = self._canvas._original_pixmap is not None
        self._apply_btn.setEnabled(has_image and has_prompt and has_drawing)
    
    def _load_image(self):
        """Open file dialog to load an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Tous les fichiers (*)"
        )
        
        if file_path:
            if not self._canvas.set_image(file_path):
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Impossible de charger l'image sélectionnée."
                )
    
    def _apply_edit(self):
        """Apply the targeted edit using the API with separate original + sketch images."""
        from api_client import NanoBananaClient
        from datetime import datetime
        import tempfile
        import os
        
        # Get API key from settings
        api_key = self._config.api_key
        if not api_key:
            QMessageBox.warning(
                self,
                "Attention",
                "Clé API non configurée. Allez dans l'onglet Paramètres."
            )
            return
        
        # Check for drawings
        if not self._canvas.has_any_drawing():
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez dessiner sur l'image pour indiquer la zone à modifier."
            )
            return
        
        # Get sketch image (original with drawings on it)
        sketch_image = self._canvas.get_sketch_only_image()
        if sketch_image is None:
            QMessageBox.warning(
                self,
                "Attention",
                "Veuillez dessiner sur l'image pour indiquer la zone à modifier."
            )
            return
        
        # Build prompt
        base_prompt = self._prompt_edit.toPlainText().strip()
        if not base_prompt:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un prompt.")
            return
        
        # Create temp files for original and sketch
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_temp_path = self._canvas.get_image_path()  # Use original directly
        sketch_temp_path = os.path.join(temp_dir, f"pixelforge_sketch_{timestamp}.png")
        
        # Save sketch image
        sketch_image.save(sketch_temp_path, "PNG")
        
        # Disable button during processing
        self._apply_btn.setEnabled(False)
        self._apply_btn.setText("⏳ Traitement en cours...")
        QApplication.processEvents()
        
        try:
            # Initialize client
            client = NanoBananaClient(api_key)
            
            # Make API call with separate original and sketch images
            result_bytes, error_msg = client.edit_image_with_sketch(
                original_image_path=original_temp_path,
                sketch_image_path=sketch_temp_path,
                prompt=base_prompt,
                model=self._model_combo.currentData(),
                aspect_ratio="original",
                output_quality=self._quality_combo.currentData()
            )
            
            if result_bytes and not error_msg:
                # Save result
                original_path = Path(self._canvas.get_image_path())
                output_dir = original_path.parent
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = f"{original_path.stem}_targeted_{timestamp}.png"
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
                            border: 1px solid #ff6b35;
                            border-radius: 8px;
                        }
                        QLabel:hover {
                            border: 2px solid #ff6b35;
                        }
                    """)
                
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Image modifiée enregistrée:\n{output_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la modification:\n{error_msg or 'Erreur inconnue'}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du traitement:\n{str(e)}"
            )
        
        finally:
            # Cleanup temp sketch file
            try:
                os.remove(sketch_temp_path)
            except:
                pass
            
            self._apply_btn.setEnabled(True)
            self._apply_btn.setText("🎯 Appliquer la modification")
            self._on_selection_changed()  # Update button state
    
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
