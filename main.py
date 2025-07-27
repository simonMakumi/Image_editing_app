# Imports Modules
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QLabel, QListWidget,
                             QPushButton, QHBoxLayout, QVBoxLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import os
from PIL import Image, ImageFilter, ImageEnhance

# --- App Settings ---
app = QApplication([])
main_window = QWidget()
main_window.setWindowTitle("PhotoQT")
main_window.resize(900, 700)

# --- All app widgets ---
btn_folder = QPushButton("Folder")
file_list = QListWidget()

btn_left = QPushButton("Left")
btn_right = QPushButton("Right")
mirror = QPushButton("Mirror")
sharpness = QPushButton("Sharpen")
gray = QPushButton("B/W")
saturation = QPushButton("Color")
contrast = QPushButton("Contrast")
blur = QPushButton("Blur")

# Dropdown box for filters
filter_box = QComboBox()
filter_box.addItem("Original")
filter_box.addItem("Left")
filter_box.addItem("Right")
filter_box.addItem("Mirror")
filter_box.addItem("Sharpen")
filter_box.addItem("B/W")
filter_box.addItem("Color")
filter_box.addItem("Contrast")
filter_box.addItem("Blur")

picture_box = QLabel("Image will appear here")


# --- App Design (Layout) ---
master_layout = QHBoxLayout()

col1 = QVBoxLayout()
col2 = QVBoxLayout()

col1.addWidget(btn_folder)
col1.addWidget(file_list)
col1.addWidget(filter_box)
col1.addWidget(btn_left)
col1.addWidget(btn_right)
col1.addWidget(mirror)
col1.addWidget(sharpness)
col1.addWidget(gray)
col1.addWidget(saturation)
col1.addWidget(contrast)
col1.addWidget(blur)

col2.addWidget(picture_box) 
master_layout.addLayout(col1, 20) # Col1 takes 20% of width
master_layout.addLayout(col2, 80) # Col2 takes 80% of width

main_window.setLayout(master_layout)


# --- All App Functionality ---

working_directory = ""

# Helper function to filter files by extension
def filter_files_by_extensions(files, extensions):
    results = []
    for file in files:
        for ext in extensions:
            if file.lower().endswith(ext): 
                results.append(file)
    return results

# Function to choose current work directory
def getWorkDirectory():
    global working_directory
    selected_directory = QFileDialog.getExistingDirectory(main_window, "Select Image Directory")
    if selected_directory: # Ensure a directory was actually selected
        working_directory = selected_directory
        extensions = ['.jpg', '.jpeg', '.png', '.svg', '.bmp', '.tiff']

        try:
            filenames = filter_files_by_extensions(os.listdir(working_directory), extensions)
            file_list.clear() # Clear existing items in the list widget
            for filename in filenames:
                file_list.addItem(filename)
        except Exception as e:
            print(f"Error listing directory: {e}")
            file_list.clear()


