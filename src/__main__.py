import sys
import signal
from PyQt6.QtWidgets import QApplication

from src.app import ScreenshotApp


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    screenshot_app = ScreenshotApp()
    screenshot_app.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
