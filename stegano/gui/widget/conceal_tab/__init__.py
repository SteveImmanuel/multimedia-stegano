from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from stegano.gui.widget.encrypt_config import EncryptConfig
from stegano.gui.widget.io_box import InputBox, OutputBox


class ConcealTab(QWidget):
    def __init__(self):
        super(ConcealTab, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self._file_input_box = InputBox('Input file')
        self._message_input_box = InputBox('Message file')
        self._encrypt_config_box = EncryptConfig()
        self._file_output_box = OutputBox('Output file')

        self._input_layout = QHBoxLayout()
        self._input_layout.addWidget(self._file_input_box)
        self._input_layout.addWidget(self._message_input_box)

        self._do_btn = QPushButton()
        self._do_btn.setText('Conceal')

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addWidget(self._encrypt_config_box)
        self._main_layout.addWidget(self._do_btn)
        self._main_layout.addWidget(self._file_output_box)

        self.setLayout(self._main_layout)