class Editor():
    def __init__(self):
        self.image = None
        self.original = None
        self.filename = None
        self.save_folder = "edits/" 

    def load_image(self, filename):
        self.filename = filename
        fullname = os.path.join(working_directory, self.filename)
        try:
            self.original = Image.open(fullname)
            self.image = self.original.copy()
        except Exception as e:
            print(f"Error loading image {fullname}: {e}")
            self.image = None
            self.original = None
            picture_box.setText("Error loading image. Is it corrupted?")


    def save_image(self):
        if self.image is None or self.filename is None:
            print("No image to save.")
            return

        path = os.path.join(working_directory, self.save_folder)
        if not(os.path.exists(path) and os.path.isdir(path)):
            try:
                os.makedirs(path)
            except OSError as e:
                print(f"Error creating save directory {path}: {e}")
                return
        
        # Save the current state of self.image
        fullname = os.path.join(path, self.filename)
        try:
            self.image.save(fullname)
            print(f"Image saved to: {fullname}")
        except Exception as e:
            print(f"Error saving image to {fullname}: {e}")


    # Displays the current PIL image object in picture_box directly from memory
    def show_image_in_box(self):
        if self.image is None:
            picture_box.setText("No image loaded.")
            picture_box.show()
            return

        
        pil_image = self.image # Work with the current self.image

        if pil_image.mode == 'RGB':
            qimage_format = QImage.Format_RGB888
            bytes_per_line = pil_image.width * 3 # 3 bytes per pixel for RGB
        elif pil_image.mode == 'RGBA':
            qimage_format = QImage.Format_RGBA8888
            bytes_per_line = pil_image.width * 4 # 4 bytes per pixel for RGBA
        elif pil_image.mode == 'L': # Grayscale
            qimage_format = QImage.Format_Grayscale8
            bytes_per_line = pil_image.width * 1 # 1 byte per pixel for Grayscale
        else:
            pil_image = pil_image.convert('RGB')
            qimage_format = QImage.Format_RGB888
            bytes_per_line = pil_image.width * 3

        # Create QImage from PIL image data (pil_image.tobytes() gives raw pixel data)
        qimage = QImage(pil_image.tobytes(), 
                        pil_image.width, 
                        pil_image.height, 
                        bytes_per_line,
                        qimage_format)

        pixmap = QPixmap.fromImage(qimage)
        w, h = picture_box.width(), picture_box.height()
        pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        
        picture_box.setPixmap(pixmap)
        picture_box.show()


    # Each method now operates on 'self.image' and then calls 'show_image_in_box()'
    # For now, 'save_image()' is still called here; it will be optimized for undo/redo later.
    
    def gray_filter(self):
        if self.image is None: return
        self.image = self.image.convert("L")
        self.save_image() 
        self.show_image_in_box()

    def left(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.ROTATE_90)
        self.save_image()
        self.show_image_in_box()

    def right(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.ROTATE_270)
        self.save_image()
        self.show_image_in_box()

    def mirror(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.save_image()
        self.show_image_in_box()

    def sharpen(self):
        if self.image is None: return
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.save_image()
        self.show_image_in_box()

    def blur(self):
        if self.image is None: return
        self.image = self.image.filter(ImageFilter.BLUR)
        self.save_image()
        self.show_image_in_box()

    def color(self):
        if self.image is None: return
        # Enhance color saturation by 20%
        self.image = ImageEnhance.Color(self.image).enhance(1.2)
        self.save_image()
        self.show_image_in_box()

    def contrast(self):
        if self.image is None: return
        # Enhance contrast by 20%
        self.image = ImageEnhance.Contrast(self.image).enhance(1.2)
        self.save_image()
        self.show_image_in_box()
    
    # Method to apply filter from the dropdown
    def apply_filter(self, filter_name):
        if self.image is None: return
        
        # If "Original" is selected, revert self.image to a copy of the pristine original
        if filter_name == "Original":
            if self.original:
                self.image = self.original.copy()
            else:
                # If no original is loaded, do nothing
                print("No original image to revert to.")
                return 
        else:
            # Mapping of filter names from QComboBox to their respective PIL operations (lambdas)
            mapping = {
                "B/W" : lambda img: img.convert("L"),
                "Color" : lambda img: ImageEnhance.Color(img).enhance(1.2),
                "Contrast" : lambda img: ImageEnhance.Contrast(img).enhance(1.2),
                "Blur" : lambda img: img.filter(ImageFilter.BLUR),
                "Sharpen" : lambda img: img.filter(ImageFilter.SHARPEN),
                "Left" : lambda img: img.transpose(Image.ROTATE_90),
                "Right" : lambda img: img.transpose(Image.ROTATE_270),
                "Mirror" : lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)
            }

            filter_function = mapping.get(filter_name)
            if filter_function:
                self.image = filter_function(self.image)
            else:
                print(f"Warning: Filter '{filter_name}' not found in dropdown mapping.")
                return

        self.save_image()
        self.show_image_in_box()


# Function called when a filter is selected from the dropdown
def handle_filter():
    if file_list.currentRow() >= 0:
        select_filter = filter_box.currentText()
        main.apply_filter(select_filter)


# Function called when a new image file is selected in the file list
def displayImage():
    if file_list.currentRow() >= 0:
        filename = file_list.currentItem().text()
        main.load_image(filename) 
        main.show_image_in_box()


# Instantiate the Editor class to manage image operations
main = Editor()


# --- Connect UI elements to their respective functions/methods ---

btn_folder.clicked.connect(getWorkDirectory)

file_list.currentRowChanged.connect(displayImage)
filter_box.currentTextChanged.connect(handle_filter)

# Connect individual filter buttons to their respective Editor methods
gray.clicked.connect(main.gray_filter)
btn_left.clicked.connect(main.left)
btn_right.clicked.connect(main.right)
mirror.clicked.connect(main.mirror)
sharpness.clicked.connect(main.sharpen)
blur.clicked.connect(main.blur)
saturation.clicked.connect(main.color)
contrast.clicked.connect(main.contrast)

main_window.show()
app.exec_()