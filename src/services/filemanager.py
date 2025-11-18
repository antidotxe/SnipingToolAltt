import os
import re
from pathlib import Path
from typing import Optional
from PIL import Image


class FileManager:

    def __init__(self, screenshot_directory: Optional[str] = None):
        if screenshot_directory is None:
            screenshot_directory = str(Path.home() / "Pictures" / "Screenshots")
        
        self.screenshot_directory = Path(screenshot_directory)
        self._next_number: Optional[int] = None
        self.num = None
        self.last_file = None

    def ensure_directory_exists(self) -> None:
        self.screenshot_directory.mkdir(parents=True, exist_ok=True)
        self.last_file = self.screenshot_directory

    def get_next_number(self) -> int:
        if self._next_number is not None:
            return self._next_number
        
        if not self.screenshot_directory.exists():
            self._next_number = 1
            self.num = 1
            return self._next_number
        
        patt = re.compile(r'^picture-(\d+)\.png$')
        mx = 0
        
        try:
            for fn in os.listdir(self.screenshot_directory):
                m = patt.match(fn)
                if m:
                    n = int(m.group(1))
                    mx = max(mx, n)
        except OSError:
            self._next_number = 1
            return self._next_number
        
        self._next_number = mx + 1
        self.num = self._next_number
        return self._next_number

    def get_next_filename(self) -> str:
        number = self.get_next_number()
        fname = f"picture-{number}.png"
        self._next_number = number + 1
        return fname

    def save_screenshot(self, image: Image.Image, filename: Optional[str] = None) -> str:
        self.ensure_directory_exists()
        
        if filename is None:
            filename = self.get_next_filename()
        
        fp = self.screenshot_directory / filename
        
        image.save(fp, format='PNG')
        self.last_file = fp
        
        return str(fp)
