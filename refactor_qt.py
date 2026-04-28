import os

file_path = "metadata_browser.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace imports
content = content.replace("from PyQt5.", "from PyQt6.")
content = content.replace("from PyQt5 import", "from PyQt6 import")

# Enums
# Alignment
content = content.replace("Qt.AlignCenter", "Qt.AlignmentFlag.AlignCenter")

# Aspect Ratio
content = content.replace("Qt.KeepAspectRatio", "Qt.AspectRatioMode.KeepAspectRatio")

# Transformation Mode
content = content.replace("Qt.SmoothTransformation", "Qt.TransformationMode.SmoothTransformation")

# Orientation
content = content.replace("Qt.Horizontal", "Qt.Orientation.Horizontal")
content = content.replace("QListWidget.LeftToRight", "QListWidget.Flow.LeftToRight")

# Cursor Shape
content = content.replace("Qt.PointingHandCursor", "Qt.CursorShape.PointingHandCursor")

# Interaction Flags
content = content.replace("Qt.TextSelectableByMouse", "Qt.TextInteractionFlag.TextSelectableByMouse")
content = content.replace("Qt.LinksAccessibleByMouse", "Qt.TextInteractionFlag.LinksAccessibleByMouse")
content = content.replace("Qt.NoItemFlags", "Qt.ItemFlag.NoItemFlags")

# Context Menu Policy
content = content.replace("Qt.CustomContextMenu", "Qt.ContextMenuPolicy.CustomContextMenu")

# Key
content = content.replace("Qt.Key_Left", "Qt.Key.Key_Left")
content = content.replace("Qt.Key_Right", "Qt.Key.Key_Right")
content = content.replace("Qt.Key_Up", "Qt.Key.Key_Up")
content = content.replace("Qt.Key_Down", "Qt.Key.Key_Down")

# Roles
content = content.replace("Qt.UserRole", "Qt.ItemDataRole.UserRole")

# QMessageBox
content = content.replace("QMessageBox.Critical", "QMessageBox.Icon.Critical")
content = content.replace("QMessageBox.Warning", "QMessageBox.Icon.Warning")
content = content.replace("QMessageBox.Information", "QMessageBox.Icon.Information")

content = content.replace("QMessageBox.Ok", "QMessageBox.StandardButton.Ok")
content = content.replace("QMessageBox.Cancel", "QMessageBox.StandardButton.Cancel")
content = content.replace("QMessageBox.NoButton", "QMessageBox.StandardButton.NoButton")
content = content.replace("QMessageBox.Yes", "QMessageBox.StandardButton.Yes")
content = content.replace("QMessageBox.No", "QMessageBox.StandardButton.No")

# QDialog
content = content.replace("QDialog.Accepted", "QDialog.DialogCode.Accepted")
content = content.replace("QDialogButtonBox.Save", "QDialogButtonBox.StandardButton.Save")
content = content.replace("QDialogButtonBox.Cancel", "QDialogButtonBox.StandardButton.Cancel")

# QStyle
content = content.replace("QStyle.SP_DirIcon", "QStyle.StandardPixmap.SP_DirIcon")
content = content.replace("QStyle.SP_FileIcon", "QStyle.StandardPixmap.SP_FileIcon")

# QAbstractItemView
content = content.replace("QAbstractItemView.ScrollPerPixel", "QAbstractItemView.ScrollMode.ScrollPerPixel")

# Methods
content = content.replace(".exec_()", ".exec()")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored metadata_browser.py to use PyQt6.")
