import traceback

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
            output = self.function()
            if type(output) == str:
                out_path = output
                psnr = 0.0
            else:
                out_path, psnr = output
            self.signal.success.emit(out_path, psnr)
        except Exception as e:
            print(e)
            traceback.print_exc()
            self.signal.error.emit(str(e))
