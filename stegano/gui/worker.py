from PyQt5.QtCore import QRunnable, pyqtSignal, QObject


class WorkerSignal(QObject):
    error = pyqtSignal(str)
    success = pyqtSignal(str, float)


class Worker(QRunnable):
    def __init__(self, function):
        super(Worker, self).__init__()
        self.setAutoDelete(True)
        self.function = function
        self.signal = WorkerSignal()

    def run(self):
        try:
            out_path, psnr = self.function()
            self.signal.success.emit(out_path, psnr)
        except Exception as e:
            print(e)
            self.signal.error.emit(str(e))
