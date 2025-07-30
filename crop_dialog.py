# crop_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

class CropDialog(QDialog):
    def __init__(self, current_width, current_height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crop Image")
        self.setFixedSize(300, 200)

        self.current_width = current_width
        self.current_height = current_height

        self.x = 0
        self.y = 0
        self.width = current_width
        self.height = current_height

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # X coordinate
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X (Left):"))
        self.x_input = QLineEdit(self)
        self.x_input.setPlaceholderText("0")
        self.x_input.setValidator(QIntValidator(0, self.current_width -1 , self))
        x_layout.addWidget(self.x_input)
        main_layout.addLayout(x_layout)

        # Y coordinate
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y (Top):"))
        self.y_input = QLineEdit(self)
        self.y_input.setPlaceholderText("0")
        self.y_input.setValidator(QIntValidator(0, self.current_height -1, self))
        y_layout.addWidget(self.y_input)
        main_layout.addLayout(y_layout)

        # Width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText(str(self.current_width))
        self.width_input.setValidator(QIntValidator(1, self.current_width, self))
        width_layout.addWidget(self.width_input)
        main_layout.addLayout(width_layout)

        # Height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText(str(self.current_height))
        self.height_input.setValidator(QIntValidator(1, self.current_height, self))
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
        x_str = self.x_input.text().strip()
        y_str = self.y_input.text().strip()
        width_str = self.width_input.text().strip()
        height_str = self.height_input.text().strip()

        try:
            self.x = int(x_str) if x_str else 0
            self.y = int(y_str) if y_str else 0
            self.width = int(width_str) if width_str else self.current_width
            self.height = int(height_str) if height_str else self.current_height

            # Basic validation
            if not (0 <= self.x < self.current_width and 0 <= self.y < self.current_height):
                QMessageBox.warning(self, "Invalid Coordinates", "X and Y coordinates must be within image bounds.")
                return
            
            if not (1 <= self.width <= self.current_width - self.x and 1 <= self.height <= self.current_height - self.y):
                QMessageBox.warning(self, "Invalid Dimensions", "Crop width and height must be positive and within image bounds relative to X, Y.")
                return

            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid integer numbers for all fields.")

    def get_crop_rect(self):
        return self.x, self.y, self.width, self.height

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = CropDialog(800, 600)
    if dialog.exec_() == QDialog.Accepted:
        x, y, w, h = dialog.get_crop_rect()
        print(f"User wants to crop: X={x}, Y={y}, Width={w}, Height={h}")
    else:
        print("Crop dialog cancelled.")
    sys.exit(app.exec_())