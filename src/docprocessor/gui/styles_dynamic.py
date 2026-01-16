"""Dynamic UI styles that adapt to theme and size profile.

This module provides theme-aware and size-aware styles that automatically
adapt to user preferences.
"""

from docprocessor.gui.size_profile import get_size_profile_manager
from docprocessor.gui.theme_manager import get_theme_manager


# Convenience accessor for current theme colors
class Colors:
    """Dynamic color accessor that uses current theme."""

    @property
    def BG_DARK(self):
        return get_theme_manager().get_colors().BG_DARK

    @property
    def BG_MEDIUM(self):
        return get_theme_manager().get_colors().BG_MEDIUM

    @property
    def BG_LIGHT(self):
        return get_theme_manager().get_colors().BG_LIGHT

    @property
    def BG_HOVER(self):
        return get_theme_manager().get_colors().BG_HOVER

    @property
    def BG_PRESSED(self):
        return get_theme_manager().get_colors().BG_PRESSED

    @property
    def BORDER_DARK(self):
        return get_theme_manager().get_colors().BORDER_DARK

    @property
    def BORDER_NORMAL(self):
        return get_theme_manager().get_colors().BORDER_NORMAL

    @property
    def BORDER_LIGHT(self):
        return get_theme_manager().get_colors().BORDER_LIGHT

    @property
    def BORDER_FOCUS(self):
        return get_theme_manager().get_colors().BORDER_FOCUS

    @property
    def TEXT_PRIMARY(self):
        return get_theme_manager().get_colors().TEXT_PRIMARY

    @property
    def TEXT_SECONDARY(self):
        return get_theme_manager().get_colors().TEXT_SECONDARY

    @property
    def TEXT_DISABLED(self):
        return get_theme_manager().get_colors().TEXT_DISABLED

    @property
    def TEXT_HINT(self):
        return get_theme_manager().get_colors().TEXT_HINT

    @property
    def PRIMARY(self):
        return get_theme_manager().get_colors().PRIMARY

    @property
    def PRIMARY_HOVER(self):
        return get_theme_manager().get_colors().PRIMARY_HOVER

    @property
    def PRIMARY_PRESSED(self):
        return get_theme_manager().get_colors().PRIMARY_PRESSED

    @property
    def SUCCESS(self):
        return get_theme_manager().get_colors().SUCCESS

    @property
    def SUCCESS_HOVER(self):
        return get_theme_manager().get_colors().SUCCESS_HOVER

    @property
    def ERROR(self):
        return get_theme_manager().get_colors().ERROR

    @property
    def ERROR_HOVER(self):
        return get_theme_manager().get_colors().ERROR_HOVER

    @property
    def WARNING(self):
        return get_theme_manager().get_colors().WARNING

    @property
    def WARNING_HOVER(self):
        return get_theme_manager().get_colors().WARNING_HOVER

    @property
    def SELECTION(self):
        return get_theme_manager().get_colors().SELECTION

    @property
    def DISABLED_BG(self):
        return get_theme_manager().get_colors().DISABLED_BG

    @property
    def DISABLED_TEXT(self):
        return get_theme_manager().get_colors().DISABLED_TEXT


# Singleton instance
_colors_instance = Colors()


def get_colors():
    """Get the dynamic colors accessor."""
    return _colors_instance


