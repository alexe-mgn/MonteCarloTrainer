from PySide6.QtWidgets import QWidget

from client.exceptions import AppError
from common.task.utils import STEP
from client.task.Task import Task, TaskSession

from client.gui.UI.TaskWidget import Ui_TaskWidget

from client.gui.SpoilerController import SpoilerController
from client.gui.plot.PlotController import PlotController


class TaskWidget(QWidget, Ui_TaskWidget):
    _STEPS = (STEP.RECT, STEP.POINTS, STEP.INTEGRAL, STEP.ERROR)

    def __init__(self):
        super().__init__()
        self.setupUi()
        self._step_widgets: dict[STEP, QWidget] = {k: v for k, v in zip(
            self._STEPS,
            (self.widgetRect, self.widgetPoints, self.widgetIntegral, self.widgetMError)
        )}

        self._plot_controller = PlotController(self.viewPlot)

        self._spoilers: dict[STEP, SpoilerController] = {}
        for step, w in self._step_widgets.items():
            sc = SpoilerController(w)
            self._spoilers[step] = sc
            w.sc = sc
            if w.layout() is not None:
                w.layout().activate()
            w.adjustSize()

            w.mousePressEvent = lambda *args, sc=sc: (sc._w.setEnabled(True), sc.expand(not sc.is_expanded()))

        for step, w in self._step_widgets.items():
            # w.setEnabled(False)
            w.sc.set_expanded(False)
            ...

        self._task_session: TaskSession | None = None

    def setupUi(self, target=None):
        super().setupUi(self if target is None else target)
        for w in (self.buttonRectComplete, self.buttonPointsComplete, self.buttonIntComplete):
            w.clicked.connect(self.next_step)

    def task(self):
        return self._task_session.task

    def set_task(self, task: Task):
        self._task_session = TaskSession(task)
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            self._spoilers[step].set_expanded(is_current)
            # self._spoilers[step].expand(current)

    def next_step(self):
        if self._task_session is None:
            raise AppError(f"Сессия выполнения задания не задана.")
        self._task_session.next_step()
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            # self._spoilers[step].set_expanded(current)
            self._spoilers[step].expand(is_current)
