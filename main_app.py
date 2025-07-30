# main_app.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QDialog

from resize_dialog import ResizeDialog
from photoqt_ui import PhotoQTUI
from image_editor import Editor

class MainAppController(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = PhotoQTUI()
        self.editor = Editor(self.ui)
        self.setup_connections()
        self.ui.show()

    def setup_connections(self):
        # File/Directory Operations
        self.ui.btn_folder.clicked.connect(self.select_directory_and_load)
        self.ui.file_list.currentItemChanged.connect(self.load_selected_image)
        
        # Filter Operations
        self.ui.filter_box.currentTextChanged.connect(self.handle_filter_selection)
        self.ui.filter_param_slider.valueChanged.connect(self.handle_slider_change)
        self.ui.filter_param_slider.sliderReleased.connect(self.handle_slider_release)
        
        # Undo/Redo
        self.ui.btn_undo.clicked.connect(self.editor.undo)
        self.ui.btn_redo.clicked.connect(self.editor.redo)
        
        # Theme Selection
        self.ui.theme_box.currentTextChanged.connect(self.ui.apply_theme)

        # Save Operations
        self.ui.btn_save_as.clicked.connect(self.save_image_as_dialog)

        self.ui.btn_resize.clicked.connect(self.open_resize_dialog)

    def select_directory_and_load(self):
        if self.ui.select_directory():
            if self.ui.file_list.count() > 0:
                self.ui.file_list.setCurrentRow(0) # Selects first item, which triggers load_selected_image
            else:
                self.editor.image = None
                self.ui.picture_box.clear()
                self.ui.picture_box.setText("No images found in this folder.")
                self.editor.clear_history()

    def load_selected_image(self, current_item):
        if current_item:
            filename = current_item.text()
            # Editor handles constructing the full path
            self.editor.load_image(filename)

    def handle_filter_selection(self, filter_name):
        if filter_name in self.editor.filters_with_parameters:
            self.ui.filter_param_slider.setValue(50) # Reset slider to default
            self.ui.filter_param_label.setVisible(True)
            self.ui.filter_param_slider.setVisible(True)
            self.editor.apply_filter(filter_name, slider_value=50, is_slider_change=False) 
        else:
            self.ui.filter_param_label.setVisible(False)
            self.ui.filter_param_slider.setVisible(False)
            self.editor.apply_filter(filter_name, is_slider_change=False)

    def handle_slider_change(self, value):
        current_filter = self.ui.get_selected_filter_name()
        if current_filter in self.editor.filters_with_parameters:
            self.editor.apply_filter(current_filter, slider_value=value, is_slider_change=True)

    def handle_slider_release(self):
        current_filter = self.ui.get_selected_filter_name()
        # Finalize filter application when slider is released
        if current_filter in self.editor.filters_with_parameters:
            self.editor.apply_filter(current_filter, slider_value=self.ui.filter_param_slider.value(), is_slider_change=False)

    def save_image_as_dialog(self):
        if self.editor.image is None:
            print("No image to save.")
            return

        # Suggest an initial filename and path in the 'edits' directory
        initial_filename = "edited_" + (self.editor.current_filename if self.editor.current_filename else "image.png")
        initial_save_path = os.path.join(self.editor.edits_directory, initial_filename)

        # Open file dialog for saving
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image As", initial_save_path, 
                                                 "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;All Files (*.*)")
        
        if file_path:
            print(f"User selected save path: {file_path}")
            # Call the editor's save method, which handles format conversion if necessary
            self.editor.save_image(path=file_path)
        else:
            print("Save As operation cancelled by user.")

    def open_resize_dialog(self):
        if self.editor.image is None:
            print("No image loaded to resize.")
            return

        current_width, current_height = self.editor.image.size
        print(f"Current image dimensions: {current_width}x{current_height}")

        dialog = ResizeDialog(current_width, current_height, self) # Pass current dimensions and self as parent
        if dialog.exec_() == QDialog.Accepted:
            new_width, new_height = dialog.get_dimensions()
            print(f"User wants to resize to: {new_width}x{new_height}")
            # Call the editor's resize method
            self.editor.resize_image(new_width, new_height)
        else:
            print("Resize operation cancelled.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app_controller = MainAppController() # Corrected to MainAppController
    sys.exit(app.exec_())