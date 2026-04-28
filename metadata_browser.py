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



def apply_dark_theme(app):
    """Apply a dark theme to the application."""
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    dark_stylesheet = """
    QMainWindow, QWidget {
        background-color: #16161E;
        color: #C0CAF5;
    }
    QMenu {
        background-color: #1A1B26;
        color: #C0CAF5;
        border: 1px solid #292E42;
    }
    QMenu::item {
        padding: 6px 24px 6px 24px;
        background-color: transparent;
    }
    QMenu::item:selected {
        background-color: rgba(88, 166, 255, 0.15);
        color: #58A6FF;
    }
    QMenu::separator {
        height: 1px;
        background-color: #292E42;
        margin: 4px 0px;
    }
    QPushButton {
        background-color: #1F2335;
        border: 1px solid #292E42;
        border-radius: 6px;
        padding: 6px 12px;
        color: #C0CAF5;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #292E42;
        border: 1px solid #58A6FF;
    }
    QPushButton:pressed {
        background-color: #3B4261;
    }
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #1A1B26;
        color: #C0CAF5;
        border: 1px solid #292E42;
        border-radius: 4px;
        padding: 6px;
        selection-background-color: #58A6FF;
    }
    QListWidget, QTreeView {
        background-color: #1A1B26;
        color: #C0CAF5;
        border: 1px solid #292E42;
        border-radius: 6px;
        outline: none;
    }
    QListWidget::item, QTreeView::item {
        padding: 4px;
        border-radius: 4px;
        margin: 2px 4px;
        border: 1px solid transparent;
    }
    QListWidget::item:selected, QTreeView::item:selected {
        background-color: rgba(88, 166, 255, 0.15);
        color: #58A6FF;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
    QListWidget::item:hover, QTreeView::item:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    QLabel {
        color: #C0CAF5;
    }
    QComboBox {
        background-color: #1F2335;
        border: 1px solid #292E42;
        border-radius: 4px;
        color: #C0CAF5;
        padding: 4px 8px;
    }
    QComboBox::drop-down {
        border: none;
        background: transparent;
    }
    QComboBox QAbstractItemView {
        background-color: #1F2335;
        color: #C0CAF5;
        border: 1px solid #292E42;
        selection-background-color: rgba(88, 166, 255, 0.15);
        selection-color: #58A6FF;
        border-radius: 4px;
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 10px;
        margin: 0px 2px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #3B4261;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #58A6FF;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background: transparent;
        height: 10px;
        margin: 0px 0px 2px 0px;
    }
    QScrollBar::handle:horizontal {
        background: #3B4261;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #58A6FF;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    QSplitter::handle {
        background-color: transparent;
    }
    QMessageBox {
        background-color: #16161E;
        color: #C0CAF5;
    }
    """
    app.setStyleSheet(dark_stylesheet)

    # Customize palette for links
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Link, QColor("#58A6FF"))  # Lighter/muted blue for dark mode
    app.setPalette(palette)


# Validation and Sanitization Functions
def validate_search_terms(search_terms: str) -> str:
    """Validate and sanitize search terms.
    
    Args:
        search_terms: The search terms string to validate.
    
    Returns:
        The sanitized search terms string.
    
    Raises:
        ValueError: If search_terms is not a string, empty, exceeds 200 characters,
                   or contains problematic characters.
    """
    if not isinstance(search_terms, str):
        raise ValueError("Search terms must be a string")
    
    sanitized = search_terms.strip()
    if not sanitized:
        raise ValueError("Search terms cannot be empty")
    
    if len(sanitized) > 200:
        raise ValueError("Search terms cannot exceed 200 characters")
    
    # Remove potentially problematic characters but keep basic punctuation
    sanitized = re.sub(r'[^\w\s\-\.&]', '', sanitized)
    return sanitized


def validate_asset_name(asset_name: str) -> str:
    """Validate asset name for filename compatibility.
    
    Args:
        asset_name: The asset name string to validate.
    
    Returns:
        The validated and sanitized asset name string.
    
    Raises:
        ValueError: If asset_name is not a string, empty, exceeds 255 characters,
                   or contains invalid filename characters.
    """
    if not isinstance(asset_name, str):
        raise ValueError("Asset name must be a string")
    
    sanitized = asset_name.strip()
    if not sanitized:
        raise ValueError("Asset name cannot be empty")
    
    if len(sanitized) > 255:
        raise ValueError("Asset name cannot exceed 255 characters")
    
    # Check for invalid filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, sanitized):
        raise ValueError("Asset name contains invalid filename characters")
    
    return sanitized


def validate_path(path_str: str | Path) -> Path:
    """Validate and convert path to Path object.
    
    Args:
        path_str: The path string or Path object to validate.
    
    Returns:
        A Path object representing the validated path.
    
    Raises:
        ValueError: If path_str is not a string or Path object, or if path doesn't exist.
    """
    if not isinstance(path_str, (str, Path)):
        raise ValueError("Path must be a string or Path object")
    
    path = Path(path_str)
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    return path


def validate_csv_file(csv_file: str | Path) -> Path:
    """Validate CSV file exists and is readable.
    
    Args:
        csv_file: The CSV file path to validate.
    
    Returns:
        A Path object representing the validated CSV file.
    
    Raises:
        ValueError: If file doesn't exist, is not a file, or is not a CSV file.
    """
    if not isinstance(csv_file, (str, Path)):
        raise ValueError("CSV file path must be a string or Path object")
    
    csv_path = Path(csv_file)
    if not csv_path.exists():
        raise ValueError(f"CSV file not found: {csv_path}")
    
    if not csv_path.is_file():
        raise ValueError(f"Path is not a file: {csv_path}")
    
    if csv_path.suffix.lower() != '.csv':
        raise ValueError(f"File is not a CSV file: {csv_path}")
    
    return csv_path


def validate_csv_structure(fieldnames: List[str], required_fields: List[str]) -> bool:
    """Validate CSV has required fields.
    
    Args:
        fieldnames: List of field names from CSV header.
        required_fields: List of required field names.
    
    Returns:
        True if validation passes.
    
    Raises:
        ValueError: If fieldnames is empty or required fields are missing.
    """
    if not fieldnames:
        raise ValueError("CSV file is empty or has no header row")
    
    missing_fields = set(required_fields) - set(fieldnames)
    if missing_fields:
        raise ValueError(f"CSV file is missing required fields: {', '.join(missing_fields)}")
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be safe for use as a filename.
    
    Args:
        filename: The filename string to sanitize.
    
    Returns:
        The sanitized filename string with invalid characters removed or replaced.
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Replace multiple underscores with single
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    # Remove leading/trailing whitespace or dots
    sanitized = sanitized.strip('. ')
    return sanitized


