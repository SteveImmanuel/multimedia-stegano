from os import path

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLineEdit, \
    QPushButton, QHBoxLayout, QLabel, QFileDialog


class IoBox(QGroupBox):
    def __init__(self, is_input: bool = True):
        super(IoBox, self).__init__()
        self._is_input = is_input

        self._file_loaded = False

        self._setup_ui()

    def _setup_ui(self):
        if self._is_input:
            self.setTitle('Input')
        else:
            self.setTitle('Output')

        self._path_label = QLabel()
        self._path_label.setText('File path : ')

        self._file_path = QLineEdit()

        self._path_input_layout = QHBoxLayout()
        self._path_input_layout.addWidget(self._path_label)
        self._path_input_layout.addWidget(self._file_path)

        self._action_btn = QPushButton()
        if self._is_input:
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
        if self._is_input:
            filepath, _ = QFileDialog.getOpenFileName(self, 'Load file', QDir.currentPath(), '')
            if filepath:
                self._file_path.setText(filepath)
        else:
            filepath, _ = QFileDialog.getSaveFileName(self, 'Save file', QDir.currentPath(), '')
            if filepath:
                self._file_path.setText(filepath)

    def _set_button_state(self):
        if not self._is_input:
            self._action_btn.setEnabled(self._file_loaded)

        self._open_btn.setEnabled(self._file_loaded)
