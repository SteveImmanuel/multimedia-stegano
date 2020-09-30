from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from stegano.gui.widget.io_box import IoBox, IoBoxType


class EncryptTab(QWidget):
    def __init__(self):
        super(EncryptTab, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout()

        self._file_input_box = IoBox(IoBoxType.INPUT, 'Input file')
        self._message_input_box = IoBox(IoBoxType.INPUT, 'Message file')
        self._file_output_box = IoBox(IoBoxType.OUTPUT, 'Output file')

        self._input_layout = QHBoxLayout()
        self._input_layout.addWidget(self._file_input_box)
        self._input_layout.addWidget(self._message_input_box)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addWidget(self._file_output_box)

        self.setLayout(self._main_layout)
