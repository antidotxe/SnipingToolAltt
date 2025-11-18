import keyboard
from typing import Callable, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal


class KeybindManager(QObject):
    
    keybind_triggered = pyqtSignal(str)

    def __init__(self, config_manager=None):
        super().__init__()
        self._keybinds: Dict[str, Callable] = {}
        self._action_to_keybind: Dict[str, str] = {}
        self._listening = False
        self._config_manager = config_manager
        self.kb_list = []

    def register_keybind(self, key_combo: str, callback: Callable, action: Optional[str] = None) -> None:
        self._keybinds[key_combo] = callback
        self.kb_list.append(key_combo)
        
        if action:
            self._action_to_keybind[action] = key_combo
        
        self.keybind_triggered.connect(lambda key: callback() if key == key_combo else None)
        
        if self._listening:
            keyboard.add_hotkey(key_combo, lambda kc=key_combo: self.keybind_triggered.emit(kc))

    def unregister_keybind(self, key_combo: str) -> None:
        if key_combo in self._keybinds:
            if self._listening:
                try:
                    keyboard.remove_hotkey(key_combo)
                except KeyError:
                    pass
            
            del self._keybinds[key_combo]
            if key_combo in self.kb_list:
                self.kb_list.remove(key_combo)
            
            a_remove = None
            for a, kb in self._action_to_keybind.items():
                if kb == key_combo:
                    a_remove = a
                    break
            if a_remove:
                del self._action_to_keybind[a_remove]

    def start_listening(self) -> None:
        if self._listening:
            return
        
        for kc in self._keybinds.keys():
            keyboard.add_hotkey(kc, lambda kc2=kc: self.keybind_triggered.emit(kc2))
        
        self._listening = True

    def stop_listening(self) -> None:
        if not self._listening:
            return
        
        for kc in self._keybinds.keys():
            try:
                keyboard.remove_hotkey(kc)
            except KeyError:
                pass
        
        self._listening = False

    def is_listening(self) -> bool:
        return self._listening

    def reload_keybinds(self, action_callbacks: Dict[str, Callable]) -> None:
        if not self._config_manager:
            raise ValueError("ConfigManager not set. Cannot reload keybinds from config.")
        
        was_l = self._listening
        
        if was_l:
            self.stop_listening()
        
        kbs_remove = list(self._keybinds.keys())
        for kc in kbs_remove:
            self.unregister_keybind(kc)
        
        for act, cb in action_callbacks.items():
            kc = self._config_manager.get_keybind(act)
            if kc:
                self.register_keybind(kc, cb, act)
        
        if was_l:
            self.start_listening()

    def load_keybinds_from_config(self, action_callbacks: Dict[str, Callable]) -> None:
        if not self._config_manager:
            raise ValueError("ConfigManager not set. Cannot load keybinds from config.")
        
        for act, cb in action_callbacks.items():
            kc = self._config_manager.get_keybind(act)
            if kc:
                self.register_keybind(kc, cb, act)

    def update_keybind(self, action: str, new_key_combo: str, callback: Callable) -> None:
        old_kc = self._action_to_keybind.get(action)
        
        if old_kc:
            self.unregister_keybind(old_kc)
        
        self.register_keybind(new_key_combo, callback, action)

    def get_registered_keybinds(self) -> Dict[str, str]:
        return dict(self._keybinds.keys())

    def get_action_keybind(self, action: str) -> Optional[str]:
        return self._action_to_keybind.get(action)
