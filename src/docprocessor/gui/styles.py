"""Centralized UI styles and color palette for consistent theming.

This module provides a unified dark theme color palette and reusable
style strings for all GUI components.
"""

# =============================================================================
# COLOR PALETTE - Dark Theme
# =============================================================================


class Colors:
    """Application color palette - Dark theme."""

    # Backgrounds
    BG_DARK = "#1e1e1e"  # Very dark - for lists, code areas
    BG_MEDIUM = "#2b2b2b"  # Medium dark - for input fields
    BG_LIGHT = "#3a3a3a"  # Light dark - for buttons
    BG_HOVER = "#4a4a4a"  # Hover state
    BG_PRESSED = "#2a2a2a"  # Pressed state

    # Borders
    BORDER_DARK = "#333"  # Dark borders
    BORDER_NORMAL = "#444"  # Normal borders
    BORDER_LIGHT = "#555"  # Light borders
    BORDER_FOCUS = "#2196F3"  # Focus state - blue

    # Text
    TEXT_PRIMARY = "#ffffff"  # Primary text - white
    TEXT_SECONDARY = "#aaa"  # Secondary text - light gray
    TEXT_DISABLED = "#666"  # Disabled text
    TEXT_HINT = "#888"  # Hint/placeholder text

    # Primary Actions
    PRIMARY = "#2196F3"  # Primary button color - blue
    PRIMARY_HOVER = "#1976D2"  # Primary hover
    PRIMARY_PRESSED = "#0D47A1"  # Primary pressed

    # Success/Error/Warning
    SUCCESS = "#4CAF50"  # Success green
    SUCCESS_HOVER = "#45a049"  # Success hover
    ERROR = "#f44336"  # Error red
    ERROR_HOVER = "#d32f2f"  # Error hover
    WARNING = "#ff9800"  # Warning orange
    WARNING_HOVER = "#f57c00"  # Warning hover

    # Special
    SELECTION = "#264f78"  # Selection background
    DISABLED_BG = "#555555"  # Disabled background
    DISABLED_TEXT = "#888888"  # Disabled text


# =============================================================================
# REUSABLE STYLE STRINGS
# =============================================================================


