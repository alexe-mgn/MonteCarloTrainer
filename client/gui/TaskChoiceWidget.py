from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from client.task.Task import Task

from client.gui.UI.TaskChoiceWidget import Ui_TaskChoiceWidget


class TaskChoiceWidget(QWidget, Ui_TaskChoiceWidget):
    complete = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._task: Task | None = None

        self._connect_ui()

    def _connect_ui(self):
        for signal in (self.inputF.textChanged, self.inputStart.valueChanged, self.inputEnd.valueChanged):
            signal.connect(self.update_task)
        self.buttonComplete.clicked.connect(self._emit_complete)

    def task(self):
        return Task(self.inputF.text(), (self.inputStart.value(), self.inputEnd.value()))

    def update_task(self):
        self._task = None
        try:
            self._task = self.task()
        except Exception as error:  # TODO
            self.viewTask.setText(str(error))
        else:
            self.viewTask.setText(self._task.unicode_str())

    def _emit_complete(self):
        self.complete.emit()
