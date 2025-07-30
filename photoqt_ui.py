# photoqt_ui.py
from PyQt5.QtWidgets import (QWidget, QFileDialog, QLabel, QListWidget, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QComboBox, QSizePolicy, QApplication, QSlider)
from PyQt5.QtCore import Qt
import os
import themes

class PhotoQTUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoQT")
        self.setFixedSize(900, 700) 

        self.current_working_directory = "" 

        self._init_widgets()
        self._init_layout()

    def _init_widgets(self):
        self.btn_folder = QPushButton("Folder")
        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(150) 

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

        self.btn_save_as = QPushButton("Save As...") 

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Original", "Left", "Right", "Mirror", "Sharpen", "B/W", "Color", "Contrast", "Blur"])
        self.filter_box.setCurrentText("Original")
        
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Dark Theme", "Light Theme"])
        
        self.picture_box = QLabel("Image will appear here")
        self.picture_box.setObjectName("picture_box")
        self.picture_box.setAlignment(Qt.AlignCenter)
        self.picture_box.setScaledContents(True)
        self.picture_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.filter_param_label = QLabel("Filter Intensity:")
        self.filter_param_label.setAlignment(Qt.AlignCenter)
        self.filter_param_slider = QSlider(Qt.Horizontal)
        self.filter_param_slider.setRange(0, 100)
        self.filter_param_slider.setValue(50) 
        self.filter_param_slider.setTickPosition(QSlider.TicksBelow)
        self.filter_param_slider.setTickInterval(10)
        
        self.filter_param_label.setVisible(False)
        self.filter_param_slider.setVisible(False)


    def _init_layout(self):
        master_layout = QHBoxLayout(self)

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()

        col1.addWidget(self.btn_folder)
        col1.addWidget(self.file_list)
        col1.addWidget(self.filter_box)
        
        col1.addWidget(self.filter_param_label)
        col1.addWidget(self.filter_param_slider)

        col1.addWidget(self.theme_box) 
        col1.addWidget(self.btn_save_as) 

        col1.addWidget(self.btn_undo)
        col1.addWidget(self.btn_redo)
        col2.addWidget(self.picture_box)

        master_layout.addLayout(col1, 20)
        master_layout.addLayout(col2, 80)

    def apply_theme(self, theme_name):
        app = QApplication.instance() 
        if app:
            if theme_name == "Dark Theme":
                app.setStyleSheet(themes.DARK_THEME_QSS)
            elif theme_name == "Light Theme":
                app.setStyleSheet(themes.LIGHT_THEME_QSS)
            else:
                app.setStyleSheet("")
        else:
            print("Error: QApplication instance not found to apply theme.")

    def _filter_files_by_extensions(self, files, extensions):
        return [f for f in files if any(f.lower().endswith(ext) for ext in extensions)]

    def select_directory(self):
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
        current_item = self.file_list.currentItem()
        return current_item.text() if current_item else None

    def get_selected_filter_name(self):
        return self.filter_box.currentText()

    # Helper method for main_app to get selected theme
    def get_selected_theme_name(self):
        return self.theme_box.currentText()