from PyQt5.QtWidgets import QGroupBox, QButtonGroup, QRadioButton, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QLabel


class ConfigBox(QGroupBox):
    def __init__(self):
        super(ConfigBox, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle('Options')
        self._button_group = QButtonGroup()
        self._button_group_layout = QHBoxLayout()

        self._encrypt_option = QRadioButton()
        self._encrypt_option.setText('Enabled')
        self._encrypt_option.setChecked(True)
        self._encrypt_option.clicked.connect(self._on_radio_selected)
        self._no_encrypt_option = QRadioButton()
        self._no_encrypt_option.setText('Disabled')
        self._no_encrypt_option.clicked.connect(self._on_radio_selected)

        self._button_group.addButton(self._encrypt_option)
        self._button_group.setId(self._encrypt_option, 1)
        self._button_group_layout.addWidget(self._encrypt_option)

        self._button_group.addButton(self._no_encrypt_option)
        self._button_group.setId(self._no_encrypt_option, 0)
        self._button_group_layout.addWidget(self._no_encrypt_option)

        self._password_entry_label = QLabel()
        self._password_entry_label.setText('Password : ')
        self._password_entry = QLineEdit()
        self._password_entry.setMaxLength(20)

        self._password_entry_layout = QHBoxLayout()
        self._password_entry_layout.addWidget(self._password_entry_label)
        self._password_entry_layout.addWidget(self._password_entry)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._button_group_layout)
        self._main_layout.addLayout(self._password_entry_layout)

        self.setLayout(self._main_layout)

    def _on_radio_selected(self):
        self._password_entry.setDisabled(self._button_group.checkedId() == 0)
