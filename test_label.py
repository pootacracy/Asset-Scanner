import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
import PIL.Image

# create a dummy image
img = PIL.Image.new("RGB", (800, 600), color="blue")
img.save("dummy.jpg")

class ResizableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 1)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pixmap = None

    def setPixmap(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        print(f"setPixmap called: isNull={self._pixmap.isNull()}")
        self.update_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_pixmap()

    def sizeHint(self) -> QSize:
        return QSize(1, 1)

    def minimumSizeHint(self) -> QSize:
        return QSize(1, 1)

    def update_pixmap(self) -> None:
        if self._pixmap:
            print(f"update_pixmap: size={self.size().width()}x{self.size().height()}")
            scaled_pixmap = self._pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)
            
    def clear(self) -> None:
        self._pixmap = None
        super().clear()

app = QApplication(sys.argv)
window = QMainWindow()
w = QWidget()
l = QVBoxLayout()
lbl = ResizableLabel()
l.addWidget(lbl)
w.setLayout(l)
window.setCentralWidget(w)
window.resize(400, 300)

pixmap = QPixmap("dummy.jpg")
lbl.setPixmap(pixmap)

window.show()
sys.exit(app.exec())
