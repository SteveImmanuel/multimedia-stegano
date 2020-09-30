from PyQt5.QtWidgets import QMainWindow, QTabWidget

from stegano.gui.widget.encrypt_tab import EncryptTab


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Stagenography')
        self.setMinimumSize(500, 600)

        self._encrypt_tab = EncryptTab()
        self._decrypt_tab = EncryptTab()

        self._tab_bar = QTabWidget()
        self._tab_bar.addTab(self._encrypt_tab, 'Encrypt')
        self._tab_bar.addTab(self._decrypt_tab, 'Decrypt')

        self.setCentralWidget(self._tab_bar)
