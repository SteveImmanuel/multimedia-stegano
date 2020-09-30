from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class PathInput(QWidget):
    def __init__(self):
        super(PathInput, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self._path_label = QLabel()
        self._path_label.setText('File path : ')

        self.path_input = QLineEdit()

        self._path_input_layout = QHBoxLayout()
        self._path_input_layout.addWidget(self._path_label)
        self._path_input_layout.addWidget(self.path_input)

        self.setLayout(self._path_input_layout)