# Worker Classes for Threading
class SearchWorker(QThread):
    """Worker thread for performing Google Image Search.
    
    This class handles asynchronous Google Image Search API requests
    to keep the UI responsive during network operations.
    
    Signals:
        finished: Emitted when the search operation completes.
        error: Emitted with error message if search fails.
        results_ready: Emitted with list of search results when successful.
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    results_ready = pyqtSignal(list)
    
    def __init__(self, search_url: str, params: Dict[str, Any]) -> None:
        """Initialize the SearchWorker.
        
        Args:
            search_url: The Google Custom Search API endpoint URL.
            params: Dictionary of query parameters for the API request.
        """
        super().__init__()
        self.search_url = search_url
        self.params = params
    
    def run(self) -> None:
        """Execute the search in the worker thread.
        
        Makes HTTP request to Google Custom Search API with timeout handling.
        Emits results_ready signal with API results or error signal on failure.
        """
        try:
            response = requests.get(self.search_url, params=self.params, timeout=10)
            response.raise_for_status()
            results = response.json().get("items", [])
            self.results_ready.emit(results)
        except requests.exceptions.Timeout:
            self.error.emit("Search request timed out. Please try again.")
        except requests.exceptions.HTTPError as e:
            status = None
            body = ""
            try:
                if e.response is not None:
                    status = e.response.status_code
                    body = e.response.text
            except Exception:
                pass
            if status == 403:
                self.error.emit("Search failed: 403 Forbidden — check Google API key, Custom Search Engine ID, billing, and API restrictions.")
            else:
                self.error.emit(f"Search failed: HTTP {status} — {body}")
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Search failed: {str(e)}")
        finally:
            self.finished.emit()


class ImageDownloadWorker(QThread):
    """Worker thread for downloading image thumbnails.
    
    Downloads images in parallel from provided URLs with timeout handling.
    Keeps the UI responsive while fetching images.
    
    Signals:
        image_ready: Emitted (index, pixmap, url) when image downloads successfully.
        download_error: Emitted (index, message) when image download fails.
        finished: Emitted when all downloads complete.
    """
    image_ready = pyqtSignal(int, QPixmap, str)  # index, pixmap, image_url
    download_error = pyqtSignal(int, str)  # index, error_message
    finished = pyqtSignal()
    
    def __init__(self, image_urls: List[str]) -> None:
        """Initialize the ImageDownloadWorker.
        
        Args:
            image_urls: List of image URLs to download.
        """
        super().__init__()
        self.image_urls = image_urls
    
    def run(self) -> None:
        """Download images in the worker thread.
        
        Fetches each image with timeout and error handling.
        Emits image_ready signal for successful downloads or
        download_error signal for failures.
        """
        for index, image_url in enumerate(self.image_urls):
            try:
                response = requests.get(image_url, timeout=15)
                response.raise_for_status()
                image_data = response.content
                
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.image_ready.emit(index, pixmap, image_url)
            except requests.exceptions.Timeout:
                self.download_error.emit(index, f"Image {index + 1} download timed out")
            except requests.exceptions.RequestException as e:
                self.download_error.emit(index, f"Failed to download image {index + 1}: {str(e)}")
        
        self.finished.emit()


class ThumbnailLoaderWorker(QThread):
    """Worker thread to load thumbnails asynchronously."""
    thumbnail_loaded = pyqtSignal(int, str, QIcon)

    def __init__(self, image_paths: List[str], icon_size: int = 40):
        super().__init__()
        self.image_paths = image_paths
        self.icon_size = icon_size
        self._is_running = True

    def run(self):
        for index, path in enumerate(self.image_paths):
            if not self._is_running:
                break
            try:
                # print(f"Loading thumbnail: {path}")
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.icon_size, self.icon_size,
                        Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    )
                    icon = QIcon(scaled_pixmap)
                    self.thumbnail_loaded.emit(index, path, icon)
                else:
                    print(f"Warning: Failed to load pixmap for {path}")
            except Exception as e:
                print(f"Error loading thumbnail for {path}: {e}")

    def stop(self):
        self._is_running = False

class EditAssetDialog(QDialog):
    """Dialog for editing asset metadata."""
    def __init__(self, asset_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Asset Metadata")
        self.asset_data = asset_data
        self.layout = QVBoxLayout(self)
        self.inputs = {}

        form_layout = QFormLayout()
        
        # Fields to edit
        fields = ["Asset Directory", "Asset Path", "Asset Images Path"]
        for field in fields:
            line_edit = QLineEdit(str(asset_data.get(field, "")))
            self.inputs[field] = line_edit
            form_layout.addRow(f"{field}:", line_edit)
        
        self.layout.addLayout(form_layout)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """Return the updated data."""
        updated_data = self.asset_data.copy()
        for field, line_edit in self.inputs.items():
            updated_data[field] = line_edit.text()
        return updated_data

class SaveImagesWorker(QThread):
    """Worker thread for saving downloaded images to disk.
    
    Handles saving multiple images to files with progress tracking
    and error handling. Keeps the UI responsive during file I/O.
    
    Signals:
        progress: Emitted (current, total) for progress updates.
        error: Emitted with error message if save fails.
        finished: Emitted when all images are saved.
    """
    progress = pyqtSignal(int, int)  # current, total
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, image_urls: List[str], images_folder: Path, asset_name: str) -> None:
        """Initialize the SaveImagesWorker.
        
        Args:
            image_urls: List of image URLs to download and save.
            images_folder: Path object for the folder to save images.
            asset_name: Name of the asset (used for filename generation).
        """
        super().__init__()
        self.image_urls = image_urls
        self.images_folder = images_folder
        self.asset_name = asset_name
    
    def run(self) -> None:
        """Download and save images in the worker thread.
        
        Fetches each image and saves it to disk with timeout handling.
        Emits progress signal for each saved image or error signal on failure.
        """
        try:
            total_images = len(self.image_urls)
            for index, image_url in enumerate(self.image_urls):
                try:
                    response = requests.get(image_url, timeout=15)
                    response.raise_for_status()
                    image_data = response.content
                    
                    safe_asset_name = sanitize_filename(self.asset_name)
                    file_path = self.images_folder / f"{safe_asset_name}_{index + 1}.jpg"
                    
                    file_path.write_bytes(image_data)
                    self.progress.emit(index + 1, total_images)
                except requests.exceptions.RequestException as e:
                    self.error.emit(f"Failed to save image {index + 1}: {str(e)}")
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Unexpected error during save: {str(e)}")
            self.finished.emit()


class ResizableLabel(QLabel):
    """QLabel that resizes its pixmap to fill the available space while maintaining aspect ratio."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 1)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pixmap = None

    def setPixmap(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self.update_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_pixmap()

    def sizeHint(self) -> QSize:
        return QSize(1, 1)

    def minimumSizeHint(self) -> QSize:
        return QSize(1, 1)

    def update_pixmap(self) -> None:
        if self._pixmap and not self._pixmap.isNull():
            if self.width() <= 1 or self.height() <= 1:
                return
            # Scale to the full size of the widget
            scaled_pixmap = self._pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)
            
    def clear(self) -> None:
        self._pixmap = None
        super().clear()


class CollapsibleSection(QWidget):
    """A custom widget that provides a collapsible section with a header button."""
    def __init__(self, title, parent=None, expanded=True):
        super(CollapsibleSection, self).__init__(parent)
        self.expanded = expanded
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #1A1B26;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-weight: bold;
                font-size: 13px;
                color: #C0CAF5;
            }
            QPushButton:hover {
                background-color: #1F2335;
                color: #58A6FF;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle)
        self.main_layout.addWidget(self.toggle_button)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.addWidget(self.content_widget)
        
        # Styling for the content area to look like a group box
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)

        self.title = title
        self._update_button()
        self.content_widget.setVisible(self.expanded)

    def setContentLayout(self, layout):
        """Set the layout for the collapsible content."""
        # Instead of replacing the layout, add the provided layout
        # as a sub-layout to avoid unparented widget issues in PyQt6
        
        # Clear existing items if called multiple times (though shouldn't be)
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Not fully destroying sub-layouts recursively here, but covers simple cases
                pass
                
        self.content_layout.addLayout(layout)

    def toggle(self):
        self.expanded = not self.expanded
        self._update_button()
        self.content_widget.setVisible(self.expanded)

    def _update_button(self):
        arrow = "▼" if self.expanded else "▶"
        self.toggle_button.setText(f"  {arrow}  {self.title}")


