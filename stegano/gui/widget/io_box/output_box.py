from os import path
import shutil

from PyQt5.QtCore import QUrl, QDir
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit

from stegano.gui.widget.io_box.path_input import PathInput


class OutputBox(QGroupBox):
    def __init__(self, title: str = 'Output'):
        super(OutputBox, self).__init__()
        self._title = title

        self._file_valid = False

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle(self._title)

        self._path_output = PathInput()
        self._path_output.path_input.setReadOnly(True)

        self._save_btn = QPushButton()
        self._save_btn.setText('Save As')

        self._open_btn = QPushButton()
        self._open_btn.setText('Open')
        self._open_btn.setToolTip('Open in external program')

        self._button_layout = QHBoxLayout()
        self._button_layout.addWidget(self._save_btn)
        self._button_layout.addWidget(self._open_btn)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._path_output)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)

        self._save_btn.clicked.connect(self._on_save_btn)
        self._open_btn.clicked.connect(self._on_open_btn)
        self._path_output.path_input.textChanged.connect(self._on_path_changed)

        self._set_button_state()

    @property
    def path_output(self) -> QLineEdit:
        return self._path_output.path_input

    def _on_open_btn(self):
        file_url = QUrl.fromLocalFile(self._path_output.path_input.text())
        QDesktopServices.openUrl(file_url)

    def _on_save_btn(self):
        filepath, _ = QFileDialog.getSaveFileName(self, 'Save file as', QDir.currentPath(), '')

        if filepath:
            old_path = self._path_output.path_input.text()
            shutil.copy(old_path, filepath)
            self._path_output.path_input.setText(filepath)

    def _set_button_state(self):
        self._save_btn.setEnabled(self._file_valid)
        self._open_btn.setEnabled(self._file_valid)

    def _on_path_changed(self, new_text: str):
        self._file_valid = path.exists(new_text)
        self._set_button_state()
