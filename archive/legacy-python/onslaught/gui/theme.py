from PyQt6.QtGui import QPalette, QColor

# Aligned with C# Material Design BundledTheme (Indigo primary / Blue secondary)
ACCENT_COLOR = "#3F51B5"  # Material Design Indigo 500
WINDOW_BG = "#FAFAFA"  # Material grey-50
TEXT_COLOR = "#212121"  # Material grey-900
SUBTLE_TEXT = "#757575"  # Material grey-600


def apply_light_theme(app) -> None:
    """Apply a light palette aligned with the C# WPF Material Design Indigo theme."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(WINDOW_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F5F5F5"))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Button, QColor("#E8EAF6"))  # Indigo 50
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_COLOR))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT_COLOR))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link, QColor(ACCENT_COLOR))
    app.setPalette(palette)