class ImageSearchApp(QMainWindow):
    """Google Image Search application window.
    
    Provides a GUI for searching Google Images and downloading selected
    images for use with asset management. Uses threading to keep UI
    responsive during network operations.
    """
    
    def __init__(self, search_terms: str, default_save_path: str | Path, 
                 asset_name: str, csv_file: str | Path) -> None:
        """Initialize the ImageSearchApp.
        
        Args:
            search_terms: Initial search terms for the image search.
            default_save_path: Path where downloaded images will be saved.
            asset_name: Name of the asset being edited/managed.
            csv_file: Path to CSV file containing asset metadata.
        
        Raises:
            ValueError: If any of the inputs fail validation.
        """
        super().__init__()
        try:
            self.search_terms = validate_search_terms(search_terms)
            self.save_path = validate_path(default_save_path)
            self.asset_name = validate_asset_name(asset_name)
            self.csv_file = validate_csv_file(csv_file)
        except ValueError as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setText(f"Input validation error: {str(e)}")
            error_dialog.setWindowTitle("Validation Error")
            error_dialog.exec()
            raise
        
        self.setWindowTitle("Google Image Search")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search terms")
        self.search_input.setText(search_terms)
        self.layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_button)
        
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QGridLayout(self.scroll_area_widget)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        
        self.save_button = QPushButton("Save Selected Images To Asset")
        self.save_button.clicked.connect(lambda: self.save_images(default_save_path, asset_name, csv_file))
        self.layout.addWidget(self.save_button)
        
        self.selected_images = []
        self.selected_labels = []
        
        # Threading attributes
        self.search_worker = None
        self.download_worker = None
        self.save_worker = None
        
        self.perform_search()
    
    def perform_search(self) -> None:
        """Perform a Google Image Search with the current input terms.
        
        Validates search terms and starts the SearchWorker thread to
        asynchronously fetch search results. Shows loading indicator
        and disables search button during operation.
        """
        search_terms = self.search_input.text()
        
        try:
            sanitized_terms = validate_search_terms(search_terms)
        except ValueError as e:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Warning)
            error_dialog.setText(f"Invalid search terms: {str(e)}")
            error_dialog.setWindowTitle("Input Error")
            error_dialog.exec()
            return
        
        # Clear previous results
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Show loading message
        loading_label = QLabel("Searching...\nPlease wait.")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area_layout.addWidget(loading_label, 0, 0)
        
        # Disable search button during search
        self.search_button.setEnabled(False)
        
        # Perform Google Image Search in a worker thread
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": sanitized_terms,
            "cx": "53c963e4202294acb",  # Replace with your Custom Search Engine ID
            "key": "AIzaSyCBuuNSU7GCFcocwPP_LSl7FSwEiss1QrM",  # Replace with your API key
            "searchType": "image",
            "num": 10
        }
        
        # Cleanup old worker if it exists
        if self.search_worker is not None:
            self.search_worker.quit()
            self.search_worker.wait()
        
        self.search_worker = SearchWorker(search_url, params)
        self.search_worker.results_ready.connect(self.on_search_results)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    def on_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Handle search results from worker thread.
        
        Processes search results and initiates image downloads.
        Clears loading indicator and starts ImageDownloadWorker.
        
        Args:
            results: List of search results from Google Custom Search API.
        """
        # Clear loading message
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        if not results:
            no_results_label = QLabel("No images found. Try a different search.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_area_layout.addWidget(no_results_label, 0, 0)
            return
        
        # Extract image URLs and start downloading them
        image_urls = [result.get("link") for result in results if "link" in result]
        
        if self.download_worker is not None:
            self.download_worker.quit()
            self.download_worker.wait()
        
        self.download_worker = ImageDownloadWorker(image_urls)
        self.download_worker.image_ready.connect(self.on_image_downloaded)
        self.download_worker.download_error.connect(self.on_image_download_error)
        self.download_worker.start()
    
    def on_image_downloaded(self, index: int, pixmap: QPixmap, image_url: str) -> None:
        """Handle downloaded image from worker thread.
        
        Displays downloaded image in the scroll area with selection capability.
        
        Args:
            index: The index of the image in the results list.
            pixmap: The QPixmap object of the downloaded image.
            image_url: The URL of the downloaded image.
        """
        label = QLabel()
        label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
        label.setCursor(Qt.CursorShape.PointingHandCursor)
        label.mousePressEvent = lambda event, lbl=label, img_url=image_url: self.select_image(event, lbl, img_url)
        row = index // 5
        col = index % 5
        self.scroll_area_layout.addWidget(label, row, col)
    
    def on_image_download_error(self, index: int, error_message: str) -> None:
        """Handle image download error.
        
        Logs the error message without blocking UI operation.
        
        Args:
            index: The index of the image that failed to download.
            error_message: Description of the download error.
        """
        print(error_message)
    
    def on_search_error(self, error_message: str) -> None:
        """Handle search error from worker thread.
        
        Shows error dialog to the user with error details.
        
        Args:
            error_message: Description of the search error.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(error_message)
        error_dialog.setWindowTitle("Search Error")
        error_dialog.exec()
    
    def on_search_finished(self) -> None:
        """Handle search completion.
        
        Re-enables the search button to allow new searches.
        """
        self.search_button.setEnabled(True)
    
    def select_image(self, event: Any, label: QLabel, image_url: str) -> None:
        """Toggle image selection state.
        
        Marks images as selected/deselected by adding/removing red border.
        
        Args:
            event: The mouse event that triggered the selection.
            label: The QLabel widget representing the image.
            image_url: The URL of the image being selected.
        """
        if label in self.selected_labels:
            self.selected_labels.remove(label)
            self.selected_images.remove(image_url)
            label.setStyleSheet("")  # Remove red border from deselected image
        else:
            self.selected_labels.append(label)
            self.selected_images.append(image_url)
            label.setStyleSheet("border: 2px solid red;")  # Add red border to selected image
        print(f"Selected images: {self.selected_images}")
    
    def save_images(self, default_save_path: str | Path, asset_name: str, csv_file: str | Path) -> None:
        """Save selected images to disk and update CSV.
        
        Validates inputs and starts SaveImagesWorker to download and save
        selected images. Shows progress dialog during operation.
        
        Args:
            default_save_path: Path where images will be saved.
            asset_name: Name of the asset.
            csv_file: Path to CSV file to update with image folder path.
        """
        if not self.selected_images:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText("Please select at least one image before saving.")
            msg_box.setWindowTitle("No Selection")
            msg_box.exec()
            return
        
        try:
            images_folder = validate_path(default_save_path) / "Images"
            images_folder.mkdir(parents=True, exist_ok=True)
        except (ValueError, OSError) as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setText(f"Could not create images folder: {str(e)}")
            msg_box.setWindowTitle("Directory Error")
            msg_box.exec()
            return
        
        # Disable save button during operation
        self.save_button.setEnabled(False)
        
        # Show progress dialog
        self.progress_dialog = QMessageBox()
        self.progress_dialog.setIcon(QMessageBox.Icon.Information)
        self.progress_dialog.setText("Saving images...\nPlease wait.")
        self.progress_dialog.setWindowTitle("Saving Images")
        self.progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
        
        # Cleanup old worker if it exists
        if self.save_worker is not None:
            self.save_worker.quit()
            self.save_worker.wait()
        
        # Start save worker
        self.save_worker = SaveImagesWorker(self.selected_images, images_folder, asset_name)
        self.save_worker.progress.connect(self.on_save_progress)
        self.save_worker.error.connect(self.on_save_error)
        self.save_worker.finished.connect(lambda: self.on_save_finished(images_folder, asset_name, csv_file))
        self.save_worker.start()
    
    def on_save_progress(self, current: int, total: int) -> None:
        """Update save progress dialog.
        
        Updates the progress message during image save operation.
        
        Args:
            current: Number of images saved so far.
            total: Total number of images to save.
        """
        self.progress_dialog.setText(f"Saving images...\n{current}/{total}")
    
    def on_save_error(self, error_message: str) -> None:
        """Handle save error.
        
        Shows error dialog to inform user of save failures.
        
        Args:
            error_message: Description of the error that occurred.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText(error_message)
        error_dialog.setWindowTitle("Save Error")
        error_dialog.exec()
    
    def on_save_finished(self, images_folder: Path, asset_name: str, csv_file: str | Path) -> None:
        """Handle save completion.
        
        Updates CSV file with image folder path and shows success message.
        
        Args:
            images_folder: Path to the folder where images were saved.
            asset_name: Name of the asset.
            csv_file: Path to CSV file to update.
        """
        self.save_button.setEnabled(True)
        self.progress_dialog.close()
        
        # Update CSV to track image folder
        self.update_csv(asset_name, images_folder, csv_file)
        
        # Show success message
        success_dialog = QMessageBox()
        success_dialog.setIcon(QMessageBox.Icon.Information)
        success_dialog.setText(f"Images saved successfully to:\n{images_folder}")
        success_dialog.setWindowTitle("Save Complete")
        success_dialog.exec()
        
        self.close()  # Close the window after saving the images
    
    def update_csv(self, asset_name: str, images_folder: Path, csv_file: str | Path) -> None:
        """Update CSV file with image folder path.
        
        Reads CSV file, finds the matching asset record, updates its image path,
        and writes the file back. Includes retry logic for file locking issues.
        
        Args:
            asset_name: Name of the asset to update.
            images_folder: Path to the images folder to record.
            csv_file: Path to the CSV file to update.
        """
        while True:
            try:
                updated_rows = []
                csv_path = Path(csv_file)
                with csv_path.open('r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row["Asset Name"] == asset_name:
                            row["Asset Images Path"] = str(images_folder)
                        updated_rows.append(row)
                
                with csv_path.open('w', encoding='utf-8', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=updated_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(updated_rows)
                break
            except IOError:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setText("The file 'asset_paths.csv' is currently open. Please close it and try again.")
                msg_box.setWindowTitle("File Open Error")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                ret = msg_box.exec()
                if ret == QMessageBox.StandardButton.Cancel:
                    print("Save operation aborted.")
                    break


class AssetBrowser(QMainWindow):
    """Asset Browser window for managing imported assets.
    
    Provides functionality to browse, filter, and edit asset metadata
    and images. Integrates with CSV database for asset information storage.
    """
    
    def __init__(self) -> None:
        """Initialize the AssetBrowser window.
        
        Sets up the UI with filters, asset list, and detail panel.
        Loads assets from CSV file on startup.
        """
        super().__init__()
        self.setWindowTitle("Asset Browser")
        self.setGeometry(100, 100, 1000, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.addWidget(self.splitter)
        
        # --- Asset List Column (Left Pane) ---
        self.asset_list_container = QWidget()
        self.asset_list_container.setFixedWidth(350)
        self.asset_list_layout = QVBoxLayout(self.asset_list_container)
        self.asset_list_layout.setContentsMargins(5, 5, 5, 5)
        self.asset_list_layout.setSpacing(8)
        
        # 1. Unified Search & Filter Bar
        self.search_bar_layout = QHBoxLayout()
        self.search_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.asset_name_filter = QLineEdit()
        self.asset_name_filter.setPlaceholderText("Search Asset Name...")
        self.asset_name_filter.setClearButtonEnabled(True)
        self.asset_name_completer = QCompleter()
        self.asset_name_filter.setCompleter(self.asset_name_completer)
        self.asset_name_filter.textChanged.connect(self.apply_filters) # Live search integration
        
        self.filter_toggle_button = QToolButton()
        self.filter_toggle_button.setText("⚙️ Filters")
        self.filter_toggle_button.setCheckable(True)
        self.filter_toggle_button.setChecked(False)
        self.filter_toggle_button.clicked.connect(self.toggle_filters)
        
        self.search_bar_layout.addWidget(self.asset_name_filter)
        self.search_bar_layout.addWidget(self.filter_toggle_button)
        self.asset_list_layout.addLayout(self.search_bar_layout)
        
        # 2. Advanced Filters Dropdown Frame (Hidden initially)
        self.filter_form = QFormLayout()
        
        self.creator_filter = QComboBox()
        self.creator_filter.addItem("Unset")
        self.creator_filter.setEditable(True)
        self.filter_form.addRow("Creator:", self.creator_filter)
        
        self.asset_type_filter = QComboBox()
        self.asset_type_filter.addItem("Unset")
        self.asset_type_filter.setEditable(True)
        self.filter_form.addRow("Asset Type:", self.asset_type_filter)
        
        self.supported_filter = QComboBox()
        self.supported_filter.addItem("Unset")
        self.supported_filter.addItem("All")
        self.supported_filter.addItem("Supported")
        self.supported_filter.addItem("Unsupported")
        self.filter_form.addRow("Supported:", self.supported_filter)
        
        self.reset_filters_button = QPushButton("Reset Filters")
        self.reset_filters_button.clicked.connect(self.reset_filters)
        self.filter_form.addRow(self.reset_filters_button)
        
        self.filter_frame = QFrame()
        self.filter_frame.setLayout(self.filter_form)
        self.filter_frame.setStyleSheet("background-color: #1F2335; border-radius: 6px; border: 1px solid #292E42;")
        
        self.filter_scroll_area = QScrollArea()
        self.filter_scroll_area.setWidget(self.filter_frame)
        self.filter_scroll_area.setWidgetResizable(True)
        self.filter_scroll_area.setVisible(False)
        self.filter_scroll_area.setMaximumHeight(180)
        
        self.asset_list_layout.addWidget(self.filter_scroll_area)
        
        # 3. Sorting mode
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Alphabetical", "Grouped by Creator"])
        self.sort_combo.setCurrentIndex(1)  # Default to Grouped by Creator
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)
        self.asset_list_layout.addWidget(self.sort_combo)

        # 4. Actual List Widget
        self.asset_list = QListWidget()
        self.asset_list.setAlternatingRowColors(True)
        self.asset_list.setIconSize(QSize(24, 24))
        self.asset_list.currentItemChanged.connect(self.display_asset_details)
        self.asset_list_layout.addWidget(self.asset_list)
        
        self.splitter.addWidget(self.asset_list_container)
        
        self.details_panel = QVBoxLayout()
        self.details_widget = QWidget()
        self.details_widget.setLayout(self.details_panel)
        # self.splitter.addWidget(self.details_widget) # Add later wrapped in ScrollArea

        # --- Group 1: Image Preview ---
        self.image_group = CollapsibleSection("Image Preview")
        self.image_layout = QVBoxLayout()
        self.image_group.setContentLayout(self.image_layout)
        
        self.image_label = ResizableLabel()
        # self.image_label.setFixedSize(640, 480) # Removed fixed size
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; background-color: #1A1B26;") # Subtle elegant border
        # Ensure image label expands
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.on_image_context_menu)

        self.button_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.image_count_label = QLabel("")
        self.image_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_button.clicked.connect(self.show_previous_image)
        self.next_button.clicked.connect(self.show_next_image)
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.image_count_label)
        self.button_layout.addWidget(self.next_button)

        self.image_path_title = QLabel("Image Path: ")
        
        self.open_folder_button = QToolButton()
        self.open_folder_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.open_folder_button.setToolTip("Open Image Folder")
        self.open_folder_button.clicked.connect(self.open_image_folder)

        self.image_path_value = QLabel("")
        self.image_path_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.image_path_value.linkActivated.connect(self.open_link)
        
        self.image_path_layout = QHBoxLayout()
        self.image_path_layout.addWidget(self.image_path_title)
        self.image_path_layout.addWidget(self.open_folder_button)
        self.image_path_layout.addWidget(self.image_path_value)
        self.image_path_layout.addStretch()

        self.image_layout.addWidget(self.image_label)
        self.image_layout.addLayout(self.button_layout)
        
        # Thumbnail strip
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setViewMode(QListWidget.ViewMode.IconMode) # IconMode reliably kills the scrollbar bug
        self.thumbnail_list.setMovement(QListView.Movement.Static) # Prevents click-and-drag reordering
        self.thumbnail_list.setWrapping(False)
        self.thumbnail_list.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.thumbnail_list.setFixedHeight(75) 
        self.thumbnail_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # GridSize must be strictly taller than IconSize in IconMode to prevent downscaling the thumbnail
        self.thumbnail_list.setIconSize(QSize(50, 50))
        self.thumbnail_list.setGridSize(QSize(56, 70)) 
        self.thumbnail_list.setSpacing(2)
        
        self.thumbnail_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.thumbnail_list.customContextMenuRequested.connect(self.on_thumbnail_context_menu)
        self.thumbnail_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border: 1px solid transparent;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: rgba(88, 166, 255, 0.15);
                border: 1px solid rgba(88, 166, 255, 0.4);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.thumbnail_list.currentItemChanged.connect(self.on_thumbnail_selection_changed)
        self.image_layout.addWidget(self.thumbnail_list)

        self.image_layout.addLayout(self.image_path_layout)
        
        self.details_panel.addWidget(self.image_group)

        # --- Group 2: File Information ---
        self.file_info_group = CollapsibleSection("File Information", expanded=False)
        self.file_info_layout = QFormLayout()
        self.file_info_group.setContentLayout(self.file_info_layout)

        self.asset_directory_label = QLabel()
        self.asset_directory_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.asset_directory_label.linkActivated.connect(self.open_link)
        self.file_info_layout.addRow("Directory:", self.asset_directory_label)

        self.asset_path_label = QLabel()
        self.asset_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.file_info_layout.addRow("Path:", self.asset_path_label)

        self.details_panel.addWidget(self.file_info_group)

        # --- Group 3: Asset Metadata ---
        self.metadata_group = CollapsibleSection("Asset Metadata", expanded=False)
        self.metadata_layout = QFormLayout()
        self.metadata_group.setContentLayout(self.metadata_layout)

        self.asset_id_label = QLabel()
        self.asset_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("ID:", self.asset_id_label)

        self.asset_name_label = QLabel()
        self.asset_name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("Name:", self.asset_name_label)

        self.creator_label = QLabel()
        self.creator_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("Creator:", self.creator_label)

        self.asset_type_label = QLabel()
        self.asset_type_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("Type:", self.asset_type_label)
        
        self.supported_label = QLabel()
        self.supported_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("Supported:", self.supported_label)

        self.unsupported_label = QLabel()
        self.unsupported_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.metadata_layout.addRow("Unsupported:", self.unsupported_label)

        self.description_label = QLabel()
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.description_label.setWordWrap(True)
        self.metadata_layout.addRow("Description:", self.description_label)
        
        self.details_panel.addWidget(self.metadata_group)
        
        # --- Action Buttons ---
        self.actions_layout = QHBoxLayout()
        
        self.edit_images_button = QPushButton("Edit Asset Images")
        self.edit_images_button.clicked.connect(self.edit_asset)
        self.actions_layout.addWidget(self.edit_images_button)

        self.edit_metadata_button = QPushButton("Edit Metadata")
        self.edit_metadata_button.clicked.connect(self.edit_metadata)
        self.actions_layout.addWidget(self.edit_metadata_button)

        self.delete_asset_button = QPushButton("Delete Asset")
        self.delete_asset_button.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E53935;
                border: 1px solid #FFCDD2;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        self.delete_asset_button.clicked.connect(self.delete_asset)
        self.actions_layout.addWidget(self.delete_asset_button)
        
        self.details_panel.addLayout(self.actions_layout)

        # --- Group 4: Asset Files ---
        self.files_group = CollapsibleSection("Asset Files", expanded=False)
        self.files_layout = QVBoxLayout()
        self.files_group.setContentLayout(self.files_layout)
        
        self.file_model = QFileSystemModel()
        # Initialize to the current app directory instead of scanning drive root
        self.file_model.setRootPath(str(Path.cwd()))
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setAnimated(False)
        self.file_tree.setIndentation(20)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.on_file_context_menu)
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        
        self.files_layout.addWidget(self.file_tree)
        self.details_panel.addWidget(self.files_group)

        # Wrap details in scroll area to handle height
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidget(self.details_widget)
        self.details_scroll.setWidgetResizable(True)
        self.splitter.addWidget(self.details_scroll)

        self.load_assets()
        self.current_image_index = 0
        self.current_image_files: List[str] = []
        self.expected_image_dir: Optional[Path] = None
        self.thumbnail_loader = None
        self.stl_processes = []


    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for navigation."""
        # Ignore if focus is on an input field
        focused_widget = QApplication.focusWidget()
        if isinstance(focused_widget, (QLineEdit, QComboBox)):
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key.Key_Left:
            self.show_previous_image()
        elif event.key() == Qt.Key.Key_Right:
            self.show_next_image()
        elif event.key() == Qt.Key.Key_Up:
            # Navigate asset list if it doesn't have focus
            if not self.asset_list.hasFocus():
                current_row = self.asset_list.currentRow()
                if current_row > 0:
                    self.asset_list.setCurrentRow(current_row - 1)
        elif event.key() == Qt.Key.Key_Down:
            # Navigate asset list if it doesn't have focus
            if not self.asset_list.hasFocus():
                current_row = self.asset_list.currentRow()
                if current_row < self.asset_list.count() - 1:
                    self.asset_list.setCurrentRow(current_row + 1)
        else:
            super().keyPressEvent(event)
    
    def load_assets(self) -> None:
        """Load assets from CSV file and populate filters.
        
        Reads the asset_paths.csv file, extracts unique values for
        filters, and populates the asset list. Shows error dialog if
        the CSV file cannot be read or is invalid.
        """
        csv_path = Path('asset_paths.csv')
        with csv_path.open('r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.assets = list(reader)
            #print(self.assets)
            creators = sorted(list(set(asset["Creator"] for asset in self.assets)))
            self.creator_filter.addItems(creators)
            
            asset_types = sorted(list(set(asset["Asset Type"] for asset in self.assets)))
            self.asset_type_filter.addItems(asset_types)
            
            asset_names = sorted(list(set(asset["Asset Name"] for asset in self.assets)))
            #print(asset_names)
            model = QStandardItemModel()
            for name in asset_names:
                model.appendRow(QStandardItem(name))
            self.asset_name_completer.setModel(model)
            
            self.display_all_assets()
    
    def display_all_assets(self) -> None:
        """Display all assets in the asset list.
        
        Clears the current list and populates it with all assets
        sorted alphabetically by asset name.
        """
        self.asset_list.blockSignals(True)
        self.asset_list.clear()
        mode = self.sort_combo.currentText() if hasattr(self, 'sort_combo') else "Alphabetical"
        file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        if mode == "Grouped by Creator":
            groups: Dict[str, List[Dict[str, str]]] = {}
            for asset in self.assets:
                creator = asset.get("Creator", "") or ""
                groups.setdefault(creator, []).append(asset)

            for creator in sorted(groups.keys(), key=lambda s: s.lower()):
                header = QListWidgetItem(f"-- {creator} --")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                header.setBackground(QColor("#333"))
                header.setForeground(QColor("#aaa"))
                self.asset_list.addItem(header)
                for asset in sorted(groups[creator], key=lambda x: x["Asset Name"].lower()):
                    item = QListWidgetItem(file_icon, asset["Asset Name"])
                    item.setData(Qt.ItemDataRole.UserRole, asset["Asset ID"])  # Store the Asset ID in the item
                    self.asset_list.addItem(item)
        else:
            sorted_assets = sorted(self.assets, key=lambda x: x["Asset Name"].lower())
            for asset in sorted_assets:
                item = QListWidgetItem(file_icon, asset["Asset Name"])
                item.setData(Qt.ItemDataRole.UserRole, asset["Asset ID"])  # Store the Asset ID in the item
                self.asset_list.addItem(item)
        
        self.asset_list.blockSignals(False)
    
    def apply_filters(self) -> None:
        """Apply active filter selections to the asset list.
        
        Filters assets based on Creator, Asset Type, Asset Name, and
        Supported status. Updates the asset list to show only matching results.
        """
        self.asset_list.blockSignals(True)
        self.asset_list.clear()
        creator_filter = self.creator_filter.currentText().lower()
        asset_type_filter = self.asset_type_filter.currentText().lower()
        asset_name_filter = self.asset_name_filter.text().lower()
        supported_filter = self.supported_filter.currentText()
        
        filtered_assets = [
            asset for asset in self.assets
            if ((creator_filter == "unset" or creator_filter == asset["Creator"].lower()) and
                (asset_type_filter == "unset" or asset_type_filter == asset["Asset Type"].lower()) and
                asset_name_filter in asset["Asset Name"].lower() and
                (supported_filter == "Unset" or supported_filter == "All" or
                 (supported_filter == "Supported" and asset["Supported"] == "True") or
                 (supported_filter == "Unsupported" and asset["Unsupported"] == "True")))
        ]
        mode = self.sort_combo.currentText() if hasattr(self, 'sort_combo') else "Alphabetical"
        file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        if mode == "Grouped by Creator":
            groups: Dict[str, List[Dict[str, str]]] = {}
            for asset in filtered_assets:
                creator = asset.get("Creator", "") or ""
                groups.setdefault(creator, []).append(asset)

            for creator in sorted(groups.keys(), key=lambda s: s.lower()):
                header = QListWidgetItem(f"-- {creator} --")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                header.setBackground(QColor("#333"))
                header.setForeground(QColor("#aaa"))
                self.asset_list.addItem(header)
                for asset in sorted(groups[creator], key=lambda x: x["Asset Name"].lower()):
                    item = QListWidgetItem(file_icon, asset["Asset Name"])
                    item.setData(Qt.ItemDataRole.UserRole, asset["Asset ID"])  # Store the Asset ID in the item
                    self.asset_list.addItem(item)
        else:
            sorted_assets = sorted(filtered_assets, key=lambda x: x["Asset Name"].lower())
            for asset in sorted_assets:
                item = QListWidgetItem(file_icon, asset["Asset Name"])
                item.setData(Qt.ItemDataRole.UserRole, asset["Asset ID"])  # Store the Asset ID in the item
                self.asset_list.addItem(item)
        
        self.asset_list.blockSignals(False)
    
    def reset_filters(self):
        """Reset all filters to default values and refresh list."""
        self.creator_filter.setCurrentIndex(0)
        self.asset_type_filter.setCurrentIndex(0)
        self.asset_name_filter.clear()
        self.supported_filter.setCurrentIndex(0)
        self.apply_filters()
    
    def display_asset_details(self, item: Optional[QListWidgetItem]) -> None:
        """Display details of the selected asset.
        
        Shows asset information, displays images from the asset's image folder,
        and loads image navigation controls. Updates all detail labels and image display.
        
        Args:
            item: The QListWidgetItem that was selected (None if no selection).
        """
        if item is None:
            return
        
        asset_id = item.data(Qt.ItemDataRole.UserRole)  # Retrieve the Asset ID from the item
        asset = next(asset for asset in self.assets if asset["Asset ID"] == asset_id)
        
        asset_dir = asset['Asset Directory']
        self.asset_directory_label.setText(f"<a href='{QUrl.fromLocalFile(asset_dir).toString()}'>{asset_dir}</a>")
        self.asset_id_label.setText(f"{asset['Asset ID']}")
        asset_path = asset['Asset Path']
        self.asset_path_label.setText(f"{asset_path}")
        self.asset_name_label.setText(f"{asset['Asset Name']}")
        self.creator_label.setText(f"{asset['Creator']}")
        self.asset_type_label.setText(f"{asset['Asset Type']}")
        self.supported_label.setText(f"{asset['Supported']}")
        self.unsupported_label.setText(f"{asset['Unsupported']}")
        
        try:
            asset_images_path = None
            if asset.get("Asset Images Path"):
                asset_images_path = Path(asset["Asset Images Path"])
            
            # Load images from the asset directory recursively, pass expected path for verification
            self.load_images(Path(asset_dir), asset_images_path)

        except Exception as e:
            print(f"Error accessing path for asset {asset.get('Asset Name', 'Unknown')}: {e}")
            self.current_image_files = []
            self.show_image()

        # Update File Browser
        try:
             asset_directory = Path(asset["Asset Directory"])
             if asset_directory.exists():
                 root_path = str(asset_directory)
                 self.file_model.setRootPath(root_path)
                 self.file_tree.setRootIndex(self.file_model.index(root_path))
             else:
                 # If directory doesn't exist, show app directory
                 fallback = str(Path.cwd())
                 self.file_model.setRootPath(fallback)
                 self.file_tree.setRootIndex(self.file_model.index(fallback))
        except Exception as e:
             print(f"Error updating file browser: {e}")
             fallback = str(Path.cwd())
             self.file_model.setRootPath(fallback)
             self.file_tree.setRootIndex(self.file_model.index(fallback))
            
    def describe_image(self, image_paths: List[str]) -> str:
        """Describe image using Ollama API (placeholder).
        
        Generates descriptive tags for images using the Ollama API
        with the LLaVA model. Currently a placeholder implementation.
        
        Args:
            image_paths: List of file paths to images to describe.
        
        Returns:
            String containing image descriptions and tags.
        """
        # Implement your image description logic here
        # For example, you can use an image recognition API or a pre-trained model
        # Here, we'll just return a placeholder description
        if not image_paths:
            return ""
        descriptions = []
        # Placeholder logic for describing images
        for image_path in image_paths:
            path = image_path
            # Call the Ollama API to describe the image
            res = ollama.chat(
            model='llava',
            messages=[
                    {'role': 'user',
                    'content': 'List 5-10 relevant tags for this image. Include gender, race, object in hands, actions',
                    'images': [path]
                    }
                ]
            )
            descriptions.append(res['message']['content'])
        
        return "\n".join(descriptions)
            
    def show_image(self) -> None:
        """Display the current image and update navigation controls.
        
        Shows the image at the current index, updates the image count
        label, and shows/hides navigation buttons as appropriate.
        """
        if self.current_image_files:
            # Bounds checking
            if not (0 <= self.current_image_index < len(self.current_image_files)):
                self.current_image_index = 0
                
            image_file = Path(self.current_image_files[self.current_image_index])
            if image_file.exists():
                pixmap = QPixmap(str(image_file))
                # Pass full pixmap to ResizableLabel, it will handle scaling
                self.image_label.setPixmap(pixmap)
                
                # Update image path label
                path_str = str(image_file)
                # Ensure the link text is just the filename
                link_html = f"<a href='{QUrl.fromLocalFile(path_str).toString()}'>{image_file.name}</a>"
                
                # Check if image is external (not in expected directory)
                is_external = False
                if self.expected_image_dir:
                    try:
                        # Check if image_file is relative to expected_image_dir
                        # On Windows, path casing and slashes can be tricky. Resolve both.
                        img_path = image_file.resolve()
                        expected = self.expected_image_dir.resolve()
                        # print(f"Checking: {img_path} relative to {expected}")
                        img_path.relative_to(expected)
                    except ValueError:
                        is_external = True
                        # print(f"  -> External! (ValueError)")
                    except Exception as e:
                        print(f"Error checking external path: {e}")
                
                if is_external:
                    # Place (External) text OUTSIDE the link
                    self.image_path_value.setText(f"(External) {link_html}")
                    self.image_path_value.setStyleSheet("") 
                    self.image_path_value.setToolTip(f"This image is outside the standard images folder:\n{self.expected_image_dir}")
                else:
                    self.image_path_value.setText(link_html)
                    self.image_path_value.setStyleSheet("")
                    self.image_path_value.setToolTip(str(image_file))
                
                # Update thumbnail selection if item exists
                if self.thumbnail_list.count() > self.current_image_index:
                     item = self.thumbnail_list.item(self.current_image_index)
                     if item:
                         self.thumbnail_list.blockSignals(True)
                         self.thumbnail_list.setCurrentItem(item)
                         self.thumbnail_list.blockSignals(False)

            else:
                self.image_label.clear()
                self.image_label.setStyleSheet("border: 2px solid black;")  # Add border for outline
                self.image_path_value.setText("Not found")
            self.prev_button.setVisible(len(self.current_image_files) > 1)
            self.next_button.setVisible(len(self.current_image_files) > 1)
            self.image_count_label.setText(f"{self.current_image_index + 1} / {len(self.current_image_files)}")
        else:
            self.image_label.clear()
            self.image_label.setText("No images available")
            self.image_label.setStyleSheet("border: 2px solid black;")  # Add border for outline
            self.image_path_value.setText("None")
            self.prev_button.setVisible(False)
            self.next_button.setVisible(False)
            self.image_count_label.setText("")
    
    def load_images(self, asset_directory: Path, expected_image_dir: Optional[Path] = None) -> None:
        """Load images from the asset directory recursively into the viewer.
        
        Args:
            asset_directory: The root directory of the asset to scan.
            expected_image_dir: The standard directory where images are expected (for UI indication).
        """
        self.expected_image_dir = expected_image_dir
        self.current_image_files = []
        
        if asset_directory.exists():
            # Recursively find all supported images
            extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            for file_path in asset_directory.rglob('*'):
                 if file_path.is_file() and file_path.suffix.lower() in extensions:
                     self.current_image_files.append(str(file_path))
        
        # Sort for consistent order
        self.current_image_files.sort()
        self.current_image_index = 0
        self.show_image()
        
        # Start thumbnail loader
        self.thumbnail_list.clear()
        if self.thumbnail_loader and self.thumbnail_loader.isRunning():
            try:
                self.thumbnail_loader.thumbnail_loaded.disconnect(self.on_thumbnail_loaded)
            except Exception:
                pass # Signal might not be connected
            self.thumbnail_loader.stop()
            self.thumbnail_loader.wait()
            
        self.thumbnail_loader = ThumbnailLoaderWorker(self.current_image_files)
        self.thumbnail_loader.thumbnail_loaded.connect(self.on_thumbnail_loaded)
        self.thumbnail_loader.start()

    def on_thumbnail_loaded(self, index: int, path: str, icon: QIcon) -> None:
        """Handle loaded thumbnail."""
        # Verify that the loaded thumbnail belongs to the current image set
        if not self.current_image_files or index >= len(self.current_image_files):
            return
        
        # Verify path matches
        if self.current_image_files[index] != path:
            return

        item = QListWidgetItem(icon, "")
        item.setData(Qt.ItemDataRole.UserRole, index)
        self.thumbnail_list.addItem(item)
        if index == self.current_image_index:
            self.thumbnail_list.blockSignals(True)
            self.thumbnail_list.setCurrentItem(item)
            self.thumbnail_list.blockSignals(False)

    def on_thumbnail_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        """Handle thumbnail selection change."""
        if not current:
            return
            
        index = current.data(Qt.ItemDataRole.UserRole)
        # Only update if index actually changed to prevent loops
        if index != self.current_image_index:
            if 0 <= index < len(self.current_image_files):
                self.current_image_index = index
                self.show_image()

    def show_previous_image(self) -> None:
        """Navigate to the previous image in the asset's image list."""
        if self.current_image_files:
            self.current_image_index = (self.current_image_index - 1) % len(self.current_image_files)
            self.show_image()
    
    def show_next_image(self) -> None:
        """Navigate to the next image in the asset's image list."""
        if self.current_image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.current_image_files)
            self.show_image()
    
    def toggle_filters(self) -> None:
        """Toggle visibility of the filter panel."""
        if self.filter_toggle_button.isChecked():
            self.filter_toggle_button.setText("Hide Filters")
            self.filter_scroll_area.setVisible(True)
        else:
            self.filter_toggle_button.setText("Show Filters")
            self.filter_scroll_area.setVisible(False)
    
    def edit_asset(self) -> None:
        """Open ImageSearchApp for editing asset images.
        
        Extracts current asset information and opens a new window
        for downloading and saving images related to this asset.
        """
        asset_name = self.asset_name_label.text()
        creator = self.creator_label.text()
        search_terms = f"{asset_name} {creator}"
        # We need to extract the raw path from the HTML link or text
        # Since we set it as <a href='...'>path</a>, we can extract from text() if it's plain text,
        # but for directory it's a link.
        
        # However, it's safer to get it from self.assets list using the ID
        asset_id = self.asset_id_label.text()
        try:
            asset = next(a for a in self.assets if a["Asset ID"] == asset_id)
            asset_directory = asset["Asset Directory"]
        except StopIteration:
            print("Error: Could not find asset ID to edit")
            return

        print(f"edit_asset: asset directory: {asset_directory}")
        self.image_search_window = ImageSearchApp(search_terms, asset_directory, asset_name, 'asset_paths.csv')
        self.image_search_window.show()

    def backup_csv(self):
        """Create a timestamped backup of asset_paths.csv."""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"asset_paths_{timestamp}.csv"
            shutil.copy2("asset_paths.csv", backup_file)
            print(f"Backup created: {backup_file}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Failed to create backup: {e}")
            return False

    def edit_metadata(self):
        """Open dialog to edit asset metadata."""
        asset_id = self.asset_id_label.text()
        if not asset_id:
            return

        try:
            asset = next(a for a in self.assets if a["Asset ID"] == asset_id)
        except StopIteration:
            return

        dialog = EditAssetDialog(asset, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_asset = dialog.get_data()
            
            if not self.backup_csv():
                return

            # Update CSV
            try:
                # Update in memory list
                index = next(i for i, a in enumerate(self.assets) if a["Asset ID"] == asset_id)
                self.assets[index] = updated_asset
                
                # Write back to CSV
                fieldnames = list(self.assets[0].keys())
                with open('asset_paths.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.assets)
                
                # Refresh display
                self.display_asset_details(self.asset_list.currentItem())
                QMessageBox.information(self, "Success", "Asset metadata updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {e}")

    def delete_asset(self):
        """Delete the current asset from the CSV."""
        asset_id = self.asset_id_label.text()
        if not asset_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this asset from the database?\nThis will NOT delete files from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.backup_csv():
                return

            # Capture current row index before deletion
            current_row = self.asset_list.currentRow()

            try:
                # Remove from memory
                self.assets = [a for a in self.assets if a["Asset ID"] != asset_id]
                
                # Write back to CSV
                if self.assets:
                    fieldnames = list(self.assets[0].keys())
                    with open('asset_paths.csv', 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.assets)
                else:
                    # Handle empty CSV case if needed, or just write header
                    pass

                # Refresh list
                self.apply_filters()
                
                # Select previous item (or same index if available, or last if index out of bounds)
                if self.asset_list.count() > 0:
                    new_row = max(0, current_row - 1)
                    if new_row < self.asset_list.count():
                         self.asset_list.setCurrentRow(new_row)
                    else:
                         self.asset_list.setCurrentRow(self.asset_list.count() - 1)

                QMessageBox.information(self, "Success", "Asset deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete asset: {e}")

    def on_file_double_clicked(self, index):
        """Open file on double click."""
        file_path = self.file_model.filePath(index)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def on_file_context_menu(self, position):
        """Show context menu for file browser."""
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            return

        file_path = self.file_model.filePath(index)
        menu = QMenu()
        
        open_action = QAction("Open", self)
        menu.addAction(open_action)

        open_folder_action = QAction("Open Containing Folder", self)
        menu.addAction(open_folder_action)

        preview_action = None
        if file_path.lower().endswith(('.stl', '.obj', '.ply')):
            menu.addSeparator()
            preview_action = QAction("Generate Preview Image (3D Model)", self)
            menu.addAction(preview_action)

        # Process the result outside the menu's event loop to prevent modal deadlocks
        action = menu.exec(self.file_tree.viewport().mapToGlobal(position))
        
        if action == open_action:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        elif action == open_folder_action:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(file_path).parent)))
        elif preview_action and action == preview_action:
            QTimer.singleShot(10, lambda: self.open_stl_preview(file_path))

    def open_stl_preview(self, file_path):
        """Open the STL preview dialog."""
        # Find current asset to get expected images path
        asset_id = self.asset_id_label.text()
        images_path = None
        try:
            asset = next(a for a in self.assets if a["Asset ID"] == asset_id)
            if asset.get("Asset Images Path"):
                p = Path(asset["Asset Images Path"])
                # Create the directory if it doesn't exist
                if not p.exists():
                     try:
                         p.mkdir(parents=True, exist_ok=True)
                     except OSError as e:
                         print(f"Error creating images directory: {e}")
                
                if p.exists():
                    images_path = p
        except StopIteration:
            pass

        if not images_path:
            images_path = Path(file_path).parent

        import subprocess
        try:
            # Launch the external VTK viewer script rather than risking PyQt6 OpenGL deadlocks
            script_path = Path(__file__).parent / "display_stl.py"
            # Creating a wrapper script isn't needed, but we can launch it and check for immediate death
            log_file = open("stl_preview.log", "w")
            
            # sys.executable is returning a broken venv path on this machine, using 'py' launcher
            executable = "py" if os.name == "nt" else sys.executable
            
            process = subprocess.Popen(
                [executable, str(script_path), str(file_path), str(images_path)],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait up to 1 second to see if it crashed immediately due to imports
            try:
                # Can't use communicate if we redirected to a file, so we poll instead
                process.wait(timeout=0.5)
                if process.returncode != 0:
                    QMessageBox.critical(self, "STL Preview Error", f"Subprocess exited with code {process.returncode}. Check stl_preview.log for details.")
            except subprocess.TimeoutExpired:
                # Still running after a half second, assume it successfully launched the GUI!
                if not hasattr(self, 'stl_processes'):
                    self.stl_processes = []
                self.stl_processes.append(process)
                
                # Monitor process completion to refresh images
                timer = QTimer(self)
                timer.setInterval(1000)
                def check_process():
                    if process.poll() is not None:
                        timer.stop()
                        if hasattr(self, '_active_timers') and timer in self._active_timers:
                            self._active_timers.remove(timer)
                        # Refresh the current item's display to show new images
                        current_item = self.asset_list.currentItem()
                        if current_item:
                            self.display_asset_details(current_item)
                
                if not hasattr(self, '_active_timers'):
                    self._active_timers = []
                self._active_timers.append(timer)
                timer.timeout.connect(check_process)
                timer.start()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch STL previewer: {e}")

    def open_link(self, url):
        """Open the provided URL in the default application."""
        QDesktopServices.openUrl(QUrl(url))

    def open_image_folder(self):
        """Open the folder containing the current image."""
        if self.current_image_files and self.current_image_index < len(self.current_image_files):
            image_path = Path(self.current_image_files[self.current_image_index])
            folder_path = image_path.parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))

    def make_image_default(self, image_path: str):
        path = Path(image_path)
        dir_path = path.parent
        # Remove prefix from any existing default images
        for p in dir_path.glob("00_default_*"):
            if p.is_file():
                try:
                    new_name = p.name.replace("00_default_", "", 1)
                    p.rename(p.with_name(new_name))
                except Exception as e:
                    print(f"Error renaming {p}: {e}")
        
        # Rename the selected file
        if not path.name.startswith("00_default_"):
            new_path = path.with_name(f"00_default_{path.name}")
            try:
                path.rename(new_path)
                QMessageBox.information(self, "Success", "Image set as default.")
                # Refresh UI
                current_item = self.asset_list.currentItem()
                if current_item:
                    self.display_asset_details(current_item)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to set default image: {e}")

    def on_image_context_menu(self, position):
        if not hasattr(self, 'current_image_files') or not self.current_image_files:
            return
        if self.current_image_index >= len(self.current_image_files):
            return
            
        menu = QMenu()
        set_default_action = QAction("Set as Default Image", self)
        menu.addAction(set_default_action)
        action = menu.exec(self.image_label.mapToGlobal(position))
        
        if action == set_default_action:
            self.make_image_default(self.current_image_files[self.current_image_index])

    def on_thumbnail_context_menu(self, position):
        if not hasattr(self, 'current_image_files') or not self.current_image_files:
            return
            
        item = self.thumbnail_list.itemAt(position)
        if not item:
            return
            
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is None or index >= len(self.current_image_files):
            return
            
        menu = QMenu()
        set_default_action = QAction("Set as Default Image", self)
        menu.addAction(set_default_action)
        action = menu.exec(self.thumbnail_list.viewport().mapToGlobal(position))
        
        if action == set_default_action:
            self.make_image_default(self.current_image_files[index])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = AssetBrowser()
    window.show()
    sys.exit(app.exec())
