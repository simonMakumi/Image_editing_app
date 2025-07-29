from PyQt5.QtWidgets import QWidget, QFileDialog, QLabel, QListWidget, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt
import os

class PhotoQTUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoQT")
        self.resize(900, 700)

        # Stores the currently selected folder path
        self.current_working_directory = "" 

        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        self.btn_folder = QPushButton("Folder")
        self.file_list = QListWidget()

        self.btn_left = QPushButton("Left")
        self.btn_right = QPushButton("Right")
        self.mirror = QPushButton("Mirror")
        self.sharpness = QPushButton("Sharpen")
        self.gray = QPushButton("B/W")
        self.saturation = QPushButton("Color")
        self.contrast = QPushButton("Contrast")
        self.blur = QPushButton("Blur")

        self.btn_undo = QPushButton("Undo")
        self.btn_redo = QPushButton("Redo")

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Original", "Left", "Right", "Mirror", "Sharpen", "B/W", "Color", "Contrast", "Blur"])

        self.picture_box = QLabel("Image will appear here")
        self.picture_box.setAlignment(Qt.AlignCenter) # Center text and image within the label

    def _init_layout(self):
        master_layout = QHBoxLayout(self)

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()

        col1.addWidget(self.btn_folder)
        col1.addWidget(self.file_list)
        col1.addWidget(self.filter_box)

        col1.addWidget(self.btn_undo)
        col1.addWidget(self.btn_redo)

        col1.addWidget(self.btn_left)
        col1.addWidget(self.btn_right)
        col1.addWidget(self.mirror)
        col1.addWidget(self.sharpness)
        col1.addWidget(self.gray)
        col1.addWidget(self.saturation)
        col1.addWidget(self.contrast)
        col1.addWidget(self.blur)

        col2.addWidget(self.picture_box)

        master_layout.addLayout(col1, 20)
        master_layout.addLayout(col2, 80)

    def _filter_files_by_extensions(self, files, extensions):
        return [f for f in files if any(f.lower().endswith(ext) for ext in extensions)]

    def select_directory(self):
        """
        Opens a directory selection dialog, updates the internal current_working_directory,
        and populates the file_list widget.
        Returns True if a directory was selected and processed, False otherwise.
        """
        selected_directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if selected_directory:
            self.current_working_directory = selected_directory
            extensions = ['.jpg', '.jpeg', '.png', '.svg', '.bmp', '.tiff']
            try:
                filenames = self._filter_files_by_extensions(os.listdir(self.current_working_directory), extensions)
                self.file_list.clear()
                for filename in filenames:
                    self.file_list.addItem(filename)
                return True
            except Exception as e:
                print(f"Error listing directory: {e}")
                self.file_list.clear()
                return False
        return False

    def get_selected_filename(self):
        """Returns the text of the currently selected item in the file list."""
        current_item = self.file_list.currentItem()
        return current_item.text() if current_item else None

    def get_selected_filter_name(self):
        """Returns the currently selected text from the filter dropdown box."""
        return self.filter_box.currentText()