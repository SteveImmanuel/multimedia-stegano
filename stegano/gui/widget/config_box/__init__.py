from typing import List, Dict, Tuple

from PyQt5.QtWidgets import QGroupBox, QButtonGroup, QRadioButton, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QLabel, QFormLayout

from stegano.util import StringUtil


class ConfigBox(QGroupBox):
    def __init__(self):
        super(ConfigBox, self).__init__()

        self._state_engine_option_loaded: bool = False
        self._state_engine_option: List[Dict[str, str]] = []
        self._state_use_encryption = True

        self._engine_option_group: List[QButtonGroup] = []

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle('Options')

        self._main_layout = QFormLayout()

        # Label
        self._encrypt_option_label = QLabel()
        self._encrypt_option_label.setText('Encryption')
        self._encrypt_password_label = QLabel()
        self._encrypt_password_label.setText('Password')

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

    def set_engine_option(self, engine_option: List[Dict[str, str]]):
        if self._state_engine_option_loaded:
            self._state_engine_option_loaded = False
            self._main_layout.removeRow(2)

        if len(engine_option) == 0:
            return

        self._state_engine_option = engine_option

        engine_option_label = QLabel()
        engine_option_label.setText('Engine param')
        engine_option_layout = QVBoxLayout()
        self._engine_option_group.clear()

        for option in engine_option:
            option_group = QButtonGroup()
            button_layout = QHBoxLayout()
            for idx, (key, value) in enumerate(option.items()):
                radio_btn = QRadioButton()
                radio_btn.setText(value)
                if idx == 0:
                    radio_btn.setChecked(True)

                option_group.addButton(radio_btn)
                option_group.setId(radio_btn, idx)
                button_layout.addWidget(radio_btn)

            engine_option_layout.addLayout(button_layout)
            self._engine_option_group.append(option_group)

        self._state_engine_option_loaded = True
        self._main_layout.addRow(engine_option_label, engine_option_layout)

    @property
    def config(self) -> Tuple[str, List[str]]:
        encryption_key = '' if not self._state_use_encryption else self._encrypt_password.text()

        engine_param = []
        for idx, group in enumerate(self._engine_option_group):
            option = self._state_engine_option[idx]
            engine_param.append(list(option.keys())[group.checkedId()])

        return encryption_key, engine_param

    def _on_radio_selected(self):
        self._encrypt_password.setDisabled(self._encrypt_option_group.checkedId() == 0)
        self._state_use_encryption = self._encrypt_option_group.checkedId() == 1
