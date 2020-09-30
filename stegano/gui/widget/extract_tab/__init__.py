from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from stegano.gui.widget.io_box import InputBox, OutputBox


class ExtractTab(QWidget):
    def __init__(self):
        super(ExtractTab, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self._file_input_box = InputBox('Input file')
        self._file_output_box = OutputBox('Output file')

        self._do_btn = QPushButton()
        self._do_btn.setText('Extract')

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._file_input_box)
        self._main_layout.addWidget(self._do_btn)
        self._main_layout.addWidget(self._file_output_box)

        self.setLayout(self._main_layout)
