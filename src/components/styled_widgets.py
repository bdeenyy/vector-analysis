# src/components/styled_widgets.py
from PyQt6.QtWidgets import QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt

class StyledButton(QPushButton):
    """Стилизованная кнопка"""
    def __init__(self, text="", parent=None, style_type="default"):
        super().__init__(text, parent)
        self.style_type = style_type
        self.apply_style()

    def apply_style(self):
        """Применить стиль в зависимости от типа"""
        styles = {
            "default": """
                QPushButton {
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #f9fafb;
                }
            """,
            "primary": """
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
            """,
            "circular": """
                QPushButton {
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 16px;
                    color: #666666;
                    width: 32px;
                    height: 32px;
                }
            """
        }
        self.setStyleSheet(styles.get(self.style_type, styles["default"]))

class StyledFrame(QFrame):
    """Стилизованная панель"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
            }
        """)

class StyledTitle(QLabel):
    """Стилизованный заголовок"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #111827;
                margin-bottom: 8px;
            }
        """)