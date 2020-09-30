from PyQt5.QtWidgets import QMainWindow, QTabWidget

from stegano.gui.widget.conceal_tab import ConcealTab
from stegano.gui.widget.extract_tab import ExtractTab


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Stagenography')
        self.setMinimumSize(500, 600)

        self._conceal_tab = ConcealTab()
        self._extract_tab = ExtractTab()

        self._tab_bar = QTabWidget()
        self._tab_bar.addTab(self._conceal_tab, 'Conceal')
        self._tab_bar.addTab(self._extract_tab, 'Extract')

        self.setCentralWidget(self._tab_bar)
