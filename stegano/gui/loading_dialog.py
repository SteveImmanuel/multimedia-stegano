from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar


class LoadingDialog(QDialog):
    def __init__(self):
        super(LoadingDialog, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Processing...')

        main_layout = QVBoxLayout()

        loading_bar = QProgressBar()
        loading_bar.setMinimum(0)
        loading_bar.setMaximum(0)

        main_layout.addWidget(loading_bar)

        self.setLayout(main_layout)
