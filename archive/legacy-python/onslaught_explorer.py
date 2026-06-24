#!/usr/bin/env python3
"""
Onslaught Career Editor - GUI Entry Point
PyQt6-based toolkit for Battle Engine Aquila

Usage:
    python3 onslaught_explorer.py
    python3 onslaught_explorer.py --file save.bes
    python3 onslaught_explorer.py --file defaultoptions.bea
"""

import sys
import argparse
from pathlib import Path


def main():
    """Main entry point for the GUI application"""
    parser = argparse.ArgumentParser(
        description="Onslaught Career Editor - Battle Engine Aquila Toolkit"
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help="Open a .bes/.bea save/options file on startup"
    )
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help="Show version and exit"
    )
    args = parser.parse_args()

    # Import here to avoid slow startup for --version
    from onslaught.core.constants import APP_NAME, APP_VERSION

    if args.version:
        print(f"{APP_NAME} v{APP_VERSION}")
        return 0

    # Check for PyQt6
    try:
        from PyQt6.QtWidgets import QApplication, QStyleFactory
    except ImportError:
        print("Error: PyQt6 is required. Install with:")
        print("  pip install PyQt6")
        return 1

    # Create application
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Apply a consistent light theme to match the WPF app
    from onslaught.gui.theme import apply_light_theme
    apply_light_theme(app)

    # Import and create main window
    from onslaught.gui.main_window import MainWindow
    window = MainWindow()

    # Open file if specified
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            window.open_path(file_path)
        else:
            print(f"Warning: File not found: {args.file}")

    # Show window and run event loop
    window.show()
    return_code = app.exec()
    return return_code


if __name__ == "__main__":
    sys.exit(main())
