import os
from PIL import Image, ImageEnhance, ImageFilter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer, QIODevice
import io

class Editor:
    def __init__(self, ui):
        self.ui = ui
        self.image = None
        self.original_image = None
        self.image_history = []
        self.history_index = -1
        self.current_filename = None
        self.current_filepath = None # Full path to the original image
        
        # Directory where edited images will be saved by default
        self.edits_directory = "edits"
        if not os.path.exists(self.edits_directory):
            os.makedirs(self.edits_directory)

        self.filters_with_parameters = [
            "Left", "Right", "Mirror", "Sharpen", "Color", "Contrast", "Blur"
        ]

    def load_image(self, filename):
        full_path = os.path.join(self.ui.current_working_directory, filename)
        print(f"[Editor.load_image] Attempting to load: {filename}")
        print(f"[Editor.load_image] Current working directory: '{self.ui.current_working_directory}'")
        print(f"[Editor.load_image] Full image path: '{full_path}'")

        try:
            print("[Editor.load_image] Attempting to open image with PIL...")
            # Open the image using Pillow (PIL)
            pil_image = Image.open(full_path)
            
            # Reset history for a new image
            self.clear_history() 

            self.original_image = pil_image.copy() # Store a copy of the original
            self.image = pil_image.copy() # Set current image to the loaded one
            self.current_filename = filename
            self.current_filepath = full_path

            self.add_to_history(self.image) # Add initial state to history
            self.show_image_in_box()
            print("[Editor.load_image] Image loaded successfully and added to history.")

        except FileNotFoundError:
            print(f"Error: Image file not found at {full_path}")
            self.ui.picture_box.setText("Image not found.")
            self.image = None
            self.original_image = None
            self.current_filename = None
            self.current_filepath = None
        except Exception as e:
            print(f"Error loading image {full_path}: {e}")
            self.ui.picture_box.setText("Error loading image.")
            self.image = None
            self.original_image = None
            self.current_filename = None
            self.current_filepath = None

    def add_to_history(self, image_state):
        # Remove any "future" states if we've undone something
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
            print("No more undo steps.")

    def redo(self):
        if self.history_index < len(self.image_history) - 1:
            self.history_index += 1
            self.image = self.image_history[self.history_index].copy()
            self.show_image_in_box()
            print("Redo applied.")
        else:
            print("No more redo steps.")

    def show_image_in_box(self):
        if self.image:
            # Convert PIL Image to QPixmap for display in QLabel
            image_bytes = io.BytesIO()
            # Save as PNG to support transparency if present, then convert to QPixmap
            self.image.save(image_bytes, format="PNG")
            
            qpixmap = QPixmap()
            qpixmap.loadFromData(image_bytes.getvalue())
            self.ui.picture_box.setPixmap(qpixmap)
        else:
            self.ui.picture_box.clear() # Clear the picture box if no image
            self.ui.picture_box.setText("Image will appear here")

    def save_image(self, path=None):
        if self.image is None:
            print("No image to save.")
            return

        final_save_path = path if path else os.path.join(self.edits_directory, self.current_filename)
        
        if not final_save_path:
            print("Cannot determine save path.")
            return

        file_extension = os.path.splitext(final_save_path)[1].lower()

        try:
            if file_extension in ['.jpg', '.jpeg']:
                # Convert RGBA to RGB for JPEG saving
                rgb_image = Image.new("RGB", self.image.size, (255, 255, 255))
                rgb_image.paste(self.image, mask=self.image.split()[3] if self.image.mode == 'RGBA' else None)
                rgb_image.save(final_save_path)
                print(f"Image saved to: {final_save_path} (converted to RGB)")
            else:
                self.image.save(final_save_path)
                print(f"Image saved to: {final_save_path}")
        except Exception as e:
            print(f"Error saving image to {final_save_path}: {e}")

    def apply_filter(self, filter_name, slider_value=50, is_slider_change=False):
        if self.image is None:
            print("No image loaded to apply filter.")
            return

        # Start from the last finalized image state (for chaining)
        temp_image = self.image_history[self.history_index].copy()

        filter_function = None
        if filter_name == "Original":
            if self.original_image:
                temp_image = self.original_image.copy()
            else:
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
            print(f"Unknown filter: {filter_name}")
            return

        if filter_function:
            if filter_name == "B/W": # B/W is a special case without a slider value
                self.image = filter_function(temp_image, None)
            else:
                self.image = filter_function(temp_image, slider_value)
            
            self.show_image_in_box()

            if not is_slider_change:
                self.add_to_history(self.image)
                self.save_image() # Auto-save on filter application if not a preview
                print(f"Applied filter: {filter_name} with value {slider_value}. (Saved and added to history)")
            else:
                print(f"Applied filter: {filter_name} with value {slider_value}. (Preview only)")
        elif filter_name == "Original":
            self.add_to_history(self.image)
            self.save_image()
            print("Reset to original image. (Saved and added to history)")


    def apply_left(self, image_to_process, value):
        angle = -90 * (value / 100.0) # Scale value (0-100) to rotation angle
        return image_to_process.rotate(angle, expand=True)

    def apply_right(self, image_to_process, value):
        angle = 90 * (value / 100.0)
        return image_to_process.rotate(angle, expand=True)

    def apply_mirror(self, image_to_process, value):
        if value > 50: # Simple threshold for mirroring
            return image_to_process.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            return image_to_process # Return original if slider is low

    def apply_sharpen(self, image_to_process, value):
        enhancer = ImageEnhance.Sharpness(image_to_process)
        # Value 0 is blur, 1.0 is original, 2.0+ is sharpen
        # Scale 0-100 to 0.1-5.0 (or a suitable range)
        factor = 0.1 + (value / 100.0) * 4.9 
        return enhancer.enhance(factor)

    def apply_grayscale(self, image_to_process):
        return image_to_process.convert("L").convert("RGB") # Convert to grayscale then back to RGB for consistency

    def apply_color(self, image_to_process, value):
        enhancer = ImageEnhance.Color(image_to_process)
        # 0.0 is black and white, 1.0 is original, 2.0 is double saturation
        factor = value / 50.0 # Scale 0-100 to 0-2.0
        return enhancer.enhance(factor)

    def apply_contrast(self, image_to_process, value):
        enhancer = ImageEnhance.Contrast(image_to_process)
        # 0.0 is solid grey, 1.0 is original, 2.0 is double contrast
        factor = value / 50.0 
        return enhancer.enhance(factor)

    def apply_blur(self, image_to_process, value):
        # Scale 0-100 to a blur radius, e.g., 0-10
        radius = value / 10.0
        return image_to_process.filter(ImageFilter.GaussianBlur(radius))
    
    def resize_image(self, new_width, new_height):
        if self.image is None:
            print("No image loaded to resize.")
            return

        try:
            new_width = max(1, int(new_width))
            new_height = max(1, int(new_height))

            print(f"Resizing image from {self.image.size} to {new_width}x{new_height}")
            self.image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.add_to_history(self.image) # Add resized state to history
            self.show_image_in_box() # Update the UI
            self.save_image() # Auto-save the resized image
            print("Image resized successfully.")

        except ValueError:
            print("Invalid dimensions provided for resizing. Please enter integers.")
        except Exception as e:
            print(f"Error during image resizing: {e}")