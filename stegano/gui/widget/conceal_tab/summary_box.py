from PyQt5.QtWidgets import QGroupBox, QLabel, QFormLayout


class SummaryBox(QGroupBox):
    def __init__(self):
        super(SummaryBox, self).__init__()

        self._setup_ui()

    def _setup_ui(self):
        self.setTitle('Summary')

        self._message = QLabel()

        self._engine_type_label = QLabel()
        self._engine_type_label.setText('Engine')
        self._engine_type = QLabel()
        self._max_message_label = QLabel()
        self._max_message_label.setText('Max message')
        self._max_message = QLabel()

        self._layout = QFormLayout()
        self._layout.addRow(self._message)
        self._layout.addRow(self._engine_type_label, self._engine_type)
        self._layout.addRow(self._max_message_label, self._max_message)

        self.set_file_detail('-', 0)
        self.set_message('Please select file')

        self.setLayout(self._layout)

    def set_message(self, message: str):
        self._message.setText(message)

    def set_file_detail(self, engine: str, max_message: int):
        self._engine_type.setText(': {}'.format(engine))
        self._max_message.setText(': {} bytes'.format(max_message))
