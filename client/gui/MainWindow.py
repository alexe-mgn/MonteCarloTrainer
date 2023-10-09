import os

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from common.exceptions import AppError

from client.utils import CONST, PATH

from client.gui.TaskDownloader import TaskDownloader
from client.gui.TaskChoiceWidget import TaskChoiceWidget
from client.gui.TaskWidget import TaskWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(CONST.CLIENT_NAME)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.choice_widget = TaskChoiceWidget()
        self.stack.addWidget(self.choice_widget)

        self.task_widget = TaskWidget()
        self.stack.addWidget(self.task_widget)

        self.stack.setCurrentWidget(self.choice_widget)

        self._connect_ui()

    def _connect_ui(self):
        self.choice_widget.complete.connect(self.start_task)

    def start_task(self):
        self.task_widget.set_task(self.choice_widget.task())
        self.stack.setCurrentWidget(self.task_widget)


class DownloaderMainWindow(MainWindow):

    def __init__(self):
        super().__init__()
        # self.choice_widget.set_task_displayed(False)
        self._downloader = TaskDownloader()
        self._downloader.updated.connect(self._downloaded)

    def load_key_path(self, p: str):
        if not os.path.isfile(p):
            raise AppError("Не удалось загрузить данные для получения таблицы заданий.")
        with open(p, mode='r') as f:
            self._downloader.set_source(f.read().strip())

    def download(self):
        self._downloader.update_tasks()

    def _downloaded(self):
        self.choice_widget.set_task_batch(self._downloader.task_batch)
