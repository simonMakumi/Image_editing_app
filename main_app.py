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
        
        self._connect_signals_slots()
        
        # Apply the default theme
        self.ui.apply_theme("Dark Theme") 
        # Set the QComboBox to reflect the initial theme
        self.ui.theme_box.setCurrentText("Dark Theme")
        
        # Connect the theme_box's signal to the handler
        self.ui.theme_box.currentIndexChanged.connect(self._handle_theme_selection)

        self.ui.show()

    def _connect_signals_slots(self):
        self.ui.btn_folder.clicked.connect(self._handle_folder_selection)
        self.ui.file_list.itemClicked.connect(self._handle_file_selection)
        
        # Connect filter buttons
        self.ui.btn_left.clicked.connect(self.editor.left)
        self.ui.btn_right.clicked.connect(self.editor.right)
        self.ui.mirror.clicked.connect(self.editor.mirror)
        self.ui.sharpness.clicked.connect(self.editor.sharpen)
        self.ui.gray.clicked.connect(self.editor.gray_filter)
        self.ui.saturation.clicked.connect(self.editor.color)
        self.ui.contrast.clicked.connect(self.editor.contrast)
        self.ui.blur.clicked.connect(self.editor.blur)

        # Connect Undo/Redo
        self.ui.btn_undo.clicked.connect(self.editor.undo)
        self.ui.btn_redo.clicked.connect(self.editor.redo)

        # Connect ComboBox filter application
        self.ui.filter_box.currentTextChanged.connect(self.editor.apply_filter)
        
    def _handle_folder_selection(self):
        success = self.ui.select_directory()
        if success and self.ui.file_list.count() > 0:
            self.editor.image = None
            self.editor.original = None
            self.editor.clear_history()
            self.ui.picture_box.clear()
            self.ui.picture_box.setText("Select an image from the list.") 
            
            # Automatically select the first file if directory selection was successful 
            # and there are files to display.
            self.ui.file_list.setCurrentRow(0)
            # Trigger file selection handler for the first item
            self._handle_file_selection(self.ui.file_list.currentItem())

    def _handle_file_selection(self, item):
        filename = item.text()
        if filename:
            self.editor.load_image(filename)
            self.ui.filter_box.setCurrentText("Original")

    def _handle_theme_selection(self):
        selected_theme = self.ui.get_selected_theme_name()
        self.ui.apply_theme(selected_theme)

if __name__ == "__main__":
    app = PhotoQTApp(sys.argv)
    sys.exit(app.exec_())