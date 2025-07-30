from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIntValidator

class ResizeDialog(QDialog):
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Image")
        self.setFixedSize(300, 150)

        self.width = current_width
        self.height = current_height

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # Width input
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText(str(self.width))
        self.width_input.setValidator(QIntValidator(1, 99999, self)) 
        width_layout.addWidget(self.width_input)
        main_layout.addLayout(width_layout)

        # Height input
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText(str(self.height))
        self.height_input.setValidator(QIntValidator(1, 99999, self))
        height_layout.addWidget(self.height_input)
        main_layout.addLayout(height_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch(1) 
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Connect signals
        self.ok_button.clicked.connect(self.accept_and_validate)
        self.cancel_button.clicked.connect(self.reject)

    def accept_and_validate(self):
        new_width_str = self.width_input.text().strip()
        new_height_str = self.height_input.text().strip()

        try:
            width = int(new_width_str) if new_width_str else self.width
            height = int(new_height_str) if new_height_str else self.height

            if width <= 0 or height <= 0:
                QMessageBox.warning(self, "Invalid Dimensions", "Width and height must be positive integers.")
                return

            self.width = width
            self.height = height
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid integer numbers for width and height.")


    def create_int_validator(self):
        from PyQt5.QtGui import QIntValidator
        validator = QIntValidator(1, 99999, self)
        return validator

    def get_dimensions(self):
        return self.width, self.height

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = ResizeDialog(800, 600)
    if dialog.exec_() == QDialog.Accepted:
        width, height = dialog.get_dimensions()
        print(f"User entered: Width={width}, Height={height}")
    else:
        print("Dialog cancelled.")
    sys.exit(app.exec_())