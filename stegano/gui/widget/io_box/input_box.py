from os import path

from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog

from stegano.gui.widget.io_box.path_input import PathInput


class InputBox(QGroupBox):
    def __init__(self, title: str = 'Input'):
        super(InputBox, self).__init__()
        self._title = title

        self._file_valid = False

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle(self._title)

        self._path_input = PathInput()

        self._browse_btn = QPushButton()
        self._browse_btn.setText('Browse')
        self._load_btn = QPushButton()
        self._load_btn.setText('Load')
        self._open_btn = QPushButton()
        self._open_btn.setText('Open')
        self._open_btn.setToolTip('Open in external program')

        self._button_layout = QHBoxLayout()
        self._button_layout.addWidget(self._browse_btn)
        self._button_layout.addWidget(self._load_btn)
        self._button_layout.addWidget(self._open_btn)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._path_input)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)

        self._browse_btn.clicked.connect(self._on_browse_btn)
        self._open_btn.clicked.connect(self._on_open_btn)
        self._path_input.path_input.textChanged.connect(self._on_path_changed)

        self._set_button_state()

    @property
    def load_btn(self):
        return self._load_btn

    @property
    def path_input(self):
        return self._path_input.path_input

    def _on_open_btn(self):
        file_url = QUrl.fromLocalFile(self._path_input.path_input.text())
        QDesktopServices.openUrl(file_url)

    def _on_path_changed(self, new_text):
        self._file_valid = path.exists(new_text)
        self._set_button_state()

    def _on_browse_btn(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Load file', QDir.currentPath(), '')

        if filepath:
            self._path_input.path_input.setText(filepath)

    def _set_button_state(self):
        self._open_btn.setEnabled(self._file_valid)
        self._load_btn.setEnabled(self._file_valid)
