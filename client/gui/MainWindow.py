from PySide6.QtWidgets import QMainWindow, QStackedWidget

from client.gui.TaskChoiceWidget import TaskChoiceWidget
from client.gui.TaskWidget import TaskWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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
