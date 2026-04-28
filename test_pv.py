import sys
import os

os.environ["QT_API"] = "pyqt6"
from PyQt6.QtWidgets import QApplication
import pyvista as pv
from pyvistaqt import QtInteractor

def main():
    app = QApplication(sys.argv)
    window = QtInteractor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
