import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QScrollArea, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Image Search")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search terms")
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
        
        self.save_button = QPushButton("Save Selected Image")
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)
        
        self.selected_image = None
    
    def perform_search(self):
        search_terms = self.search_input.text()
        if not search_terms:
            return
        
        # Clear previous results
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Perform Google Image Search
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": search_terms,
            "cx": "53c963e4202294acb",  # Replace with your Custom Search Engine ID
            "key": "AIzaSyA5b5i68I1iYoMG8Z2lf9d4b6Nx8fqF1I8",  # Replace with your API key
            "searchType": "image",
            "num": 10
        }
        response = requests.get(search_url, params=params)
        results = response.json().get("items", [])
        
        # Display results in a 5x5 layout
        for index, result in enumerate(results):
            image_url = result["link"]
            image_data = requests.get(image_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            label = QLabel()
            label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
            label.mousePressEvent = lambda event, img_url=image_url: self.select_image(event, img_url)
            row = index // 5
            col = index % 5
            self.scroll_area_layout.addWidget(label, row, col)
    
    def select_image(self, event, image_url):
        self.selected_image = image_url
        print(f"Selected image: {image_url}")
    
    def save_image(self):
        if self.selected_image:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
            if file_path:
                image_data = requests.get(self.selected_image).content
                with open(file_path, 'wb') as file:
                    file.write(image_data)
                print(f"Image saved to {file_path}")
        else:
            print("No image selected")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSearchApp()
    window.show()
    sys.exit(app.exec_())
