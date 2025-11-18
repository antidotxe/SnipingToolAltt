import copy
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import keyboard


class ConfigManager:

    DEFAULT_CONFIG = {
        "keybinds": {
            "overlay_toggle": "ctrl+shift+s",
            "fullscreen_capture": "ctrl+shift+f",
        },
        "screenshot_directory": str(Path.home() / "Pictures" / "Screenshots"),
    }

    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            cfg_dir = Path.home() / ".screenshot_overlay_tool"
            config_file = cfg_dir / "config.json"
        else:
            config_file = Path(config_file)

        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.cfg = None
        self.load_config()

    def load_config(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                    self.cfg = self.config
            except (json.JSONDecodeError, IOError):
                self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        else:
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)

    def save_config(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_keybind(self, action: str) -> str:
        kb = self.config.get("keybinds", {}).get(
            action, self.DEFAULT_CONFIG["keybinds"].get(action, "")
        )
        return kb

    def set_keybind(self, action: str, key_combo: str) -> None:
        if "keybinds" not in self.config:
            self.config["keybinds"] = {}

        self.config["keybinds"][action] = key_combo

    def get_screenshot_directory(self) -> str:
        d = self.config.get(
            "screenshot_directory",
            self.DEFAULT_CONFIG["screenshot_directory"],
        )
        return d

    def set_screenshot_directory(self, directory: str) -> None:
        self.config["screenshot_directory"] = directory

    def validate_keybind(self, key_combo: str, check_conflicts: bool = False) -> Tuple[bool, Optional[str]]:
        if not key_combo or not key_combo.strip():
            return False, "Keybind cannot be empty"

        norm = key_combo.strip().lower()

        v_mods = {'ctrl', 'shift', 'alt', 'win', 'cmd', 'super'}
        
        v_keys = set('abcdefghijklmnopqrstuvwxyz0123456789')
        v_keys.update([f'f{i}' for i in range(1, 25)])
        v_keys.update(['space', 'enter', 'return', 'tab', 'backspace', 'delete', 
                          'escape', 'esc', 'up', 'down', 'left', 'right',
                          'home', 'end', 'pageup', 'pagedown', 'insert',
                          'plus', 'minus', 'multiply', 'divide'])

        if '+' not in norm:
            return False, "Keybind must contain at least one modifier (e.g., 'ctrl+s')"

        pts = [p.strip() for p in norm.split('+')]
        
        if len(pts) < 2:
            return False, "Keybind must have at least one modifier and one key"

        mods = pts[:-1]
        k = pts[-1]

        for m in mods:
            if m not in v_mods:
                return False, f"Invalid modifier: '{m}'. Valid modifiers: {', '.join(sorted(v_mods))}"

        if k not in v_keys and k not in v_mods:
            return False, f"Invalid key: '{k}'"

        if len(mods) != len(set(mods)):
            return False, "Keybind contains duplicate modifiers"

        try:
            keyboard.parse_hotkey(norm)
        except Exception as e:
            return False, f"Invalid keybind format: {str(e)}"

        if check_conflicts:
            try:
                tcb = lambda: None
                keyboard.add_hotkey(norm, tcb, suppress=False)
                keyboard.remove_hotkey(norm)
            except Exception as e:
                return False, f"Keybind may be in use or unavailable: {str(e)}"

        return True, None
