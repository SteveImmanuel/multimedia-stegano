from typing import Optional, Type

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

from stegano.engine import EngineFactory, BaseEngine
from stegano.gui.loading_dialog import LoadingDialog
from stegano.gui.message_dialog import MessageDialog
from stegano.gui.widget.config_box import ConfigBox
from stegano.gui.widget.io_box import InputBox, OutputBox
from stegano.gui.worker import Worker
from stegano.util import FileUtil


class ExtractTab(QWidget):
    def __init__(self):
        super(ExtractTab, self).__init__()

        self._state_config_valid = False
        self._state_input_loaded = False
        self._state_engine: Optional[Type[BaseEngine]] = None
        self._state_output_path = ''

        self._setup_ui()

    def _setup_ui(self):
        self._loading_dialog = LoadingDialog(self)

        self._file_input_box = InputBox('Input file')
        self._file_output_box = OutputBox('Message output')
        self._config_box = ConfigBox()
        self._status_label = QLabel()

        self._do_btn = QPushButton()
        self._do_btn.setText('Extract')

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._file_input_box)
        main_layout.addWidget(self._config_box)
        main_layout.addStretch()
        main_layout.addWidget(self._status_label)
        main_layout.addWidget(self._do_btn)
        main_layout.addStretch()
        main_layout.addWidget(self._file_output_box)

        self.setLayout(main_layout)

        self._file_input_box.load_btn.clicked.connect(self._on_input_load)
        self._file_input_box.path_input.textChanged.connect(self._on_input_changed)
        self._do_btn.clicked.connect(self._on_extract)

        self._check_requirement()

    def _on_input_changed(self):
        self._state_engine = None
        self._state_input_loaded = False
        self._check_requirement()

    def _process_prereq(self):
        self._file_output_box.path_output.setText('')
        self._status_label.setText('Loading...')
        self._state_config_valid = False

        if not self._state_input_loaded:
            self._status_label.setText('Please load input file')
            return

        if self._state_engine is None:
            self._status_label.setText('No suitable engine found')
            return

        self._status_label.setText('Ready')
        self._state_config_valid = True

    def _check_requirement(self):
        self._process_prereq()
        self._do_btn.setEnabled(self._state_config_valid)

    def _on_input_load(self):
        file_path = self._file_input_box.path_input.text()

        state_engine_type = EngineFactory.get_engine_to_handle_file(file_path)
        if state_engine_type is not None:
            self._state_engine = EngineFactory.get_engine_class(state_engine_type)
            self._config_box.set_engine_option(self._state_engine.get_extract_option())
        else:
            self._config_box.set_engine_option([])

        self._state_input_loaded = True
        self._check_requirement()

    def _on_extract(self):
        config = self._config_box.config

        in_path = self._file_input_box.path_input.text()
        out_path = FileUtil.get_temp_out_name()

        worker = Worker(
            lambda: self._state_engine.extract(in_path, out_path, config[0], config[1])
        )
        worker.signal.success.connect(self._on_extract_success)
        worker.signal.error.connect(self._on_extract_error)
        QThreadPool.globalInstance().start(worker)
        self._loading_dialog.exec()

    def _on_extract_success(self, out_path: str):
        self._file_output_box.path_output.setText(out_path)
        self._loading_dialog.close()

    def _on_extract_error(self, msg: str):
        self._loading_dialog.close()
        error_dialog = MessageDialog('Error', msg, self, True)
        error_dialog.exec()
