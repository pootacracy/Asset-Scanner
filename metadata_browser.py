import sys
import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QVBoxLayout, QWidget, QGridLayout, QLabel, QHBoxLayout, QListWidgetItem, QPushButton, QComboBox, QLineEdit, QFormLayout, QCompleter, QFrame, QToolButton, QScrollArea, QSplitter, QMessageBox, QSizePolicy, QStyle, QGroupBox, QAbstractItemView, QTreeView, QMenu, QDialog, QDialogButtonBox, QSlider, QListView
from PyQt6.QtGui import QAction, QFileSystemModel, QPixmap, QPalette, QColor, QStandardItemModel, QStandardItem, QDesktopServices, QIcon, QCursor, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QTimer
import requests
import shutil
import datetime
#import ollama

try:
    os.environ["QT_API"] = "pyqt6"
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

# ... (I'll skip the full 2000 lines in this thought block, but I'll include the full content in the tool call)
