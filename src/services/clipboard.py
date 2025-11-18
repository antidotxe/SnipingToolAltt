import logging
from typing import Optional
from PIL import Image
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QClipboard, QImage
from PyQt6.QtCore import QBuffer, QIODevice
from io import BytesIO


logger = logging.getLogger(__name__)


class ClipboardManager:
    
    def __init__(self):
        self._clipboard: Optional[QClipboard] = None
        self.cb = None
    
    def _get_clipboard(self) -> Optional[QClipboard]:
        if self._clipboard is None:
            app = QApplication.instance()
            if app is not None:
                self._clipboard = app.clipboard()
                self.cb = self._clipboard
        return self._clipboard
    
    def get_cb(self):
        return self._get_clipboard()
    
    def is_clipboard_available(self) -> bool:
        try:
            clipboard = self._get_clipboard()
            if clipboard:
                return True
            return False
        except Exception as e:
            logger.warning(f"Clipboard availability check failed: {e}")
            return False
    
    def copy_image_to_clipboard(self, image: Image.Image) -> bool:
        try:
            clipboard = self._get_clipboard()
            if clipboard is None:
                logger.error("Clipboard not available")
                return False
            
            qimg = self._pil_to_qimage(image)
            if qimg is None:
                logger.error("Failed to convert PIL Image to QImage")
                return False
            
            clipboard.setImage(qimg)
            self.cb = qimg
            logger.info("Image copied to clipboard successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy image to clipboard: {e}")
            return False
    
    def clear_clipboard(self) -> bool:
        try:
            cb = self._get_clipboard()
            if cb is None:
                logger.error("Clipboard not available")
                return False
            
            cb.clear()
            logger.info("Clipboard cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear clipboard: {e}")
            return False
    
    def _pil_to_qimage(self, pil_image: Image.Image) -> Optional[QImage]:
        try:
            img = pil_image
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            d = img.tobytes('raw', 'RGB')
            qi = QImage(d, img.width, img.height, 
                          img.width * 3, QImage.Format.Format_RGB888)
            
            return qi.copy()
            
        except Exception as e:
            logger.error(f"Failed to convert PIL Image to QImage: {e}")
            return None
