import time
from os import path
from typing import Union, Type

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from stegano.engine import EngineFactory, EngineType, BaseEngine
from stegano.gui.loading_dialog import LoadingDialog
from stegano.gui.message_dialog import MessageDialog
from stegano.gui.widget.conceal_tab.summary_box import SummaryBox
from stegano.gui.widget.config_box import ConfigBox
from stegano.gui.widget.io_box import InputBox, OutputBox
from stegano.gui.worker import Worker
from stegano.util import FileUtil


class ConcealTab(QWidget):
    def __init__(self):
        super(ConcealTab, self).__init__()

        self._state_engine: Union[Type[BaseEngine], None] = None
        self._state_engine_type: Union[EngineType, None] = None
        self._state_config_valid = False
        self._state_input_loaded = False
        self._state_message_loaded = False
        self._state_output_path = ''
        self._state_max_message = 0

        self._setup_ui()

    def _setup_ui(self):
        self._loading_dialog = LoadingDialog(self)

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

        main_layout = QVBoxLayout()
        main_layout.addLayout(self._input_layout)
        main_layout.addWidget(self._config_box)
        main_layout.addWidget(self._summary_box)
        main_layout.addStretch()
        main_layout.addWidget(self._do_btn)
        main_layout.addStretch()
        main_layout.addWidget(self._file_output_box)

        self.setLayout(main_layout)

        self._file_input_box.load_btn.clicked.connect(self._on_input_load)
        self._file_input_box.path_input.textChanged.connect(self._on_input_changed)
        self._message_input_box.load_btn.clicked.connect(self._on_message_load)
        self._message_input_box.path_input.textChanged.connect(self._on_message_changed)
        self._do_btn.clicked.connect(self._on_conceal)
        self._config_box.modified.connect(self._on_config_changed)

        self._check_requirement()

    def _on_config_changed(self):
        self._calculate_max_msg()

    def _on_input_changed(self):
        self._state_engine_type = None
        self._state_engine = None
        self._state_input_loaded = False
        self._check_requirement()

    def _on_message_changed(self):
        self._state_message_loaded = False
        self._check_requirement()

    def _process_prereq(self):
        self._file_output_box.path_output.setText('')
        self._summary_box.set_message('Loading...')
        self._summary_box.set_file_detail('-', 0)
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
        max_message = self._state_max_message
        self._summary_box.set_file_detail(self._state_engine_type.value, max_message)

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
        file_path = self._file_input_box.path_input.text()

        self._state_engine_type = EngineFactory.get_engine_to_handle_file(file_path)
        if self._state_engine_type is not None:
            self._state_engine = EngineFactory.get_engine_class(self._state_engine_type)
            self._config_box.set_engine_option(self._state_engine.get_conceal_option())

            self._calculate_max_msg()
        else:
            self._config_box.set_engine_option([])

            self._state_input_loaded = True
            self._check_requirement()

    def _calculate_max_msg(self):
        worker = Worker(
            lambda: self._load_worker_function(self._state_engine,
                                               self._file_input_box.path_input.text(),
                                               self._config_box.config[1])
        )
        worker.signal.success.connect(self._on_input_load_success)
        worker.signal.error.connect(self._on_input_load_error)
        QThreadPool.globalInstance().start(worker)
        self._loading_dialog.exec()

    def _load_worker_function(self, engine, file_input, config) -> (str, float):
        time.sleep(0.5)
        result = engine.get_max_message(file_input, config)
        return str(result), 0.0

    def _on_input_load_success(self, max_size: str, _: float):
        self._loading_dialog.close()
        self._state_max_message = int(max_size)
        self._state_input_loaded = True
        self._check_requirement()

    def _on_input_load_error(self, error_msg: str):
        self._loading_dialog.close()
        error_dialog = MessageDialog('Error', error_msg, self, True)
        error_dialog.exec()

    def _on_conceal(self):
        config = self._config_box.config

        out_path = FileUtil.get_temp_out_name()
        in_path = self._file_input_box.path_input.text()
        msg_path = self._message_input_box.path_input.text()

        worker = Worker(
            lambda: self._state_engine.conceal(in_path, msg_path, out_path, config[0], config[1])
        )
        worker.signal.success.connect(self._on_conceal_success)
        worker.signal.error.connect(self._on_conceal_error)
        QThreadPool.globalInstance().start(worker)
        self._loading_dialog.exec()

    def _on_conceal_success(self, out_path: str, psnr: float):
        self._file_output_box.path_output.setText(out_path)
        self._loading_dialog.close()

        message_box = MessageDialog('Success', 'PSNR {:.2f} dB'.format(psnr), self)
        message_box.exec()

    def _on_conceal_error(self, msg: str):
        self._loading_dialog.close()
        error_dialog = MessageDialog('Error', msg, self, True)
        error_dialog.exec()
