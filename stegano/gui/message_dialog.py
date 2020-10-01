from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QDialogButtonBox, QSizePolicy, QWidget


class MessageDialog(QDialog):
    def __init__(self, title: str, desc: str, parent: QWidget, error: bool = False):
        super(MessageDialog, self).__init__(parent)
        self._title = title
        self._desc = desc
        self._error = error

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._title)

        if self._error:
            btn = QDialogButtonBox(QDialogButtonBox.Close)
            btn.rejected.connect(self.close)
        else:
            btn = QDialogButtonBox(QDialogButtonBox.Ok)
            btn.accepted.connect(self.accept)

        lbl_dec = QLabel()
        lbl_dec.setText(self._desc)
        lbl_dec.setWordWrap(True)
        lbl_dec.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(lbl_dec)
        layout.addWidget(btn)

        self.setLayout(layout)
