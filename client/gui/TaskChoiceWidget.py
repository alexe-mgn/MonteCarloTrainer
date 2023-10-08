import sys

from PySide6.QtCore import Signal, QSignalBlocker
from PySide6.QtWidgets import QWidget

from common.exceptions import AppError
from common.TaskBatch import TaskBatch

from client.task.Task import Task

from client.gui.UI.TaskChoiceWidget import Ui_TaskChoiceWidget


class TaskChoiceWidget(QWidget, Ui_TaskChoiceWidget):
    complete = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        font = self.viewTask.font()
        font.setStyleHint(font.StyleHint.Monospace)
        self.viewTask.setFont(font)
        for i in (self.inputStart, self.inputEnd):
            i.setRange(-sys.maxsize, sys.maxsize)
        self.inputPoints.setRange(1, 2 ** 31 - 1)

        self._task: Task | None = None
        self._task_batch = None
        self.set_task_batch(self._task_batch)
        self.update_task()

        self._connect_ui()

        self.labelProgram.hide()
        self.inputProgram.hide()
        self.labelGroup.hide()
        self.inputGroup.hide()

    def _connect_ui(self):
        for ci in (self.inputProgram, self.inputGroup, self.inputName):
            ci.currentIndexChanged.connect(lambda e: self.set_task_index(e - 1))
        for signal in (self.inputF.textChanged, self.inputStart.valueChanged, self.inputEnd.valueChanged):
            signal.connect(self.update_task)
        self.buttonComplete.clicked.connect(self._emit_complete)

    def task_batch(self):
        return list(self._task_batch)

    def set_task_batch(self, task_batch: TaskBatch | None):
        self._task_batch = task_batch
        for ci in (self.inputProgram, self.inputGroup, self.inputName):
            ci.setEnabled(task_batch is not None)
            ci.setMaxCount(0)
        for ti in (self.inputF, self.inputStart, self.inputEnd):
            ti.setEnabled(task_batch is None)
        if task_batch is not None:
            self.inputName.setMaxCount(len(task_batch) + 1)
            self.inputName.addItem('')
            for i in task_batch:
                self.inputName.addItem(i[0])

    def set_task_index(self, n: int):
        if self._task_batch is None:
            raise AppError(f"{self.__class__.__name__} requires defined task batch to set task index.")
        else:
            task_tuple = self._task_batch[n] if n >= 0 else ('', '', 0, 0)
            sb = QSignalBlocker(self.inputName)
            self.inputName.setCurrentIndex(n + 1 if n >= 0 else 0)

            self.inputF.setText(task_tuple[1])
            self.inputStart.setValue(task_tuple[2])
            self.inputEnd.setValue(task_tuple[3])

    def task(self) -> Task | None:
        return Task(
            self.inputF.text(), (self.inputStart.value(), self.inputEnd.value()),
            self.inputPoints.value(),
            self.inputError.value(), self.inputConfidence.value()
        ) if self.inputF.text() else None

    def update_task(self):
        self._task = None
        try:
            self._task = self.task()
        except Exception as error:  # TODO
            self.viewTask.setText(str(error))
            self.buttonComplete.setEnabled(False)
        else:
            enabled = self._task is not None
            self.viewTask.setText(self._task.unicode_str() if enabled else '')
            self.buttonComplete.setEnabled(enabled)

    def _emit_complete(self):
        self.complete.emit()
