from PyQt5.QtWidgets import QApplication
import photoqt_ui
import image_editor

def main():
    app = QApplication([])

    # Instantiate the UI (main window and all its widgets)
    ui = photoqt_ui.PhotoQTUI()
    # Instantiate the Editor, passing it a reference to the UI object
    # This allows the Editor to access UI elements like picture_box and current_working_directory
    editor = image_editor.Editor(ui_ref=ui) 

    # --- Connect UI signals to Editor methods ---

    # Handler for the "Folder" button click
    def handle_folder_selection():
        # Call the UI method to open the dialog and list files.
        # The UI object itself stores the selected directory.
        ui.select_directory() 

    # Handler for when a different file is selected in the file list
    def handle_file_selection():
        filename = ui.get_selected_filename()
        if filename:
            editor.load_image(filename)
            # The image is automatically shown by editor.load_image -> editor.add_to_history -> editor.show_image_in_box

    # Handler for when a filter is selected from the dropdown
    def handle_filter_selection():
        selected_filter = ui.get_selected_filter_name()
        if selected_filter:
            editor.apply_filter(selected_filter)

    # Connect buttons and dropdowns to their handlers/editor methods
    ui.btn_folder.clicked.connect(handle_folder_selection)
    ui.file_list.currentRowChanged.connect(handle_file_selection)
    ui.filter_box.currentTextChanged.connect(handle_filter_selection)

    ui.btn_undo.clicked.connect(editor.undo)
    ui.btn_redo.clicked.connect(editor.redo)

    ui.gray.clicked.connect(editor.gray_filter)
    ui.btn_left.clicked.connect(editor.left)
    ui.btn_right.clicked.connect(editor.right)
    ui.mirror.clicked.connect(editor.mirror)
    ui.sharpness.clicked.connect(editor.sharpen)
    ui.blur.clicked.connect(editor.blur)
    ui.saturation.clicked.connect(editor.color)
    ui.contrast.clicked.connect(editor.contrast)

    # Show the main application window
    ui.show() 
    # Start the PyQt event loop
    app.exec_()

if __name__ == "__main__":
    main()