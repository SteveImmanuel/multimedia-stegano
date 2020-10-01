from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QSizePolicy


class MessageDialog(QDialog):
    def __init__(self, title: str, desc: str):
        super(MessageDialog, self).__init__()
        self._title = title
        self._desc = desc

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._title)

        btn_ok = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_ok.accepted.connect(self.accept)

        lbl_dec = QLabel()
        lbl_dec.setText(self._desc)
        lbl_dec.setWordWrap(True)
        lbl_dec.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(lbl_dec)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
