# Imports Modules
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QLabel,
                             QListWidget, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox)
from PyQt5.QtCore import Qt
import os
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageFilter, ImageEnhance

# App Settings
app = QApplication([])
main_window = QWidget()
main_window.setWindowTitle("PhotoQT")
main_window.resize(900,700)

# All app widgets
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

# Dropdown box
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


# App Design
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

master_layout.addLayout(col1, 20)
master_layout.addLayout(col2, 80)

main_window.setLayout(master_layout)


# All App Functionality

working_directory = ""
# Filter files and extesions
def filter(files, extensions):
    results = []
    for file in files:
        for ext in extensions:
            if file.endswith(ext):
                results.append(file)
    return results

# Choose current work directory
def getWorkDirectory():
    global working_directory
    working_directory = QFileDialog.getExistingDirectory()
    extensions = ['.jpg', '.jpeg', '.png', '.svg']
    filenames = filter(os.listdir(working_directory), extensions)
    file_list.clear()
    for filename in filenames:
        file_list.addItem(filename)


class Editor():
    def __init__(self):
        self.image = None       
        self.original = None    
        self.filename = None
        self.save_folder = "edits/" 

    def load_image(self, filename):
        self.filename = filename
        fullname = os.path.join(working_directory, self.filename)
        # Load the image and keep a copy of the original
        self.original = Image.open(fullname)
        self.image = self.original.copy() 

    def save_image(self):
        path = os.path.join(working_directory, self.save_folder)
        if not(os.path.exists(path) or os.path.isdir(path)):
            os.mkdir(path)
        
        # Save the current state of self.image
        fullname = os.path.join(path, self.filename)
        self.image.save(fullname)
        print(f"Image saved to: {fullname}") 

    # Displays the current PIL image object in picture_box
    def show_image_in_box(self):
        if self.image is None:
            picture_box.setText("No image loaded.")
            picture_box.show()
            return

        # Convert PIL Image to QImage
        # Ensure image is in a format QImage can handle (e.g., RGB, RGBA)
        if self.image.mode == 'RGB':
            qimage = QImage(self.image.tobytes(), self.image.width, self.image.height, QImage.Format_RGB888)
        elif self.image.mode == 'RGBA':
            qimage = QImage(self.image.tobytes(), self.image.width, self.image.height, QImage.Format_RGBA8888)
        elif self.image.mode == 'L':
            qimage = QImage(self.image.tobytes(), self.image.width, self.image.height, QImage.Format_Grayscale8)
        else:
            # Convert to RGB if mode is not directly supported, for broader compatibility
            rgb_image = self.image.convert('RGB')
            qimage = QImage(rgb_image.tobytes(), rgb_image.width, rgb_image.height, QImage.Format_RGB888)

        # Convert QImage to QPixmap and scale for display
        pixmap = QPixmap.fromImage(qimage)
        w, h = picture_box.width(), picture_box.height()
        pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        picture_box.setPixmap(pixmap)
        picture_box.show()
    
    def gray_filter(self):
        if self.image is None: return
        self.image = self.image.convert("L")
        self.save_image() # For now, save immediately. Will change for undo/redo.
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
        # Enhance by 1.2 (20% increase)
        self.image = ImageEnhance.Color(self.image).enhance(1.2)
        self.save_image()
        self.show_image_in_box()

    def contrast(self):
        if self.image is None: return
        # Enhance by 1.2 (20% increase)
        self.image = ImageEnhance.Contrast(self.image).enhance(1.2)
        self.save_image()
        self.show_image_in_box()
    
    def apply_filter(self, filter_name):
        if self.image is None: return
        
        # When "Original" is selected, revert self.image to original copy
        if filter_name == "Original":
            if self.original:
                self.image = self.original.copy()
            else:
                return
        else:
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
                # Apply filter directly to self.image
                self.image = filter_function(self.image)
            else:
                print(f"Warning: Filter '{filter_name}' not found.")
                return # Don't proceed if filter is unknown

        self.save_image() 
        self.show_image_in_box()

def handle_filter():
    # Ensure an image is selected in the list before applying filter
    if file_list.currentRow() >= 0:
        select_filter = filter_box.currentText()
        main.apply_filter(select_filter)


def displayImage():
    if file_list.currentRow() >= 0:
        filename = file_list.currentItem().text()
        main.load_image(filename) 
        main.show_image_in_box()

# Instantiate the Editor class
main = Editor()


# Connect UI elements to functions/methods
btn_folder.clicked.connect(getWorkDirectory)
file_list.currentRowChanged.connect(displayImage)
filter_box.currentTextChanged.connect(handle_filter)

# Connect buttons to the Editor methods
gray.clicked.connect(main.gray_filter)
btn_left.clicked.connect(main.left)
btn_right.clicked.connect(main.right)
mirror.clicked.connect(main.mirror)
sharpness.clicked.connect(main.sharpen)
blur.clicked.connect(main.blur)
saturation.clicked.connect(main.color)
contrast.clicked.connect(main.contrast)


# Show/Run
main_window.show()
app.exec_()