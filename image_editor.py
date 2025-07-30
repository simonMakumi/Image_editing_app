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
        self.image = None
        self.original = None # Store the original loaded image
        self.history = []
        self.history_index = -1
        self.current_filename = None # To keep track of the currently loaded file
        self.current_filepath = None

        self._ensure_edits_directory_exists()

    def _ensure_edits_directory_exists(self):
        # Create an 'edits' subfolder if it doesn't exist
        # This will be relative to where main_app.py is run from
        # Or, we can make it relative to the loaded image directory
        # For now, let's keep it simple relative to script execution location
        # or we'll define a dedicated save path later.
        
        # A more robust way: create it within the current working directory of the UI
        # This requires the UI's directory to be set.
        if self.ui.current_working_directory:
            edit_dir = os.path.join(self.ui.current_working_directory, "edits")
            if not os.path.exists(edit_dir):
                os.makedirs(edit_dir)
                print(f"Created edits directory: {edit_dir}")

    def load_image(self, filename):
        self.current_filename = filename
        self.current_filepath = os.path.join(self.ui.current_working_directory, filename)
        
        print(f"[Editor.load_image] Attempting to load: {filename}")
        print(f"[Editor.load_image] Current working directory: '{self.ui.current_working_directory}'")
        print(f"[Editor.load_image] Full image path: '{self.current_filepath}'")

        if not os.path.exists(self.current_filepath):
            print(f"Error: File not found at {self.current_filepath}")
            self.ui.picture_box.setText("Image not found!")
            return

        try:
            print("[Editor.load_image] Attempting to open image with PIL...")
            pil_image = Image.open(self.current_filepath).convert("RGBA") # Ensure RGBA for consistency
            self.image = pil_image
            self.original = pil_image.copy() # Store a clean copy of the original
            self.clear_history() # Clear history for new image
            self.add_to_history(self.image)
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

        if self.ui.current_working_directory:
            edit_dir = os.path.join(self.ui.current_working_directory, "edits")
            if not os.path.exists(edit_dir):
                os.makedirs(edit_dir) # Ensure directory exists just before saving

            save_path = os.path.join(edit_dir, self.current_filename)
            try:
                # PIL save handles format based on extension
                self.image.save(save_path)
                print(f"Image saved to: {save_path}")
            except Exception as e:
                print(f"Error saving image to {save_path}: {e}")
        else:
            print("Cannot save: No current working directory selected.")

    def add_to_history(self, image_state):
        # Remove future history states if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Add current state to history
        self.history.append(image_state.copy())
        self.history_index = len(self.history) - 1
        print("Image state added to history, calling show_image_in_box.")
        # self.show_image_in_box() # Removed this as it can lead to double rendering from load_image

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

        print(f"[Editor.show_image_in_box] Called. self.image is None? {self.image is None}")

        # Convert PIL Image to QPixmap
        byte_array = io.BytesIO()
        self.image.save(byte_array, format="PNG") # Use PNG for lossless conversion
        byte_array.seek(0)
        
        qimage = QImage.fromData(byte_array.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        # Scale pixmap to fit QLabel dimensions while maintaining aspect ratio
        label_size = self.ui.picture_box.size()
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.ui.picture_box.setPixmap(scaled_pixmap)
        print(f"[Editor.show_image_in_box] QLabel dimensions (W, H): ({label_size.width()}, {label_size.height()})")
        print("[Editor.show_image_in_box] Image pixmap set successfully.")

    # --- Individual Filter Methods (NO self.save_image() here anymore) ---

    def left(self):
        if self.image:
            self.image = self.image.transpose(Image.ROTATE_90)
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Left") # This will trigger apply_filter which will save

    def right(self):
        if self.image:
            self.image = self.image.transpose(Image.ROTATE_270)
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Right") # This will trigger apply_filter which will save

    def mirror(self):
        if self.image:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Mirror") # This will trigger apply_filter which will save

    def sharpen(self):
        if self.image:
            self.image = ImageEnhance.Sharpness(self.image).enhance(2.0) # Example enhance factor
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Sharpen") # This will trigger apply_filter which will save

    def gray_filter(self):
        if self.image:
            self.image = self.image.convert("L").convert("RGBA") # Convert back to RGBA for consistency
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("B/W") # This will trigger apply_filter which will save

    def color(self):
        if self.image:
            self.image = ImageEnhance.Color(self.image).enhance(1.5) # Example enhance factor
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Color") # This will trigger apply_filter which will save

    def contrast(self):
        if self.image:
            self.image = ImageEnhance.Contrast(self.image).enhance(1.5) # Example enhance factor
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Contrast") # This will trigger apply_filter which will save

    def blur(self):
        if self.image:
            self.image = self.image.filter(ImageFilter.BLUR)
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.ui.filter_box.setCurrentText("Blur") # This will trigger apply_filter which will save

    # --- Centralized apply_filter method (responsible for saving) ---
    def apply_filter(self, filter_name):
        if self.image is None:
            print(f"Cannot apply filter '{filter_name}': No image loaded.")
            return

        # Always work on a copy of the *current* image from history or last operation
        # This function is usually triggered by ComboBox, so it should re-apply state
        # or confirm the current state.
        
        # A more robust apply_filter might re-process from `original` based on history.
        # But for now, if the filter is selected from ComboBox, we apply it to the current image state.
        
        # NOTE: If filter_box change *is* the source of truth, then individual buttons should
        # just change the ComboBox.
        
        # Let's ensure apply_filter does NOT apply if it's already the current state,
        # unless it's "Original" and the original is different.
        
        # First, check if the filter selected from ComboBox is the "Original" state
        if filter_name == "Original":
            if self.original and self.image != self.original: # Only revert if current is not original
                self.image = self.original.copy()
                self.add_to_history(self.image)
                self.show_image_in_box()
                self.save_image() # Save the reverted original
                print("Reverted to original image.")
            elif not self.original:
                print("No original image to revert to.")
            else:
                print("Image is already at original state.")
            return # Exit after handling Original


        # If it's not "Original", apply the selected filter
        mapping = {
            "B/W" : lambda img: img.convert("L").convert("RGBA"),
            "Color" : lambda img: ImageEnhance.Color(img).enhance(1.5), # Using a base enhance value
            "Contrast" : lambda img: ImageEnhance.Contrast(img).enhance(1.5), # Using a base enhance value
            "Blur" : lambda img: img.filter(ImageFilter.BLUR),
            "Sharpen" : lambda img: ImageEnhance.Sharpness(img).enhance(2.0), # Using a base enhance value
            "Left" : lambda img: img.transpose(Image.ROTATE_90),
            "Right" : lambda img: img.transpose(Image.ROTATE_270),
            "Mirror" : lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)
        }

        filter_function = mapping.get(filter_name)
        if filter_function:
            # Check if the effect is already applied (simple check, could be more complex)
            # This is tricky because applying the same filter twice changes the image.
            # So, we always apply and then save.
            
            # To ensure the filter is applied only once *per selection*, we should
            # ensure that apply_filter is only called when a *new* selection is made
            # OR when a button click explicitly sets the combo box.
            
            # For simplicity, we'll let it apply on every trigger from currentTextChanged
            # assuming the user intends to re-apply or confirm the filter.
            
            self.image = filter_function(self.image)
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.save_image() # <-- This is the PRIMARY place for saving
            print(f"Applied filter: {filter_name}.")
        else:
            print(f"Warning: Filter '{filter_name}' not found in mapping.")