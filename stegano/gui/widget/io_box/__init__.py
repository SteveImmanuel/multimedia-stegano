from enum import Enum
from os import path

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLineEdit, \
    QPushButton, QHBoxLayout, QLabel, QFileDialog


class IoBoxType(Enum):
    INPUT = 'input'
    OUTPUT = 'output'


class IoBox(QGroupBox):
    def __init__(self, box_type: IoBoxType = IoBoxType.INPUT, title: str = 'Input'):
        super(IoBox, self).__init__()
        self._box_type = box_type
        self._title = title

        self._file_loaded = False

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle(self._title)

        self._path_label = QLabel()
        self._path_label.setText('File path : ')

        self._file_path = QLineEdit()

        self._path_input_layout = QHBoxLayout()
        self._path_input_layout.addWidget(self._path_label)
        self._path_input_layout.addWidget(self._file_path)

        self._action_btn = QPushButton()
        if self._box_type == IoBoxType.INPUT:
            self._action_btn.setText('Load')
        else:
            self._action_btn.setText('Save')

        self._open_btn = QPushButton()
        self._open_btn.setText('Open')
        self._open_btn.setToolTip('Open in external program')

        self._button_layout = QHBoxLayout()
        self._button_layout.addWidget(self._action_btn)
        self._button_layout.addWidget(self._open_btn)

        self._layout = QVBoxLayout()
        self._layout.addLayout(self._path_input_layout)
        self._layout.addLayout(self._button_layout)

        self.setLayout(self._layout)

        self._action_btn.clicked.connect(self._on_action_btn)
        self._open_btn.clicked.connect(self._on_open_btn)
        self._file_path.textChanged.connect(self._on_path_changed)

        self._set_button_state()

    def _on_open_btn(self):
        file_url = QUrl.fromLocalFile(self._file_path.text())
        QDesktopServices.openUrl(file_url)

    def _on_path_changed(self, new_text):
        self._file_loaded = path.exists(new_text)
        self._set_button_state()

    def _on_action_btn(self):
        if self._box_type == IoBoxType.INPUT:
            filepath, _ = QFileDialog.getOpenFileName(self, 'Load file', QDir.currentPath(), '')
        else:
            filepath, _ = QFileDialog.getSaveFileName(self, 'Save file', QDir.currentPath(), '')

        if filepath:
            self._file_path.setText(filepath)

    def _set_button_state(self):
        if self._box_type == IoBoxType.OUTPUT:
            self._action_btn.setEnabled(self._file_loaded)

        self._open_btn.setEnabled(self._file_loaded)
