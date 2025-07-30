# image_editor.py
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer, QIODevice, Qt
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import shutil # Import shutil for directory operations

class Editor:
    def __init__(self, ui_instance):
        self.ui = ui_instance
        self.image = None       # The currently displayed image (potentially modified, can be a preview)
        self.original = None    # The original image loaded from file (clean base)
        self.last_finalized_image = None # NEW: The last image state that was added to history (base for chaining)
        self.history = []
        self.history_index = -1
        self.current_filename = None # To keep track of the currently loaded file
        self.current_filepath = None
        self.filters_with_parameters = ["Sharpen", "Color", "Contrast", "Blur"] 

        self._ensure_edits_directory_exists()

    def _ensure_edits_directory_exists(self):
        base_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.edits_directory = os.path.join(base_dir, "edits")

        if not os.path.exists(self.edits_directory):
            os.makedirs(self.edits_directory)
            print(f"Created edits directory: {self.edits_directory}")

    def load_image(self, filename):
        self.current_filename = filename
        self.current_filepath = os.path.join(self.ui.current_working_directory, filename)
        
        print(f"[Editor.load_image] Attempting to load: {filename}")
        print(f"[Editor.load_image] Current working directory: '{self.ui.current_working_directory}'")
        print(f"[Editor.load_image] Full image path: '{self.current_filepath}'")

        if not os.path.exists(self.current_filepath):
            print(f"Error: File not found at {self.current_filepath}")
            self.ui.picture_box.setText("Image not found!")
            self.image = None
            self.original = None
            self.last_finalized_image = None # Reset on error
            self.clear_history()
            return

        try:
            print("[Editor.load_image] Attempting to open image with PIL...")
            pil_image = Image.open(self.current_filepath).convert("RGBA")
            self.image = pil_image.copy()
            self.original = pil_image.copy() 
            self.last_finalized_image = pil_image.copy() # NEW: Set initial finalized image
            self.clear_history() 
            self.add_to_history(self.image) # Add initial state to history
            self.show_image_in_box()
            print("[Editor.load_image] Image loaded successfully and added to history.")
        except Exception as e:
            print(f"Error loading image '{self.current_filepath}': {e}")
            self.ui.picture_box.setText("Error loading image.")
            self.image = None
            self.original = None
            self.last_finalized_image = None # Reset on error
            self.clear_history()

    def save_image(self):
        if self.image is None or self.current_filename is None:
            print("No image to save or filename not set.")
            return

        save_path = os.path.join(self.edits_directory, self.current_filename)
        
        file_extension = os.path.splitext(self.current_filename)[1].lower()

        try:
            if file_extension in ['.jpg', '.jpeg']:
                rgb_image = Image.new("RGB", self.image.size, (255, 255, 255))
                rgb_image.paste(self.image, mask=self.image.split()[3] if self.image.mode == 'RGBA' else None)
                rgb_image.save(save_path)
                print(f"Image saved to: {save_path} (converted to RGB)")
            else:
                self.image.save(save_path)
                print(f"Image saved to: {save_path}")
        except Exception as e:
            print(f"Error saving image to {save_path}: {e}")
    def add_to_history(self, image_state):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(image_state.copy())
        self.history_index = len(self.history) - 1
        self.last_finalized_image = image_state.copy()
        print("Image state added to history.")

    def clear_history(self):
        self.history = []
        self.history_index = -1
        print("Image history cleared.")

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.last_finalized_image = self.image.copy()
            self.show_image_in_box()
            print("Undo successful.")
        else:
            print("Cannot undo further.")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.last_finalized_image = self.image.copy()
            self.show_image_in_box()
            print("Redo successful.")
        else:
            print("Cannot redo further.")

    def show_image_in_box(self):
        if self.image is None:
            self.ui.picture_box.clear()
            self.ui.picture_box.setText("No image loaded.")
            return

        byte_array = io.BytesIO()
        self.image.save(byte_array, format="PNG") 
        byte_array.seek(0)
        
        qimage = QImage.fromData(byte_array.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        label_size = self.ui.picture_box.size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.ui.picture_box.setPixmap(scaled_pixmap)

    def apply_filter(self, filter_name, slider_value=50, is_slider_change=False):
        if self.original is None or self.last_finalized_image is None: 
            print(f"Cannot apply filter '{filter_name}': No base image loaded or finalized state available.")
            self.ui.picture_box.setText("Load an image first.")
            return

        temp_image = self.last_finalized_image.copy() 

        # Handle 'Original' filter separately to reset everything
        if filter_name == "Original":
            self.image = self.original.copy()
            if not is_slider_change:
                self.add_to_history(self.image)
                self.save_image()
            self.show_image_in_box()
            print("Reverted to original image.")
            return

        factor = slider_value / 50.0 
        radius = slider_value / 10.0 

        mapping = {
            "B/W" : lambda img: img.convert("L").convert("RGBA"),
            "Color" : lambda img, val: ImageEnhance.Color(img).enhance(val),
            "Contrast" : lambda img, val: ImageEnhance.Contrast(img).enhance(val),
            "Blur" : lambda img, val: img.filter(ImageFilter.GaussianBlur(val)), 
            "Sharpen" : lambda img, val: ImageEnhance.Sharpness(img).enhance(val),
            "Left" : lambda img: img.transpose(Image.ROTATE_90),
            "Right" : lambda img: img.transpose(Image.ROTATE_270),
            "Mirror" : lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)
        }

        filter_function = mapping.get(filter_name)
        if filter_function:
            if filter_name in self.filters_with_parameters:
                if filter_name == "Blur":
                    temp_image = filter_function(temp_image, radius) 
                else:
                    temp_image = filter_function(temp_image, factor) 
            else:
                temp_image = filter_function(temp_image) 

            self.image = temp_image 
            self.show_image_in_box() 

            if not is_slider_change:
                self.add_to_history(self.image)
                self.save_image()
                print(f"Applied filter: {filter_name} with value {slider_value}. (Saved and added to history)")
            else:
                print(f"Applied filter: {filter_name} with value {slider_value}. (Preview only)")

        else:
            print(f"Warning: Filter '{filter_name}' not found in mapping or no operation specified.")