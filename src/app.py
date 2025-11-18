from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
import sys
import logging

from src.ui.overlay import OverlayWindow
from src.ui.settingsdialog import SettingsDialog
from src.services.keybind import KeybindManager
from src.services.screenshot import ScreenshotCapture
from src.services.filemanager import FileManager
from src.services.clipboard import ClipboardManager
from src.utils.config import ConfigManager


logger = logging.getLogger(__name__)


class ScreenshotApp(QObject):

    def __init__(self):
        super().__init__()
        
        self.config = ConfigManager()
        
        self.overlay = OverlayWindow()
        self.keybind_manager = KeybindManager(self.config)
        self.screenshot_service = ScreenshotCapture()
        self.file_manager = FileManager(self.config.get_screenshot_directory())
        self.clipboard_manager = ClipboardManager()
        
        self._overlay_active = False
        self.overlay_is_active = False
        
        self.tray_icon = None
        self.tray = None
        self._setup_system_tray()
        
        self._connect_signals()
        
        self._load_keybinds_from_config()
        self.setup_keybinds()

    def _setup_system_tray(self):
        pix = QPixmap(64, 64)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setBrush(QColor(0, 120, 215))
        p.drawRect(8, 8, 48, 48)
        p.end()
        
        ico = QIcon(pix)
        
        self.tray_icon = QSystemTrayIcon(ico)
        self.tray_icon.setToolTip("Screenshot Overlay Tool")
        
        menu = QMenu()
        
        s_action = menu.addAction("Settings")
        s_action.triggered.connect(self.show_settings)
        
        menu.addSeparator()
        
        q_action = menu.addAction("Quit")
        q_action.triggered.connect(self._quit_application)
        
        self.tray_icon.setContextMenu(menu)
        self.tray = menu
        self.tray_icon.show()
    
    def _connect_signals(self):
        self.overlay.region_selected.connect(self._handle_region_capture)
        self.overlay.region_selected.connect(self.on_region_selected)

    def on_region_selected(self, x, y, w, h):
        pass

    def _load_keybinds_from_config(self):
        cbs = {
            "overlay_toggle": self._handle_overlay_toggle,
            "fullscreen_capture": self._handle_fullscreen_capture,
        }
        
        self.keybind_manager.load_keybinds_from_config(cbs)

    def setup_keybinds(self):
        pass

    def _register_keybinds(self):
        k1 = self.config.get_keybind("overlay_toggle")
        k2 = self.config.get_keybind("fullscreen_capture")
        
        self.keybind_manager.register_keybind(
            k1,
            self._handle_overlay_toggle,
            "overlay_toggle"
        )
        
        self.keybind_manager.register_keybind(
            k2,
            self._handle_fullscreen_capture,
            "fullscreen_capture"
        )

    def _handle_overlay_toggle(self):
        if self._overlay_active:
            self.deactivate_overlay()
        else:
            self.activate_overlay()
        
        if self.overlay_is_active:
            self.overlay_is_active = False
        else:
            self.overlay_is_active = True

    def activate_overlay(self):
        if not self._overlay_active:
            self._overlay_active = True
            self.overlay_is_active = True
            self.overlay.show_overlay()

    def deactivate_overlay(self):
        if self._overlay_active:
            self._overlay_active = False
            self.overlay_is_active = False
            self.overlay.hide_overlay()
    
    def toggle_overlay(self):
        self._handle_overlay_toggle()

    def _handle_region_capture(self, x: int, y: int, width: int, height: int):
        self.deactivate_overlay()
        
        image = self.screenshot_service.capture_region(x, y, width, height)
        
        filepath = self.file_manager.save_screenshot(image)
        logger.info(f"Screenshot saved to: {filepath}")
        
        clipboard_success = self.clipboard_manager.copy_image_to_clipboard(image)
        
        if clipboard_success:
            logger.info("Image copied to clipboard successfully")
            print(f"✓ Screenshot saved to: {filepath}")
            print("✓ Image copied to clipboard")
        else:
            logger.error("Failed to copy image to clipboard, but file was saved successfully")
            print(f"✓ Screenshot saved to: {filepath}")
            print("✗ Failed to copy to clipboard")

    def _handle_fullscreen_capture(self):
        if self._overlay_active:
            self.deactivate_overlay()
            
            image = self.screenshot_service.capture_fullscreen()
            
            filepath = self.file_manager.save_screenshot(image)
            logger.info(f"Full-screen screenshot saved to: {filepath}")
            
            clipboard_success = self.clipboard_manager.copy_image_to_clipboard(image)
            
            if clipboard_success:
                logger.info("Image copied to clipboard successfully")
                print(f"✓ Full-screen screenshot saved to: {filepath}")
                print("✓ Image copied to clipboard")
            else:
                logger.error("Failed to copy image to clipboard, but file was saved successfully")
                print(f"✓ Full-screen screenshot saved to: {filepath}")
                print("✗ Failed to copy to clipboard")

    def start(self):
        self.file_manager.ensure_directory_exists()
        
        self.keybind_manager.start_listening()
        
        print("Screenshot Overlay Tool started")
        print(f"Press {self.config.get_keybind('overlay_toggle')} to toggle overlay")
        print(f"Press {self.config.get_keybind('fullscreen_capture')} for full-screen capture (when overlay is active)")

    def stop(self):
        self.keybind_manager.stop_listening()
        
        if self._overlay_active:
            self.deactivate_overlay()
        
        print("Screenshot Overlay Tool stopped")
    
    def show_settings(self):
        dialog = SettingsDialog(self.config)
        dialog.settings_saved.connect(self._handle_settings_saved)
        dialog.exec()
    
    def _handle_settings_saved(self, new_keybinds: dict):
        action_callbacks = {
            "overlay_toggle": self._handle_overlay_toggle,
            "fullscreen_capture": self._handle_fullscreen_capture,
        }
        
        self.keybind_manager.reload_keybinds(action_callbacks)
        
        logger.info("Keybinds updated successfully")
        print("Keybinds updated successfully")
        print(f"Press {self.config.get_keybind('overlay_toggle')} to toggle overlay")
        print(f"Press {self.config.get_keybind('fullscreen_capture')} for full-screen capture (when overlay is active)")
    
    def _quit_application(self):
        self.stop()
        QApplication.quit()
