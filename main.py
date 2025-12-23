#!/usr/bin/env python3
"""
Nano Banana Batch Image Processor
Main entry point for the application.

A cross-platform application for batch processing images using 
the Nano Banana (Gemini) API from Google.
"""

import sys
import os

# Add the application directory to the path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.main_window import MainWindow


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Nano Banana Batch Processor")
    app.setOrganizationName("Air MKG")
    app.setOrganizationDomain("airmkg.com")
    
    # Set default font
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    # Apply modern stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a2e;
        }
        
        QWidget {
            background-color: #16213e;
            color: #e8e8e8;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #0f3460;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 10px;
            background-color: #1a1a2e;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #e94560;
        }
        
        QPushButton {
            background-color: #0f3460;
            color: #e8e8e8;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #e94560;
        }
        
        QPushButton:pressed {
            background-color: #c73e54;
        }
        
        QPushButton:disabled {
            background-color: #2d2d44;
            color: #666666;
        }
        
        QLineEdit, QTextEdit {
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 6px;
            padding: 8px;
            color: #e8e8e8;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border-color: #e94560;
        }
        
        QComboBox {
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 6px;
            padding: 8px;
            color: #e8e8e8;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #e8e8e8;
            margin-right: 10px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            selection-background-color: #e94560;
        }
        
        QTabWidget::pane {
            border: 1px solid #0f3460;
            border-radius: 8px;
            background-color: #16213e;
        }
        
        QTabBar::tab {
            background-color: #1a1a2e;
            color: #e8e8e8;
            padding: 10px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #e94560;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #0f3460;
        }
        
        QListWidget {
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 8px;
        }
        
        QListWidget::item {
            padding: 5px;
            border-radius: 4px;
        }
        
        QListWidget::item:selected {
            background-color: #e94560;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #0f3460;
        }
        
        QProgressBar {
            background-color: #1a1a2e;
            border: 1px solid #0f3460;
            border-radius: 6px;
            height: 20px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #e94560;
            border-radius: 5px;
        }
        
        QStatusBar {
            background-color: #1a1a2e;
            color: #888888;
        }
        
        QScrollBar:vertical {
            background-color: #1a1a2e;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #0f3460;
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #e94560;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QSplitter::handle {
            background-color: #0f3460;
            height: 3px;
        }
        
        QSplitter::handle:hover {
            background-color: #e94560;
        }
        
        QMessageBox {
            background-color: #16213e;
        }
        
        QMessageBox QLabel {
            color: #e8e8e8;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