class Styles:
    """Reusable style strings for common UI elements."""

    # -------------------------------------------------------------------------
    # Buttons
    # -------------------------------------------------------------------------

    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_PRIMARY};
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 4px;
            border: none;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {Colors.DISABLED_BG};
            color: {Colors.DISABLED_TEXT};
        }}
    """

    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: {Colors.BG_LIGHT};
            border: 1px solid {Colors.BORDER_LIGHT};
            color: {Colors.TEXT_PRIMARY};
            padding: 8px 20px;
            border-radius: 4px;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_HOVER};
            border: 1px solid {Colors.BORDER_LIGHT};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BG_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {Colors.DISABLED_BG};
            color: {Colors.DISABLED_TEXT};
            border: 1px solid {Colors.BORDER_DARK};
        }}
    """

    BUTTON_SMALL = f"""
        QPushButton {{
            background-color: {Colors.BG_LIGHT};
            border: 1px solid {Colors.BORDER_LIGHT};
            color: {Colors.TEXT_PRIMARY};
            padding: 6px 12px;
            border-radius: 4px;
            min-width: 70px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_HOVER};
            border: 1px solid {Colors.BORDER_LIGHT};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BG_PRESSED};
        }}
    """

    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {Colors.SUCCESS};
            color: {Colors.TEXT_PRIMARY};
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 4px;
            border: none;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background-color: {Colors.SUCCESS_HOVER};
        }}
        QPushButton:disabled {{
            background-color: {Colors.DISABLED_BG};
            color: {Colors.DISABLED_TEXT};
        }}
    """

    # -------------------------------------------------------------------------
    # Input Fields
    # -------------------------------------------------------------------------

    LINE_EDIT = f"""
        QLineEdit {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 6px;
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
        }}
        QLineEdit:focus {{
            border: 1px solid {Colors.BORDER_FOCUS};
        }}
        QLineEdit:disabled {{
            background-color: {Colors.DISABLED_BG};
            color: {Colors.DISABLED_TEXT};
        }}
    """

    TEXT_EDIT = f"""
        QTextEdit {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 8px;
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
        }}
        QTextEdit:focus {{
            border: 1px solid {Colors.BORDER_FOCUS};
        }}
        QTextEdit::placeholder {{
            color: {Colors.TEXT_HINT};
        }}
    """

    TEXT_EDIT_CODE = f"""
        QTextEdit {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 8px;
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
            font-family: monospace;
        }}
        QTextEdit:focus {{
            border: 1px solid {Colors.BORDER_FOCUS};
        }}
    """

    # -------------------------------------------------------------------------
    # Lists and Tables
    # -------------------------------------------------------------------------

    LIST_WIDGET = f"""
        QListWidget {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 4px;
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_PRIMARY};
        }}
        QListWidget::item {{
            padding: 4px;
            border-radius: 2px;
        }}
        QListWidget::item:hover {{
            background-color: {Colors.BG_HOVER};
        }}
        QListWidget::item:selected {{
            background-color: {Colors.SELECTION};
        }}
    """

    TABLE_WIDGET = f"""
        QTableWidget {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_PRIMARY};
            gridline-color: {Colors.BORDER_DARK};
        }}
        QTableWidget::item {{
            padding: 4px;
        }}
        QTableWidget::item:hover {{
            background-color: {Colors.BG_HOVER};
        }}
        QTableWidget::item:selected {{
            background-color: {Colors.SELECTION};
        }}
        QHeaderView::section {{
            background-color: {Colors.BG_LIGHT};
            color: {Colors.TEXT_PRIMARY};
            padding: 6px;
            border: 1px solid {Colors.BORDER_DARK};
            font-weight: bold;
        }}
    """

    # -------------------------------------------------------------------------
    # Progress Bars
    # -------------------------------------------------------------------------

    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 2px solid {Colors.BORDER_NORMAL};
            border-radius: 5px;
            text-align: center;
            height: 25px;
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_PRIMARY};
        }}
        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            border-radius: 3px;
        }}
    """

    PROGRESS_BAR_SUCCESS = f"""
        QProgressBar {{
            border: 2px solid {Colors.BORDER_NORMAL};
            border-radius: 5px;
            text-align: center;
            height: 25px;
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_PRIMARY};
        }}
        QProgressBar::chunk {{
            background-color: {Colors.SUCCESS};
            border-radius: 3px;
        }}
    """

    # -------------------------------------------------------------------------
    # Labels and Text
    # -------------------------------------------------------------------------

    LABEL_HEADER = f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_PRIMARY};"
    LABEL_SUBHEADER = f"font-size: 12px; font-weight: bold; color: {Colors.TEXT_SECONDARY};"
    LABEL_SECONDARY = f"color: {Colors.TEXT_SECONDARY}; font-style: italic;"
    LABEL_HINT = f"color: {Colors.TEXT_HINT}; font-size: 11px;"

    INFO_BOX = f"""
        color: {Colors.TEXT_SECONDARY};
        padding: 10px;
        background: {Colors.BG_MEDIUM};
        border: 1px solid {Colors.BORDER_NORMAL};
        border-radius: 4px;
    """

    # -------------------------------------------------------------------------
    # Combo Boxes and Spin Boxes
    # -------------------------------------------------------------------------

    COMBO_BOX = f"""
        QComboBox {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 6px;
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
        }}
        QComboBox:hover {{
            border: 1px solid {Colors.BORDER_LIGHT};
        }}
        QComboBox:focus {{
            border: 1px solid {Colors.BORDER_FOCUS};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {Colors.TEXT_SECONDARY};
        }}
        QComboBox QAbstractItemView {{
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
            selection-background-color: {Colors.SELECTION};
            border: 1px solid {Colors.BORDER_NORMAL};
        }}
    """

    SPIN_BOX = f"""
        QSpinBox {{
            border: 1px solid {Colors.BORDER_NORMAL};
            border-radius: 4px;
            padding: 6px;
            background-color: {Colors.BG_MEDIUM};
            color: {Colors.TEXT_PRIMARY};
        }}
        QSpinBox:focus {{
            border: 1px solid {Colors.BORDER_FOCUS};
        }}
    """


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def apply_dark_theme_to_app(app):
    """Apply global dark theme to QApplication.

    Args:
        app: QApplication instance
    """
    app.setStyle("Fusion")

    from PyQt6.QtGui import QColor, QPalette

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BG_MEDIUM))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(Colors.BG_DARK))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.BG_MEDIUM))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.BG_LIGHT))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(Colors.BG_LIGHT))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Link, QColor(Colors.PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(Colors.SELECTION))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_PRIMARY))

    app.setPalette(palette)
