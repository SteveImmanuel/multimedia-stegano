from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QWidget


class LoadingDialog(QDialog):
    def __init__(self, parent: QWidget):
        super(LoadingDialog, self).__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Processing...')
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        main_layout = QVBoxLayout()

        loading_bar = QProgressBar()
        loading_bar.setMinimum(0)
        loading_bar.setMaximum(0)

        main_layout.addWidget(loading_bar)

        self.setLayout(main_layout)
