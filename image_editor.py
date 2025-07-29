from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageFilter, ImageEnhance
import os

class Editor:
    def __init__(self, ui_ref):
        self.ui = ui_ref
        self.image = None
        self.original = None
        self.filename = None
        self.save_folder = "edits/"
        self.history = []
        self.history_index = -1

    def load_image(self, filename):
        print(f"\n[Editor.load_image] Attempting to load: {filename}")
        self.filename = filename
        current_dir = self.ui.current_working_directory
        print(f"[Editor.load_image] Current working directory: '{current_dir}'")

        if not current_dir:
            print("[Editor.load_image] Error: No working directory selected in UI. Cannot load image.")
            return

        fullname = os.path.join(current_dir, self.filename)
        print(f"[Editor.load_image] Full image path: '{fullname}'")
        try:
            print("[Editor.load_image] Attempting to open image with PIL...")
            self.original = Image.open(fullname)
            self.image = self.original.copy()
            self.clear_history()
            self.add_to_history(self.image)
            print("[Editor.load_image] Image loaded successfully and added to history.")
        except Exception as e:
            print(f"[Editor.load_image] Error loading image '{fullname}': {e}")
            self.image = None
            self.original = None
            self.ui.picture_box.setText("Error loading image. Is it corrupted?")

    def clear_history(self):
        self.history = []
        self.history_index = -1

    def add_to_history(self, image_state):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        self.history.append(image_state.copy())
        self.history_index = len(self.history) - 1
        
        max_history_size = 20
        if len(self.history) > max_history_size:
            self.history.pop(0)
            self.history_index -= 1
        
        self.show_image_in_box()
        print("[Editor.add_to_history] Image state added to history, calling show_image_in_box.")

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.show_image_in_box()
        else:
            print("Cannot undo further.")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.show_image_in_box()
        else:
            print("Cannot redo further.")

    def save_image(self):
        if self.image is None or self.filename is None:
            print("No image to save.")
            return

        path = os.path.join(self.ui.current_working_directory, self.save_folder)
        if not(os.path.exists(path) and os.path.isdir(path)):
            try:
                os.makedirs(path)
            except OSError as e:
                print(f"Error creating save directory {path}: {e}")
                return
        
        fullname = os.path.join(path, self.filename)
        try:
            self.image.save(fullname)
            print(f"Image saved to: {fullname}")
        except Exception as e:
            print(f"Error saving image to {fullname}: {e}")

    def show_image_in_box(self):
        print(f"[Editor.show_image_in_box] Called. self.image is None? {self.image is None}")
        if self.image is None:
            self.ui.picture_box.setText("No image loaded.")
            self.ui.picture_box.show()
            print("[Editor.show_image_in_box] No image available to display.")
            return

        # Check QLabel dimensions at this point
        current_label_width = self.ui.picture_box.width()
        current_label_height = self.ui.picture_box.height()
        print(f"[Editor.show_image_in_box] QLabel dimensions (W, H): ({current_label_width}, {current_label_height})")
        
        pil_image = self.image

        if pil_image.mode == 'RGB':
            qimage_format = QImage.Format_RGB888
            bytes_per_line = pil_image.width * 3
        elif pil_image.mode == 'RGBA':
            qimage_format = QImage.Format_RGBA8888
            bytes_per_line = pil_image.width * 4
        elif pil_image.mode == 'L':
            qimage_format = QImage.Format_Grayscale8
            bytes_per_line = pil_image.width * 1
        else:
            pil_image = pil_image.convert('RGB')
            qimage_format = QImage.Format_RGB888
            bytes_per_line = pil_image.width * 3

        qimage = QImage(pil_image.tobytes(), 
                        pil_image.width, 
                        pil_image.height, 
                        bytes_per_line, 
                        qimage_format)

        pixmap = QPixmap.fromImage(qimage)
        
        # This is the line that should be REMOVED (or commented out)
        # pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
        
        self.ui.picture_box.setPixmap(pixmap)
        self.ui.picture_box.show()
        print("[Editor.show_image_in_box] Image pixmap set successfully.")
    
    def gray_filter(self):
        if self.image is None: return
        self.image = self.image.convert("L")
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def left(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.ROTATE_90)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def right(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.ROTATE_270)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def mirror(self):
        if self.image is None: return
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def sharpen(self):
        if self.image is None: return
        self.image = self.image.filter(ImageFilter.SHARPEN)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def blur(self):
        if self.image is None: return
        self.image = self.image.filter(ImageFilter.BLUR)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def color(self):
        if self.image is None: return
        self.image = ImageEnhance.Color(self.image).enhance(1.2)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()

    def contrast(self):
        if self.image is None: return
        self.image = ImageEnhance.Contrast(self.image).enhance(1.2)
        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()
    
    def apply_filter(self, filter_name):
        if self.image is None: return
        
        if filter_name == "Original":
            if self.original:
                self.image = self.original.copy()
            else:
                print("No original image to revert to.")
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
                self.image = filter_function(self.image)
            else:
                print(f"Warning: Filter '{filter_name}' not found.")
                return

        self.save_image()
        self.add_to_history(self.image)
        self.show_image_in_box()