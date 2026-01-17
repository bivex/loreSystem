"""
Main entry point for LoreForge application.
"""
import sys
from PyQt6.QtWidgets import QApplication

from src.presentation.gui.main_window import MainWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("LoreForge")
    app.setOrganizationName("LoreForge")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())