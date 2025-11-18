from PIL import ImageGrab
from PIL.Image import Image
from typing import Tuple


class ScreenshotCapture:
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image:
        bbox = (x, y, x + width, y + height)
        return ImageGrab.grab(bbox=bbox)
    
    def capture_fullscreen(self) -> Image:
        return ImageGrab.grab()
    
    def get_screen_geometry(self) -> Tuple[int, int]:
        img = ImageGrab.grab()
        return img.size
