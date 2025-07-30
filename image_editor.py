# image_editor.py
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer, QIODevice, Qt
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import shutil

class Editor:
    def __init__(self, ui_instance):
        self.ui = ui_instance
        self.image = None 
        self.original = None
        self.history = []
        self.history_index = -1
        self.current_filename = None
        self.current_filepath = None
        self.filters_with_parameters = ["Sharpen", "Color", "Contrast", "Blur"]

        # Ensure the edits directory exists upon initialization
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
            self.clear_history()
            return

        try:
            print("[Editor.load_image] Attempting to open image with PIL...")
            pil_image = Image.open(self.current_filepath).convert("RGBA")
            self.image = pil_image.copy() # Current image
            self.original = pil_image.copy() # Store a clean copy of the original
            self.clear_history() # Clear history for new image
            self.add_to_history(self.image) # Add initial state to history
            self.show_image_in_box()
            print("[Editor.load_image] Image loaded successfully and added to history.")
        except Exception as e:
            print(f"Error loading image '{self.current_filepath}': {e}")
            self.ui.picture_box.setText("Error loading image.")
            self.image = None
            self.original = None
            self.clear_history()

    def save_image(self):
        if self.image is None or self.current_filename is None:
            print("No image to save or filename not set.")
            return

        # Use the predefined edits_directory
        save_path = os.path.join(self.edits_directory, self.current_filename)
        try:
            # PIL save handles format based on extension
            self.image.save(save_path)
            print(f"Image saved to: {save_path}")
        except Exception as e:
            print(f"Error saving image to {save_path}: {e}")

    def add_to_history(self, image_state):
        # Remove future history states if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Add current state to history
        self.history.append(image_state.copy())
        self.history_index = len(self.history) - 1
        print("Image state added to history.")

    def clear_history(self):
        self.history = []
        self.history_index = -1
        print("Image history cleared.")

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.show_image_in_box()
            print("Undo successful.")
        
        else:
            print("Cannot undo further.")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.show_image_in_box()
            print("Redo successful.")
        else:
            print("Cannot redo further.")

    def show_image_in_box(self):
        if self.image is None:
            self.ui.picture_box.clear()
            self.ui.picture_box.setText("No image loaded.")
            return

        # Convert PIL Image to QPixmap
        byte_array = io.BytesIO()
        self.image.save(byte_array, format="PNG")
        byte_array.seek(0)
        
        qimage = QImage.fromData(byte_array.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        # Scale pixmap to fit QLabel dimensions while maintaining aspect ratio
        label_size = self.ui.picture_box.size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.ui.picture_box.setPixmap(scaled_pixmap)

    # --- Centralized apply_filter method with parameter support ---
    def apply_filter(self, filter_name, slider_value=50, is_slider_change=False):
        if self.original is None:
            print(f"Cannot apply filter '{filter_name}': No original image loaded.")
            self.ui.picture_box.setText("No image to filter. Load an image first.")
            return

        temp_image = self.original.copy() 

        # Handle 'Original' filter separately
        if filter_name == "Original":
            self.image = temp_image # Revert to original
            # Only add to history and save if it's not a temporary slider change
            if not is_slider_change:
                self.add_to_history(self.image)
                self.save_image()
            self.show_image_in_box()
            print("Reverted to original image.")
            return
        
        factor = slider_value / 50.0 # Maps 0-100 to 0.0-2.0
        radius = slider_value / 10.0 # Maps 0-100 to 0.0-10.0

        # Mapping for all filters, using parameters where applicable
        mapping = {
            "B/W" : lambda img: img.convert("L").convert("RGBA"),
            "Color" : lambda img, val: ImageEnhance.Color(img).enhance(val),
            "Contrast" : lambda img, val: ImageEnhance.Contrast(img).enhance(val),
            "Blur" : lambda img, val: img.filter(ImageFilter.GaussianBlur(val)), # Use GaussianBlur with radius
            "Sharpen" : lambda img, val: ImageEnhance.Sharpness(img).enhance(val),
            "Left" : lambda img: img.transpose(Image.ROTATE_90),
            "Right" : lambda img: img.transpose(Image.ROTATE_270),
            "Mirror" : lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)
        }

        filter_function = mapping.get(filter_name)
        if filter_function:
            # Apply filter. If it's a parameter filter, pass the calculated value.
            if filter_name in self.filters_with_parameters:
                if filter_name == "Blur":
                    temp_image = filter_function(temp_image, radius) # Blur uses radius
                else:
                    temp_image = filter_function(temp_image, factor) # Other enhance filters use factor
            else:
                temp_image = filter_function(temp_image) # Non-parameter filters

            self.image = temp_image # Update the current image
            self.show_image_in_box() # Always show the updated image

            # Only add to history and save if it's NOT just a slider being dragged
            if not is_slider_change:
                self.add_to_history(self.image)
                self.save_image()
                print(f"Applied filter: {filter_name} with value {slider_value}. (Saved and added to history)")
            else:
                print(f"Applied filter: {filter_name} with value {slider_value}. (Preview only)")

        else:
            print(f"Warning: Filter '{filter_name}' not found in mapping or no operation specified.")