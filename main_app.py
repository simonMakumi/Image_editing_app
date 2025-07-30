import sys
from PyQt5.QtWidgets import QApplication
from photoqt_ui import PhotoQTUI
from image_editor import Editor
import themes

class PhotoQTApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.ui = PhotoQTUI()
        self.editor = Editor(self.ui)
        
        # Define filters that will use the intensity slider
        self.filters_with_parameters = ["Sharpen", "Color", "Contrast", "Blur"]

        self._connect_signals_slots()
        
        # Apply initial theme and connect theme selector
        self.ui.apply_theme("Dark Theme") 
        self.ui.theme_box.setCurrentText("Dark Theme")
        self.ui.theme_box.currentIndexChanged.connect(self._handle_theme_selection)

        # Initial state for filter parameter widgets
        self._update_filter_param_visibility("Original")

        self.ui.show()

    def _connect_signals_slots(self):
        self.ui.btn_folder.clicked.connect(self._handle_folder_selection)
        self.ui.file_list.itemClicked.connect(self._handle_file_selection)
        
        self.ui.filter_box.currentTextChanged.connect(self._handle_filter_selection)
        
        self.ui.filter_param_slider.valueChanged.connect(self._handle_slider_value_change)

        # Connect Undo/Redo
        self.ui.btn_undo.clicked.connect(self.editor.undo)
        self.ui.btn_redo.clicked.connect(self.editor.redo)

        
    def _handle_folder_selection(self):
        success = self.ui.select_directory()
        if success and self.ui.file_list.count() > 0:
            self.editor.image = None
            self.editor.original = None
            self.editor.clear_history()
            self.ui.picture_box.clear() 
            self.ui.picture_box.setText("Select an image from the list.")
            
            self.ui.file_list.setCurrentRow(0)
            # Trigger file selection handler for the first item
            self._handle_file_selection(self.ui.file_list.currentItem())
            # Reset filter to original and hide slider when new folder is selected
            self.ui.filter_box.setCurrentText("Original")
            self._update_filter_param_visibility("Original")


    def _handle_file_selection(self, item):
        filename = item.text()
        if filename:
            self.editor.load_image(filename)
            # Reset filter box to "Original" after new image load
            self.ui.filter_box.setCurrentText("Original")
            # Ensure slider is hidden for "Original" filter
            self._update_filter_param_visibility("Original")


    # Handler for theme selection
    def _handle_theme_selection(self):
        selected_theme = self.ui.get_selected_theme_name()
        self.ui.apply_theme(selected_theme)

    # Handler for filter ComboBox selection
    def _handle_filter_selection(self, filter_name):
        self._update_filter_param_visibility(filter_name)
        slider_value = self.ui.filter_param_slider.value()
        self.editor.apply_filter(filter_name, slider_value)

    # Handler for slider value changes
    def _handle_slider_value_change(self, value):
        current_filter = self.ui.filter_box.currentText()
        if current_filter in self.filters_with_parameters:
            self.editor.apply_filter(current_filter, value, is_slider_change=True)
        else:
            self.editor.apply_filter(current_filter, is_slider_change=True)


    # Method to control visibility of filter parameter widgets
    def _update_filter_param_visibility(self, current_filter_name):
        should_be_visible = current_filter_name in self.filters_with_parameters
        self.ui.filter_param_label.setVisible(should_be_visible)
        self.ui.filter_param_slider.setVisible(should_be_visible)

        if should_be_visible:
            self.ui.filter_param_slider.blockSignals(True) # Block signals to prevent immediate re-trigger
            self.ui.filter_param_slider.setValue(50) # Reset to default value
            self.ui.filter_param_slider.blockSignals(False) # Unblock signals
        

if __name__ == "__main__":
    app = PhotoQTApp(sys.argv)
    sys.exit(app.exec_())