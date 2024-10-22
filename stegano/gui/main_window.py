from multiprocessing import cpu_count

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow, QTabWidget

from stegano.gui.widget.conceal_tab import ConcealTab
from stegano.gui.widget.extract_tab import ExtractTab


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        QThreadPool.globalInstance().setMaxThreadCount(cpu_count())

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Steganography')
        self.setMinimumSize(500, 650)

        self._conceal_tab = ConcealTab()
        self._extract_tab = ExtractTab()

        self._tab_bar = QTabWidget()
        self._tab_bar.addTab(self._conceal_tab, 'Conceal')
        self._tab_bar.addTab(self._extract_tab, 'Extract')

        self.setCentralWidget(self._tab_bar)
