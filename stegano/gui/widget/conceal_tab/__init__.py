from os import path
from typing import Union

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QProgressDialog

from stegano.engine import EngineFactory, EngineType, BaseEngine
from stegano.gui.loading_dialog import LoadingDialog
from stegano.gui.widget.conceal_tab.summary_box import SummaryBox
from stegano.gui.widget.config_box import ConfigBox
from stegano.gui.widget.io_box import InputBox, OutputBox


class ConcealTab(QWidget):
    def __init__(self):
        super(ConcealTab, self).__init__()

        self._state_engine: Union[BaseEngine, None] = None
        self._state_engine_type: Union[EngineType, None] = None
        self._state_config_valid = False
        self._state_input_loaded = False
        self._state_message_loaded = False

        self._setup_ui()

    def _setup_ui(self):
        self._loading_dialog = LoadingDialog()

        self._file_input_box = InputBox('Input file')
        self._message_input_box = InputBox('Message file')
        self._config_box = ConfigBox()
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
        self._main_layout.addWidget(self._config_box)
        self._main_layout.addWidget(self._do_btn)
        self._main_layout.addWidget(self._file_output_box)

        self.setLayout(self._main_layout)

        self._file_input_box.load_btn.clicked.connect(self._on_input_load)
        self._file_input_box.path_input.textChanged.connect(self._on_input_changed)
        self._message_input_box.load_btn.clicked.connect(self._on_message_load)
        self._message_input_box.path_input.textChanged.connect(self._on_message_changed)
        self._do_btn.clicked.connect(self._on_conceal)

        self._check_requirement()

    def _on_input_changed(self):
        self._state_engine_type = None
        self._state_engine = None
        self._state_input_loaded = False
        self._check_requirement()

    def _on_message_changed(self):
        self._state_message_loaded = False
        self._check_requirement()

    def _process_prereq(self):
        self._summary_box.set_message('Loading...')
        self._summary_box.set_file_detail('-', 0)
        self._config_box.set_engine_option([])
        self._state_config_valid = False

        # Checking input file
        if not self._state_input_loaded:
            self._summary_box.set_message('Please load input file')
            return

        # File exists check engine
        if self._state_engine_type is None:
            self._summary_box.set_message('No suitable engine found')
            return

        # Input file and engine exists, get file info
        max_message = self._state_engine.get_max_message(self._file_input_box.path_input.text())
        self._summary_box.set_file_detail(self._state_engine_type.value, max_message)
        self._config_box.set_engine_option(self._state_engine.get_conceal_option())

        # Checking message file
        if not self._state_message_loaded:
            self._summary_box.set_message('Please load message file')
            return

        # Check message size
        message_size = path.getsize(self._message_input_box.path_input.text())
        if message_size > max_message:
            self._summary_box.set_message('Message file too large')
            return

        self._summary_box.set_message('Ready')
        self._state_config_valid = True

    def _check_requirement(self):
        self._process_prereq()
        self._do_btn.setEnabled(self._state_config_valid)

    def _on_message_load(self):
        self._state_message_loaded = True
        self._check_requirement()

    def _on_input_load(self):
        all_engine = EngineType.list()
        file_path = self._file_input_box.path_input.text()

        file_ext = path.splitext(file_path)[-1][1:]

        for engine in all_engine:
            extension_supported = EngineFactory.get_engine_class(engine).get_supported_extensions()
            if file_ext in extension_supported:
                self._state_engine_type = engine
                self._state_engine = EngineFactory.create_engine(engine)
                break

        self._state_input_loaded = True
        self._check_requirement()

    def _on_conceal(self):
        print(self._config_box.config)
        self._loading_dialog.exec()
