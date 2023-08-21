import random

from PySide6.QtWidgets import QWidget

from common.task.utils import STEP

from client.exceptions import AppError
from client.task.Task import Task
from client.task.TaskSession import TaskSession

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

        self._connect_ui()

    def setupUi(self, target=None):
        super().setupUi(self if target is None else target)
        for w in (self.buttonRectComplete, self.buttonPointsComplete, self.buttonIntComplete):
            w.clicked.connect(self.next_step)

    def _connect_ui(self):
        self.buttonRectComplete.clicked.connect(self._rect_complete)
        self.buttonPointsComplete.clicked.connect(self._points_complete)
        self.buttonIntComplete.clicked.connect(self._integral_complete)

    def task(self):
        return self._task_session.task

    def set_task(self, task: Task):
        self._task_session = TaskSession(task)
        self._task_session.start()
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

    def _rect_complete(self):
        self._task_session.set_int_x((self.inputRectX1.value(), self.inputRectX2.value()))
        self._task_session.set_int_y((self.inputRectY1.value(), self.inputRectY2.value()))
        self.next_step()

    def _points_generate(self):
        x = self._task_session.int_x()
        y = self._task_session.int_y()
        p = (x[0] + random.random() * (x[1] - x[0]), y[0] + random.random() * (y[1] - y[0]))
        self._task_session.generate_point(p)

        self.viewPointsX.setText(str(p[0]))
        self.viewPointsY.setText(str(p[1]))
        self.viewPointsFY.setText(str(self._task_session.task.f(p[0])))

    def _points_count(self):
        hits = self._task_session.point_hits()
        self.viewPointsMiss.display(sum(not e for e in hits))
        self.viewPointsHit.display(sum(bool(e) for e in hits))

    def _points_miss(self):
        self._task_session.count_point(False)
        self._points_count()

    def _points_hit(self):
        self._task_session.count_point(True)
        self._points_count()

    def _points_complete(self):
        self.next_step()

    def _integral_complete(self):
        self.next_step()
