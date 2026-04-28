# Asset Scanner

A tool for scanning and managing assets, specifically designed for 3D model libraries.

## Features
- Scan directories for assets (supported/unsupported folders).
- Manage asset metadata in a CSV database.
- Browse assets with a PyQt6-based GUI.
- Search for asset images using Google Image Search.
- Preview 3D models (STL) and generate thumbnails.
- Organize images and rename directories for better clarity.

## Project Structure
- `metadata_browser.py`: Main GUI application for browsing and managing assets.
- `Asset_Scanner.py`: Core logic for scanning directories and generating CSV data.
- `display_stl.py`: 3D model viewer and thumbnail generator.
- `google_image_search.py`: Tool to find images for assets.
- `rename_directories.py`: Utility to clean up directory names.
- `move_images.py`: Utility to organize images into subfolders.

## Requirements
- Python 3.x
- PyQt6
- PyVista (for 3D preview)
- Requests
- Pillow (PIL)

## Installation
```bash
pip install -r requirements.txt
```
*(Note: Ensure you have your Google API keys configured in the source if using image search.)*
