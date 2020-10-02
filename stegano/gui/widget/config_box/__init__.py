from typing import List, Tuple, Union

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGroupBox, QButtonGroup, QRadioButton, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QLabel, QFormLayout, QDoubleSpinBox

from stegano.gui.config_param import ConfigParam, ConfigType, FloatParam, RadioParam
from stegano.util import StringUtil


class ConfigBox(QGroupBox):
    modified = pyqtSignal()

    def __init__(self):
        super(ConfigBox, self).__init__()

        self._state_engine_option: List[ConfigParam] = []
        self._state_use_encryption = True
        self._state_engine_option_holder: List[Union[QButtonGroup, QDoubleSpinBox]] = []

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle('Options')

        self._main_layout = QFormLayout()

        # Label
        self._encrypt_option_label = QLabel()
        self._encrypt_option_label.setText('Encryption')
        self._encrypt_password_label = QLabel()
        self._encrypt_password_label.setText('Key')

        # Encryption radio
        self._encrypt_option_group = QButtonGroup()
        self._encrypt_option_layout = QHBoxLayout()

        self._encrypt_option = QRadioButton()
        self._encrypt_option.setText('Enabled')
        self._encrypt_option.setChecked(True)
        self._encrypt_option.clicked.connect(self._on_radio_selected)
        self._no_encrypt_option = QRadioButton()
        self._no_encrypt_option.setText('Disabled')
        self._no_encrypt_option.clicked.connect(self._on_radio_selected)

        self._encrypt_option_group.addButton(self._encrypt_option)
        self._encrypt_option_group.setId(self._encrypt_option, 1)
        self._encrypt_option_layout.addWidget(self._encrypt_option)

        self._encrypt_option_group.addButton(self._no_encrypt_option)
        self._encrypt_option_group.setId(self._no_encrypt_option, 0)
        self._encrypt_option_layout.addWidget(self._no_encrypt_option)

        self._encrypt_option_layout.addStretch()

        # Encryption password
        self._encrypt_password = QLineEdit()
        self._encrypt_password.setMaxLength(20)
        self._encrypt_password.setText(StringUtil.generate_random_string(6))

        # Engine options
        self._engine_option_layout = QVBoxLayout()

        # Add to layout
        self._main_layout.addRow(self._encrypt_option_label, self._encrypt_option_layout)
        self._main_layout.addRow(self._encrypt_password_label, self._encrypt_password)

        self.setLayout(self._main_layout)

    def set_engine_option(self, engine_option: List[ConfigParam]):
        row_count = self._main_layout.rowCount()

        for i in range(row_count - 1, 1, -1):
            self._main_layout.removeRow(i)

        if len(engine_option) == 0:
            return

        self._state_engine_option = engine_option
        self._state_engine_option_holder.clear()

        for param in engine_option:
            engine_option_label = QLabel()
            engine_option_label.setText(param.title)

            if param.config_type == ConfigType.RADIO:
                assert isinstance(param, RadioParam)

                option_group = QButtonGroup()
                button_layout = QHBoxLayout()
                for idx, (key, value) in enumerate(param.options.items()):
                    radio_btn = QRadioButton()
                    radio_btn.setText(value)
                    if idx == 0:
                        radio_btn.setChecked(True)

                    radio_btn.clicked.connect(lambda: self.modified.emit())

                    option_group.addButton(radio_btn)
                    option_group.setId(radio_btn, idx)
                    button_layout.addWidget(radio_btn)

                self._main_layout.addRow(engine_option_label, button_layout)
                self._state_engine_option_holder.append(option_group)
            elif param.config_type == ConfigType.FLOAT:
                assert isinstance(param, FloatParam)
                spinbox = QDoubleSpinBox()
                spinbox.setValue(param.default)
                spinbox.setMinimum(0)
                spinbox.setSingleStep(param.step)
                spinbox.valueChanged.connect(lambda: self.modified.emit())
                self._state_engine_option_holder.append(spinbox)
                self._main_layout.addRow(engine_option_label, spinbox)

    @property
    def config(self) -> Tuple[str, List[Union[str, float, bool]]]:
        encryption_key = self._encrypt_password.text()

        engine_param = [self._state_use_encryption]
        for idx, param in enumerate(self._state_engine_option):
            holder = self._state_engine_option_holder[idx]
            if param.config_type == ConfigType.FLOAT:
                assert isinstance(holder, QDoubleSpinBox)
                engine_param.append(holder.value())
            else:
                assert isinstance(holder, QButtonGroup)
                assert isinstance(param, RadioParam)
                option = param.options
                engine_param.append(list(option.keys())[holder.checkedId()])

        return encryption_key, engine_param

    def _on_radio_selected(self):
        # self._encrypt_password.setDisabled(self._encrypt_option_group.checkedId() == 0)
        self._state_use_encryption = self._encrypt_option_group.checkedId() == 1