class StyleGenerator:
    """Generates dynamic styles based on current theme and size profile."""

    @staticmethod
    def button_primary():
        """Generate primary button style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QPushButton {{
                background-color: {colors.PRIMARY};
                color: {colors.TEXT_PRIMARY};
                font-weight: bold;
                font-size: {profile.font_size_base}px;
                padding: {profile.button_padding}px {profile.button_padding * 2}px;
                border-radius: {profile.border_radius}px;
                border: none;
                min-width: {profile.button_min_width}px;
                min-height: {profile.button_height}px;
            }}
            QPushButton:hover {{
                background-color: {colors.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {colors.PRIMARY_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {colors.DISABLED_BG};
                color: {colors.DISABLED_TEXT};
            }}
        """

    @staticmethod
    def button_secondary():
        """Generate secondary button style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QPushButton {{
                background-color: {colors.BG_LIGHT};
                border: {profile.border_width}px solid {colors.BORDER_LIGHT};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
                padding: {profile.button_padding}px {profile.button_padding * 2}px;
                border-radius: {profile.border_radius}px;
                min-width: {profile.button_min_width}px;
                min-height: {profile.button_height}px;
            }}
            QPushButton:hover {{
                background-color: {colors.BG_HOVER};
                border: {profile.border_width}px solid {colors.BORDER_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {colors.BG_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {colors.DISABLED_BG};
                color: {colors.DISABLED_TEXT};
                border: {profile.border_width}px solid {colors.BORDER_DARK};
            }}
        """

    @staticmethod
    def button_small():
        """Generate small button style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        # Small buttons are 80% of regular button size
        small_height = int(profile.button_height * 0.8)
        small_padding = int(profile.button_padding * 0.75)
        small_min_width = int(profile.button_min_width * 0.7)

        return f"""
            QPushButton {{
                background-color: {colors.BG_LIGHT};
                border: {profile.border_width}px solid {colors.BORDER_LIGHT};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_small}px;
                padding: {small_padding}px {small_padding * 2}px;
                border-radius: {profile.border_radius}px;
                min-width: {small_min_width}px;
                min-height: {small_height}px;
            }}
            QPushButton:hover {{
                background-color: {colors.BG_HOVER};
                border: {profile.border_width}px solid {colors.BORDER_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {colors.BG_PRESSED};
            }}
        """

    @staticmethod
    def button_success():
        """Generate success button style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QPushButton {{
                background-color: {colors.SUCCESS};
                color: {colors.TEXT_PRIMARY};
                font-weight: bold;
                font-size: {profile.font_size_base}px;
                padding: {profile.button_padding}px {profile.button_padding * 2}px;
                border-radius: {profile.border_radius}px;
                border: none;
                min-width: {profile.button_min_width}px;
                min-height: {profile.button_height}px;
            }}
            QPushButton:hover {{
                background-color: {colors.SUCCESS_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {colors.DISABLED_BG};
                color: {colors.DISABLED_TEXT};
            }}
        """

    @staticmethod
    def line_edit():
        """Generate line edit style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QLineEdit {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.input_padding}px;
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
                min-height: {profile.input_height}px;
            }}
            QLineEdit:focus {{
                border: {profile.border_width}px solid {colors.BORDER_FOCUS};
            }}
            QLineEdit:disabled {{
                background-color: {colors.DISABLED_BG};
                color: {colors.DISABLED_TEXT};
            }}
        """

    @staticmethod
    def text_edit():
        """Generate text edit style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QTextEdit {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.input_padding}px;
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
            }}
            QTextEdit:focus {{
                border: {profile.border_width}px solid {colors.BORDER_FOCUS};
            }}
        """

    @staticmethod
    def text_edit_code():
        """Generate code text edit style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QTextEdit {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.input_padding}px;
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                font-family: monospace;
                font-size: {profile.font_size_base}px;
            }}
            QTextEdit:focus {{
                border: {profile.border_width}px solid {colors.BORDER_FOCUS};
            }}
        """

    @staticmethod
    def list_widget():
        """Generate list widget style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QListWidget {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.spacing_small}px;
                background-color: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
            }}
            QListWidget::item {{
                padding: {profile.spacing_small}px;
                border-radius: 2px;
            }}
            QListWidget::item:hover {{
                background-color: {colors.BG_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: {colors.SELECTION};
            }}
        """

    @staticmethod
    def progress_bar():
        """Generate progress bar style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QProgressBar {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                text-align: center;
                height: 25px;
                background-color: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.PRIMARY};
                border-radius: 3px;
            }}
        """

    @staticmethod
    def progress_bar_success():
        """Generate success progress bar style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QProgressBar {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                text-align: center;
                height: 25px;
                background-color: {colors.BG_DARK};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.SUCCESS};
                border-radius: 3px;
            }}
        """

    @staticmethod
    def label_header():
        """Generate header label style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"font-size: {profile.font_size_header}px; font-weight: bold; color: {colors.TEXT_PRIMARY};"

    @staticmethod
    def label_subheader():
        """Generate subheader label style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"font-size: {profile.font_size_subheader}px; font-weight: bold; color: {colors.TEXT_SECONDARY};"

    @staticmethod
    def label_secondary():
        """Generate secondary label style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"color: {colors.TEXT_SECONDARY}; font-style: italic; font-size: {profile.font_size_base}px;"

    @staticmethod
    def label_hint():
        """Generate hint label style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"color: {colors.TEXT_HINT}; font-size: {profile.font_size_small}px;"

    @staticmethod
    def info_box():
        """Generate info box style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            color: {colors.TEXT_SECONDARY};
            padding: {profile.spacing_medium}px;
            background: {colors.BG_MEDIUM};
            border: {profile.border_width}px solid {colors.BORDER_NORMAL};
            border-radius: {profile.border_radius}px;
            font-size: {profile.font_size_base}px;
        """

    @staticmethod
    def combo_box():
        """Generate combo box style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QComboBox {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.input_padding}px;
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
                min-height: {profile.input_height}px;
            }}
            QComboBox:hover {{
                border: {profile.border_width}px solid {colors.BORDER_LIGHT};
            }}
            QComboBox:focus {{
                border: {profile.border_width}px solid {colors.BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors.TEXT_SECONDARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                selection-background-color: {colors.SELECTION};
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
            }}
        """

    @staticmethod
    def spin_box():
        """Generate spin box style."""
        colors = get_theme_manager().get_colors()
        profile = get_size_profile_manager().get_current_profile()

        return f"""
            QSpinBox {{
                border: {profile.border_width}px solid {colors.BORDER_NORMAL};
                border-radius: {profile.border_radius}px;
                padding: {profile.input_padding}px;
                background-color: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                font-size: {profile.font_size_base}px;
                min-height: {profile.input_height}px;
            }}
            QSpinBox:focus {{
                border: {profile.border_width}px solid {colors.BORDER_FOCUS};
            }}
        """


# Create convenience properties for backward compatibility
class Styles:
    """Dynamic styles that adapt to current theme and size profile."""

    @property
    def BUTTON_PRIMARY(self):
        return StyleGenerator.button_primary()

    @property
    def BUTTON_SECONDARY(self):
        return StyleGenerator.button_secondary()

    @property
    def BUTTON_SMALL(self):
        return StyleGenerator.button_small()

    @property
    def BUTTON_SUCCESS(self):
        return StyleGenerator.button_success()

    @property
    def LINE_EDIT(self):
        return StyleGenerator.line_edit()

    @property
    def TEXT_EDIT(self):
        return StyleGenerator.text_edit()

    @property
    def TEXT_EDIT_CODE(self):
        return StyleGenerator.text_edit_code()

    @property
    def LIST_WIDGET(self):
        return StyleGenerator.list_widget()

    @property
    def PROGRESS_BAR(self):
        return StyleGenerator.progress_bar()

    @property
    def PROGRESS_BAR_SUCCESS(self):
        return StyleGenerator.progress_bar_success()

    @property
    def LABEL_HEADER(self):
        return StyleGenerator.label_header()

    @property
    def LABEL_SUBHEADER(self):
        return StyleGenerator.label_subheader()

    @property
    def LABEL_SECONDARY(self):
        return StyleGenerator.label_secondary()

    @property
    def LABEL_HINT(self):
        return StyleGenerator.label_hint()

    @property
    def INFO_BOX(self):
        return StyleGenerator.info_box()

    @property
    def COMBO_BOX(self):
        return StyleGenerator.combo_box()

    @property
    def SPIN_BOX(self):
        return StyleGenerator.spin_box()


# Singleton instances for convenience
Colors = _colors_instance
Styles = Styles()
