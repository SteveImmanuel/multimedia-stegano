from os import path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from stegano.engine import EngineFactory, EngineType, BaseEngine
from stegano.gui.widget.conceal_tab.summary_box import SummaryBox
from stegano.gui.widget.encrypt_config import EncryptConfig
from stegano.gui.widget.io_box import InputBox, OutputBox


class ConcealTab(QWidget):
    def __init__(self):
        super(ConcealTab, self).__init__()

        self._engine: BaseEngine = None
        self._engine_used: EngineType = None
        self._config_valid = False

        self._setup_ui()

    def _setup_ui(self):
        self._file_input_box = InputBox('Input file')
        self._message_input_box = InputBox('Message file')
        self._encrypt_config_box = EncryptConfig()
        self._summary_box = SummaryBox()
        self._file_output_box = OutputBox('Output file')

        self._input_layout = QHBoxLayout()
        self._input_layout.addWidget(self._file_input_box)
        self._input_layout.addWidget(self._message_input_box)

        self._do_btn = QPushButton()
        self._do_btn.setText('Conceal')

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._input_layout)
        self._main_layout.addWidget(self._summary_box)
        self._main_layout.addWidget(self._encrypt_config_box)
        self._main_layout.addWidget(self._do_btn)
        self._main_layout.addWidget(self._file_output_box)

        self.setLayout(self._main_layout)

        self._file_input_box.load_btn.clicked.connect(self._on_input_load)

    def _update_summary(self):
        if self._engine_used is None:
            self._summary_box.set_message('No suitable engine found')
        else:
            max_message = self._engine.get_max_message(self._file_input_box.path_input.text())
            self._summary_box.set_file_detail(self._engine_used.value, max_message)

    def _on_input_load(self):
        all_engine = EngineType.list()
        file_path = self._file_input_box.path_input.text()

        file_ext = path.splitext(file_path)[-1][1:]

        for engine in all_engine:
            extension_supported = EngineFactory.get_engine_class(engine).get_supported_extensions()
            if file_ext in extension_supported:
                self._engine_used = engine
                self._engine = EngineFactory.create_engine(engine)
                break

        self._update_summary()
