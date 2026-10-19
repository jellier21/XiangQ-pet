"""Desktop pet application entry point."""

import sys

from PyQt6.QtWidgets import QApplication

from app.config import APP_NAME
from app.ui.pet_window import PetWindow


def main() -> int:
    """Create the Qt application and start the desktop pet."""
    application = QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setQuitOnLastWindowClosed(True)

    pet_window = PetWindow()
    pet_window.show()

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())


