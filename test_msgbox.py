import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QMainWindow

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()
    
    QMessageBox.warning(window, "Test", "This is a test")
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
