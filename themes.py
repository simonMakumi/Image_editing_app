DARK_THEME_QSS = """
/* General styles for all widgets */
QWidget {
    background-color: #333333; /* Dark background */
    color: #DDDDDD; /* Light text */
    selection-background-color: #555555;
    selection-color: #FFFFFF;
}

/* Push Button styles */
QPushButton {
    background-color: #555555;
    color: #DDDDDD;
    border: 1px solid #777777;
    border-radius: 4px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #666666;
}
QPushButton:pressed {
    background-color: #444444;
}

/* List Widget (for file_list) styles */
QListWidget {
    background-color: #444444;
    color: #DDDDDD;
    border: 1px solid #555555;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #6a6a6a; /* Slightly lighter selection */
    color: #FFFFFF;
}

/* Combo Box (for filter_box and theme_box) styles */
QComboBox {
    background-color: #555555;
    color: #DDDDDD;
    border: 1px solid #777777;
    border-radius: 4px;
    padding: 2px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 1px;
    border-left-color: #777777;
    border-left-style: solid;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}
QComboBox::down-arrow {
    /* Base64 encoded PNG for a light downward arrow */
    image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAECAYAAADtSGzhAAAACXBIWXMAAA7DAAAOwwHh6xWaAAAAIElEQVQYV2NkgAEzNTVlYPjPwMTAwMDAwMDAyMDwPwMDADpIA80K1EmtAAAAAElFTkSuQmCC);
}
QComboBox QAbstractItemView { /* Styles for the dropdown list of the QComboBox */
    border: 1px solid #777777;
    background-color: #444444;
    selection-background-color: #6a6a6a;
    color: #DDDDDD;
}

/* QLabel (general, for text labels) styles */
QLabel {
    color: #DDDDDD;
}

/* Specific style for the picture_box QLabel */
QLabel#picture_box { /* Targeting picture_box by objectName */
    background-color: #222222; /* Even darker background for the image display area */
    border: 1px solid #555555;
    border-radius: 4px;
}
"""

LIGHT_THEME_QSS = """
/* General styles for all widgets */
QWidget {
    background-color: #F0F0F0; /* Light background */
    color: #333333; /* Dark text */
    selection-background-color: #CCCCCC;
    selection-color: #000000;
}

/* Push Button styles */
QPushButton {
    background-color: #E0E0E0;
    color: #333333;
    border: 1px solid #BBBBBB;
    border-radius: 4px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #DDDDDD;
}
QPushButton:pressed {
    background-color: #F0F0F0;
}

/* List Widget (for file_list) styles */
QListWidget {
    background-color: #FFFFFF;
    color: #333333;
    border: 1px solid #DDDDDD;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #BBBBBB;
    color: #333333;
}

/* Combo Box (for filter_box and theme_box) styles */
QComboBox {
    background-color: #E0E0E0;
    color: #333333;
    border: 1px solid #BBBBBB;
    border-radius: 4px;
    padding: 2px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 1px;
    border-left-color: #BBBBBB;
    border-left-style: solid;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}
QComboBox::down-arrow {
    /* Base64 encoded PNG for a dark downward arrow */
    image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAECAYAAADtSGzhAAAACXBIWXMAAA7DAAAOwwHh6xWaAAAAHElEQVQYV2NkAAJmZmZmYPhPwMDAwMDAwMDEwPA/AwMAT1wD/K6j41AAAAAASUVORK5CYII=);
}
QComboBox QAbstractItemView { /* Styles for the dropdown list of the QComboBox */
    border: 1px solid #BBBBBB;
    background-color: #E0E0E0;
    selection-background-color: #CCCCCC;
    color: #333333;
}

/* QLabel (general, for text labels) styles */
QLabel {
    color: #333333;
}

/* Specific style for the picture_box QLabel */
QLabel#picture_box {
    background-color: #FFFFFF; /* White background for the image display area */
    border: 1px solid #DDDDDD;
    border-radius: 4px;
}
"""