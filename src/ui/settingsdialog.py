from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QMessageBox, QGroupBox,
    QFormLayout, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QKeyEvent
from typing import Dict, Optional


class KeybindEdit(QLineEdit):
    
    keybind_captured = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click and press keys...")
        self._capturing = False
        self._modifiers = []
        self.cap = False
        self.mods = []
        
    def mousePressEvent(self, event):
        self._capturing = True
        self.cap = True
        self._modifiers = []
        self.mods = []
        self.setText("Press keys...")
        self.setStyleSheet("background-color: #e3f2fd;")
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if not self._capturing:
            return
        
        k = event.key()
        
        if k in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, 
                   Qt.Key.Key_Meta, Qt.Key.Key_Super_L, Qt.Key.Key_Super_R):
            return
        
        mods = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            mods.append("ctrl")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            mods.append("shift")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            mods.append("alt")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            mods.append("win")
        
        kn = QKeySequence(k).toString().lower()
        
        if mods:
            kb = "+".join(mods) + "+" + kn
        else:
            kb = kn
        
        self.setText(kb)
        self.setStyleSheet("")
        self._capturing = False
        self.cap = False
        
        self.keybind_captured.emit(kb)
        
        event.accept()
    
    def focusOutEvent(self, event):
        if self._capturing:
            self._capturing = False
            self.cap = False
            self.setStyleSheet("")
            if not self.text() or self.text() == "Press keys...":
                self.setText("")
        super().focusOutEvent(event)


class SettingsDialog(QDialog):
    
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.cm = config_manager
        self.keybind_edits: Dict[str, KeybindEdit] = {}
        self.original_keybinds: Dict[str, str] = {}
        self.orig_kb = {}
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        l = QVBoxLayout()
        
        kg = self._create_keybinds_group()
        l.addWidget(kg)
        
        bl = self._create_button_layout()
        l.addLayout(bl)
        
        self.setLayout(l)
    
    def _create_keybinds_group(self) -> QGroupBox:
        g = QGroupBox("Keyboard Shortcuts")
        fl = QFormLayout()
        
        oe = KeybindEdit()
        oe.keybind_captured.connect(
            lambda kb: self._validate_keybind("overlay_toggle", kb)
        )
        self.keybind_edits["overlay_toggle"] = oe
        fl.addRow("Toggle Overlay:", oe)
        
        fe = KeybindEdit()
        fe.keybind_captured.connect(
            lambda kb: self._validate_keybind("fullscreen_capture", kb)
        )
        self.keybind_edits["fullscreen_capture"] = fe
        fl.addRow("Fullscreen Capture:", fe)
        
        hl = QLabel(
            "Click on a field and press your desired key combination.\n"
            "Example: Ctrl+Shift+S"
        )
        hl.setStyleSheet("color: #666; font-size: 10px;")
        fl.addRow("", hl)
        
        g.setLayout(fl)
        return g
    
    def _create_button_layout(self) -> QHBoxLayout:
        l = QHBoxLayout()
        
        rb = QPushButton("Reset to Defaults")
        rb.clicked.connect(self._reset_to_defaults)
        l.addWidget(rb)
        
        l.addStretch()
        
        cb = QPushButton("Cancel")
        cb.clicked.connect(self.reject)
        l.addWidget(cb)
        
        sb = QPushButton("Save")
        sb.setDefault(True)
        sb.clicked.connect(self._save_settings)
        l.addWidget(sb)
        
        return l
    
    def _load_current_settings(self):
        for act, ed in self.keybind_edits.items():
            kb = self.config_manager.get_keybind(act)
            ed.setText(kb)
            self.original_keybinds[act] = kb
            self.orig_kb[act] = kb
    
    def _validate_keybind(self, action: str, keybind: str):
        iv, em = self.config_manager.validate_keybind(keybind, check_conflicts=False)
        
        if not iv:
            QMessageBox.warning(
                self,
                "Invalid Keybind",
                f"The keybind '{keybind}' is invalid:\n{em}"
            )
            self.keybind_edits[action].setText(self.original_keybinds[action])
            return
        
        for oa, oe in self.keybind_edits.items():
            if oa != action and oe.text() == keybind:
                QMessageBox.warning(
                    self,
                    "Keybind Conflict",
                    f"The keybind '{keybind}' is already assigned to '{oa.replace('_', ' ').title()}'.\n"
                    "Please choose a different keybind."
                )
                self.keybind_edits[action].setText(self.original_keybinds[action])
                return
        
        self.keybind_edits[action].setStyleSheet("background-color: #c8e6c9;")
    
    def _reset_to_defaults(self):
        r = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if r == QMessageBox.StandardButton.Yes:
            for act, ed in self.keybind_edits.items():
                dk = self.config_manager.DEFAULT_CONFIG["keybinds"].get(act, "")
                ed.setText(dk)
                ed.setStyleSheet("")
    
    def _save_settings(self):
        nk = {}
        for act, ed in self.keybind_edits.items():
            kb = ed.text().strip()
            
            if not kb:
                QMessageBox.warning(
                    self,
                    "Empty Keybind",
                    f"Please set a keybind for '{act.replace('_', ' ').title()}'."
                )
                return
            
            iv, em = self.config_manager.validate_keybind(kb, check_conflicts=False)
            if not iv:
                QMessageBox.warning(
                    self,
                    "Invalid Keybind",
                    f"The keybind for '{act.replace('_', ' ').title()}' is invalid:\n{em}"
                )
                return
            
            nk[act] = kb
        
        kv = list(nk.values())
        if len(kv) != len(set(kv)):
            QMessageBox.warning(
                self,
                "Duplicate Keybinds",
                "Multiple actions cannot have the same keybind.\nPlease use unique keybinds for each action."
            )
            return
        
        for act, kb in nk.items():
            self.config_manager.set_keybind(act, kb)
        
        self.config_manager.save_config()
        
        self.settings_saved.emit(nk)
        
        QMessageBox.information(
            self,
            "Settings Saved",
            "Your settings have been saved successfully.\n"
            "The new keybinds will be applied immediately."
        )
        
        self.accept()
