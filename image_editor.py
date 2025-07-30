import os
from PIL import Image, ImageEnhance, ImageFilter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer, QIODevice
import io
from PyQt5.QtWidgets import QMessageBox

class Editor:
    def __init__(self, ui):
        self.ui = ui
        self.image = None
        self.original_image = None
        self.image_history = []
        self.history_index = -1
        self.current_filename = None
        self.current_filepath = None
        
        self.edits_directory = "edits"
        if not os.path.exists(self.edits_directory):
            try:
                os.makedirs(self.edits_directory)
            except OSError as e:
                QMessageBox.critical(self.ui, "Directory Error", f"Could not create 'edits' directory: {e}")
                print(f"Error creating edits directory: {e}")

        self.filters_with_parameters = [
            "Left", "Right", "Mirror", "Sharpen", "Color", "Contrast", "Blur"
        ]

    def load_image(self, filename):
        full_path = os.path.join(self.ui.current_working_directory, filename)
        print(f"[Editor.load_image] Attempting to load: {filename}")
        print(f"[Editor.load_image] Current working directory: '{self.ui.current_working_directory}'")
        print(f"[Editor.load_image] Full image path: '{full_path}'")

        try:
            pil_image = Image.open(full_path)
            
            self.clear_history() 

            self.original_image = pil_image.copy() # Store a copy of the original
            self.image = pil_image.copy() # Set current image to the loaded one
            self.current_filename = filename
            self.current_filepath = full_path

            self.add_to_history(self.image) # Add initial state to history
            self.show_image_in_box()
            print("[Editor.load_image] Image loaded successfully and added to history.")

        except FileNotFoundError:
            QMessageBox.critical(self.ui, "File Not Found", f"Image file not found: {full_path}")
            self.ui.picture_box.setText("Image not found.")
            self._reset_image_state()
        except Image.UnidentifiedImageError:
            QMessageBox.critical(self.ui, "Unsupported Image Type", f"Could not open image. The file format might be unsupported or corrupted: {filename}")
            self.ui.picture_box.setText("Unsupported or corrupted image.")
            self._reset_image_state()
        except Exception as e:
            QMessageBox.critical(self.ui, "Loading Error", f"An error occurred while loading image '{filename}': {e}")
            self.ui.picture_box.setText("Error loading image.")
            self._reset_image_state()

    def _reset_image_state(self):
        self.image = None
        self.original_image = None
        self.current_filename = None
        self.current_filepath = None
        self.clear_history()

    def add_to_history(self, image_state):
        if self.history_index < len(self.image_history) - 1:
            self.image_history = self.image_history[:self.history_index + 1]
        
        self.image_history.append(image_state.copy())
        self.history_index = len(self.image_history) - 1
        print("Image state added to history.")

    def clear_history(self):
        self.image_history = []
        self.history_index = -1
        print("Image history cleared.")

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.image_history[self.history_index].copy()
            self.show_image_in_box()
            print("Undo applied.")
        else:
            QMessageBox.information(self.ui, "Undo", "No more undo steps available.")
            print("No more undo steps.")

    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.image = self.image_history[self.history_index].copy()
            self.show_image_in_box()
            print("Redo applied.")
        else:
            QMessageBox.information(self.ui, "Redo", "No more redo steps available.")
            print("No more redo steps.")

    def show_image_in_box(self):
        if self.image:
            # Convert PIL Image to QPixmap for display in QLabel
            image_bytes = io.BytesIO()
            # Save as PNG to support transparency if present, then convert to QPixmap
            try:
                self.image.save(image_bytes, format="PNG")
                qpixmap = QPixmap()
                qpixmap.loadFromData(image_bytes.getvalue())
                self.ui.picture_box.setPixmap(qpixmap)
            except Exception as e:
                QMessageBox.critical(self.ui, "Display Error", f"Could not display image: {e}")
                print(f"Error converting PIL image to QPixmap: {e}")
                self.ui.picture_box.clear()
                self.ui.picture_box.setText("Error displaying image.")
        else:
            self.ui.picture_box.clear()
            self.ui.picture_box.setText("Image will appear here")

    def save_image(self, path=None):
        if self.image is None:
            print("No image to save.")
            return False

        final_save_path = path if path else os.path.join(self.edits_directory, self.current_filename)
        
        if not final_save_path:
            QMessageBox.warning(self.ui, "Save Error", "Cannot determine a valid save path.")
            print("Cannot determine save path.")
            return False

        file_extension = os.path.splitext(final_save_path)[1].lower()

        try:
            if file_extension in ['.jpg', '.jpeg']:
                if self.image.mode == 'RGBA':
                    rgb_image = Image.new("RGB", self.image.size, (255, 255, 255))
                    rgb_image.paste(self.image, mask=self.image.split()[3])
                    rgb_image.save(final_save_path, quality=95)
                else:
                    self.image.save(final_save_path, quality=95)
                print(f"Image saved to: {final_save_path} (converted to RGB for JPEG)")
            else:
                self.image.save(final_save_path)
                print(f"Image saved to: {final_save_path}")
            return True
        except PermissionError:
            QMessageBox.critical(self.ui, "Save Error", f"Permission denied to save to: {final_save_path}\nPlease choose a different location.")
            print(f"Permission denied saving image to {final_save_path}")
            return False
        except Exception as e:
            QMessageBox.critical(self.ui, "Save Error", f"An error occurred while saving image to {final_save_path}: {e}")
            print(f"Error saving image to {final_save_path}: {e}")
            return False

    def apply_filter(self, filter_name, slider_value=50, is_slider_change=False):
        if self.image is None:
            print("No image loaded to apply filter.")
            return

        temp_image = self.image_history[self.history_index].copy()

        filter_function = None
        try:
            if filter_name == "Original":
                if self.original_image:
                    temp_image = self.original_image.copy()
                else:
                    QMessageBox.warning(self.ui, "Original Image", "Original image not available for reset.")
                    print("Original image not available.")
                    return
            elif filter_name == "Left":
                filter_function = lambda img, val: self.apply_left(img, val)
            elif filter_name == "Right":
                filter_function = lambda img, val: self.apply_right(img, val)
            elif filter_name == "Mirror":
                filter_function = lambda img, val: self.apply_mirror(img, val)
            elif filter_name == "Sharpen":
                filter_function = lambda img, val: self.apply_sharpen(img, val)
            elif filter_name == "B/W":
                filter_function = lambda img, val: self.apply_grayscale(img)
            elif filter_name == "Color":
                filter_function = lambda img, val: self.apply_color(img, val)
            elif filter_name == "Contrast":
                filter_function = lambda img, val: self.apply_contrast(img, val)
            elif filter_name == "Blur":
                filter_function = lambda img, val: self.apply_blur(img, val)
            else:
                QMessageBox.warning(self.ui, "Unknown Filter", f"Unknown filter selected: {filter_name}")
                print(f"Unknown filter: {filter_name}")
                return

            if filter_function:
                if filter_name == "B/W":
                    self.image = filter_function(temp_image, None)
                else:
                    self.image = filter_function(temp_image, slider_value)
                
                self.show_image_in_box()

                if not is_slider_change:
                    self.add_to_history(self.image)
                    self.save_image() 
                    print(f"Applied filter: {filter_name} with value {slider_value}. (Saved and added to history)")
                else:
                    print(f"Applied filter: {filter_name} with value {slider_value}. (Preview only)")
            elif filter_name == "Original":
                self.add_to_history(self.image)
                self.save_image()
                print("Reset to original image. (Saved and added to history)")
        except Exception as e:
            QMessageBox.critical(self.ui, "Filter Error", f"An error occurred while applying '{filter_name}' filter: {e}")
            print(f"Error applying filter {filter_name}: {e}")
            self.image = self.image_history[self.history_index].copy() 
            self.show_image_in_box()

    def apply_left(self, image_to_process, value):
        angle = -90 * (value / 100.0)
        return image_to_process.rotate(angle, expand=True)

    def apply_right(self, image_to_process, value):
        angle = 90 * (value / 100.0)
        return image_to_process.rotate(angle, expand=True)

    def apply_mirror(self, image_to_process, value):
        if value > 50:
            return image_to_process.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            return image_to_process

    def apply_sharpen(self, image_to_process, value):
        enhancer = ImageEnhance.Sharpness(image_to_process)
        factor = 0.1 + (value / 100.0) * 4.9 
        return enhancer.enhance(factor)

    def apply_grayscale(self, image_to_process):
        return image_to_process.convert("L").convert("RGB")

    def apply_color(self, image_to_process, value):
        enhancer = ImageEnhance.Color(image_to_process)
        factor = value / 50.0 
        return enhancer.enhance(factor)

    def apply_contrast(self, image_to_process, value):
        enhancer = ImageEnhance.Contrast(image_to_process)
        factor = value / 50.0 
        return enhancer.enhance(factor)

    def apply_blur(self, image_to_process, value):
        radius = value / 10.0
        return image_to_process.filter(ImageFilter.GaussianBlur(radius))
    
    def resize_image(self, new_width, new_height):
        if self.image is None:
            print("No image loaded to resize.")
            return

        try:
            print(f"Resizing image from {self.image.size} to {new_width}x{new_height}")
            self.image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.save_image()
            QMessageBox.information(self.ui, "Resize Success", "Image resized successfully!")
            print("Image resized successfully.")

        except Exception as e:
            QMessageBox.critical(self.ui, "Resize Error", f"An error occurred during image resizing: {e}")
            print(f"Error during image resizing: {e}")

    def crop_image(self, x, y, width, height):
        if self.image is None:
            QMessageBox.warning(self.ui, "No Image", "No image loaded to crop.")
            return

        try:
            # Ensure crop box is within image bounds
            img_width, img_height = self.image.size
            if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
                QMessageBox.warning(self.ui, "Invalid Crop Area", "Crop area is outside image boundaries.")
                return

            print(f"Cropping image from ({x}, {y}) with size ({width}, {height})")
            self.image = self.image.crop((x, y, x + width, y + height))
            
            self.add_to_history(self.image)
            self.show_image_in_box()
            self.save_image()
            QMessageBox.information(self.ui, "Crop Success", "Image cropped successfully!")
            print("Image cropped successfully.")

        except Exception as e:
            QMessageBox.critical(self.ui, "Crop Error", f"An error occurred during image cropping: {e}")
            print(f"Error during image cropping: {e}")