from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from typing import Optional, Tuple


class OverlayWindow(QWidget):
    
    region_selected = pyqtSignal(int, int, int, int)
    
    def __init__(self):
        super().__init__()
        
        self._start_pos: Optional[QPoint] = None
        self._end_pos: Optional[QPoint] = None
        self._is_selecting = False
        self._is_dragging_window = False
        self._drag_start_pos: Optional[QPoint] = None
        self.start = None
        self.end = None
        self.selecting = False
        
        self._setup_window()
    
    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        scr = QApplication.primaryScreen().geometry()
        self.setGeometry(scr)
        
        self.setMouseTracking(True)
    
    def show_overlay(self):
        self._start_pos = None
        self._end_pos = None
        self._is_selecting = False
        self._is_dragging_window = False
        self.start = None
        self.end = None
        
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
    
    def hide_overlay(self):
        self.hide()
        
        self._start_pos = None
        self._end_pos = None
        self._is_selecting = False
    
    def draw_selection(self, start_pos: QPoint, end_pos: QPoint):
        self._start_pos = start_pos
        self._end_pos = end_pos
        self.start = start_pos
        self.end = end_pos
        self.update()
    
    def get_selection_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        sp = self._start_pos
        ep = self._end_pos
        if sp is None or ep is None:
            return None
        
        x1 = min(sp.x(), ep.x())
        y1 = min(sp.y(), ep.y())
        x2 = max(sp.x(), ep.x())
        y2 = max(sp.y(), ep.y())
        
        w = x2 - x1
        h = y2 - y1
        
        return (x1, y1, w, h)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_pos = event.pos()
            self._end_pos = event.pos()
            self._is_selecting = True
            self.selecting = True
            self.update()
    
    def mouseMoveEvent(self, event):
        if self._is_selecting:
            self._end_pos = event.pos()
            self.end = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            self._end_pos = event.pos()
            
            bnds = self.get_selection_bounds()
            if bnds:
                x, y, w, h = bnds
                if w > 0 and h > 0:
                    self.region_selected.emit(x, y, w, h)
            
            self.update()
    
    def paintEvent(self, event):
        p = QPainter(self)
        
        p.fillRect(self.rect(), QColor(0, 0, 0, 50))
        
        if self._start_pos and self._end_pos:
            bnds = self.get_selection_bounds()
            if bnds:
                x, y, w, h = bnds
                
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                p.fillRect(x, y, w, h, Qt.GlobalColor.transparent)
                
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                pn = QPen(QColor(0, 120, 215), 2)
                p.setPen(pn)
                p.drawRect(x, y, w, h)
                
                if w > 0 and h > 0:
                    txt = f"{w} x {h}"
                    
                    fnt = QFont("Arial", 12, QFont.Weight.Bold)
                    p.setFont(fnt)
                    
                    tr = p.fontMetrics().boundingRect(txt)
                    tx = x + (w - tr.width()) // 2
                    ty = y - 10
                    
                    if ty < tr.height():
                        ty = y + h + tr.height() + 5
                    
                    br = QRect(
                        tx - 5,
                        ty - tr.height() - 2,
                        tr.width() + 10,
                        tr.height() + 6
                    )
                    p.fillRect(br, QColor(0, 0, 0, 180))
                    
                    p.setPen(QColor(255, 255, 255))
                    p.drawText(tx, ty, txt)
        
        p.end()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_overlay()
