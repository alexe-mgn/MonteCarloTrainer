import functools
import random
from typing import Self

from PySide6.QtGui import QPalette, Qt, QColor
from PySide6.QtWidgets import QWidget

from client.task.exceptions import TaskError
from common.task.utils import STEP, ERROR, ACTION

from client.exceptions import AppError, AppWarning
from client.task.Task import Task
from client.task.TaskSession import TaskSession

from client.gui.UI.TaskWidget import Ui_TaskWidget

from client.gui.controllers.SpoilerController import SpoilerController
from client.gui.controllers.error_controllers import ErrorPaletteController, ErrorMultiController, \
    ErrorPaletteDisablerController
from client.gui.plot.PlotController import PlotController


class TaskWidget(QWidget, Ui_TaskWidget):
    RECT_ALLOWED_DISTANCE = 0.5

    _STEPS = (STEP.RECT, STEP.POINTS, STEP.INTEGRAL, STEP.ERROR)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.viewTaskInterval.__text = self.viewTaskInterval.text()

        self._step_widgets: dict[STEP, QWidget] = {k: v for k, v in zip(
            self._STEPS,
            (self.widgetRect, self.widgetPoints, self.widgetIntegral, self.widgetMError)
        )}

        self._plot_controller = PlotController(self.viewPlot)

        self._spoilers: dict[STEP, SpoilerController] = {}
        for step, w in self._step_widgets.items():
            sc = SpoilerController(w)
            self._spoilers[step] = sc
            w.spoiler_controller = sc
            if w.layout() is not None:
                w.layout().activate()
            w.adjustSize()

        for step, w in self._step_widgets.items():
            # w.setEnabled(False)
            w.spoiler_controller.set_expanded(False)
            ...

        self._task_session: TaskSession | None = None
        self._error: TaskError | None = None
        self._error_controllers = {
            ERROR.X_0: ErrorPaletteController(self.inputRectX1),
            ERROR.X_1: ErrorPaletteController(self.inputRectX2),
            ERROR.Y_0: ErrorPaletteController(self.inputRectY1),
            ERROR.Y_1: ErrorPaletteController(self.inputRectY2),
            # ERROR.RECT_WRONG_STEP: None,

            ERROR.COUNT_BEFORE_GENERATE: ErrorMultiController(
                c_count_gen := ErrorPaletteController(self.buttonPointsGenerate),
                c_count_miss := ErrorPaletteDisablerController(self.buttonPointsMiss),
                c_count_hit := ErrorPaletteDisablerController(self.buttonPointsHit),
            ),
            # ERROR.POINT: None,
            ERROR.GENERATE_BEFORE_COUNT: ErrorMultiController(
                c_gen_gen := ErrorPaletteDisablerController(self.buttonPointsGenerate),
                c_gen_miss := ErrorPaletteController(self.buttonPointsMiss),
                c_gen_hit := ErrorPaletteController(self.buttonPointsHit),
            ),
            ERROR.COMPLETE_BEFORE_COUNT: ErrorMultiController(
                c_complete_complete := ErrorPaletteDisablerController(self.buttonPointsComplete),
                c_complete_miss := ErrorPaletteController(self.buttonPointsMiss),
                c_complete_hit := ErrorPaletteController(self.buttonPointsHit),
            ),
            ERROR.COUNT: None,
            ERROR.COUNT_MISS: ErrorPaletteDisablerController(self.buttonPointsMiss),
            ERROR.COUNT_HIT: ErrorPaletteDisablerController(self.buttonPointsHit),
            # ERROR.NOT_ENOUGH_POINTS: None, TODO
            # ERROR.POINTS_WRONG_STEP: None,

            ERROR.AREA: ErrorPaletteController(self.inputIntArea),
            ERROR.HIT: ErrorPaletteController(self.inputIntHit),
            ERROR.POINTS: ErrorPaletteController(self.inputIntAll),
            ERROR.RESULT: ErrorPaletteController(self.inputIntResult),
            # ERROR.INTEGRAL_WRONG_STEP: None,
        }
        c_count_gen.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_gen_miss.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_gen_hit.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_complete_miss.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_complete_hit.set_error_palette(ErrorPaletteController.PALETTE_HINT)

        self._connect_ui()

    def _connect_ui(self):
        self._plot_controller.loaded.connect(self._update_plot)

        self.inputRectX1.valueChanged.connect(self._update_plot)  # TODO Comparison
        self.inputRectX2.valueChanged.connect(self._update_plot)
        self.inputRectY1.valueChanged.connect(self._update_plot)
        self.inputRectY2.valueChanged.connect(self._update_plot)
        self.buttonRectComplete.clicked.connect(self._rect_complete)

        self.buttonPointsGenerate.clicked.connect(self._points_generate)
        self.buttonPointsMiss.clicked.connect(self._points_miss)
        self.buttonPointsHit.clicked.connect(self._points_hit)
        self.buttonPointsComplete.clicked.connect(self._points_complete)

        self.buttonIntComplete.clicked.connect(self._integral_complete)

    def task(self):
        return self._task_session.task

    def _update_plot(self):
        if self._plot_controller.is_loaded:
            self._plot_controller.set_task(self._task_session.task)
            if self._task_session.int_x and self._task_session.int_y:
                self._plot_controller.set_rect(
                    *self._task_session.int_x, *self._task_session.int_y
                )
            else:
                self._plot_controller.set_rect(
                    self.inputRectX1.value(),
                    self.inputRectX2.value(),
                    self.inputRectY1.value(),
                    self.inputRectY2.value(),
                )
            self._plot_controller.set_rect_fill(self._task_session.step != STEP.RECT)
            points = self._task_session.points
            self._plot_controller.set_points(points)
            self._plot_controller.select_point(None if self._task_session.point_counted else (len(points) - 1))
            self._plot_controller.update_plot()

    def set_task(self, task: Task):
        self._task_session = TaskSession(task)

        self.viewTaskF.setText(task.f_unicode_str())
        self.viewTaskInterval.setText(self.viewTaskInterval.__text.format(
            a=str(task.interval[0]),
            b=str(task.interval[1])
        ))

        dist_x = task.interval[1] - task.interval[0]
        margin_x = self.RECT_ALLOWED_DISTANCE * dist_x
        margin_interval = (task.interval[0] - margin_x, task.interval[1] + margin_x)
        self.inputRectX1.setMinimum(margin_interval[0])
        self.inputRectX2.setMinimum(margin_interval[0])
        self.inputRectX1.setMaximum(margin_interval[1])
        self.inputRectX2.setMaximum(margin_interval[1])

        # TODO Y

        self._update_plot()

        self._task_session.start()
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            self._spoilers[step].set_expanded(is_current)
            # self._spoilers[step].expand(current)

    def _set_error(self, error: TaskError | None = None):
        for code, controller in self._error_controllers.items():
            if controller is not None:
                controller.set_error_state(False)
        self._error = None
        unhandled = TaskError(action=error.action if error is not None else ACTION(0))
        if error:
            for code in ERROR:
                if code in error.code:
                    if code in self._error_controllers:
                        if self._error_controllers[code] is not None:
                            self._error_controllers[code].set_error_state(True)
                    else:
                        unhandled |= code
        self._error = error
        if unhandled:
            raise unhandled

    @staticmethod
    def check_error(func):
        @functools.wraps(func)
        def wrapper(self: Self, *args, **kwargs):
            if self._task_session is None:
                raise AppError(f"Сессия выполнения задания не задана при вызове {func}.")
            self._set_error()
            res = None
            try:
                res = func(self, *args, **kwargs)
            except TaskError as error:
                self._set_error(error)
            self._update_plot()
            return res

        return wrapper

    @check_error
    def _next_step(self):
        self._task_session.next_step()
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            # self._spoilers[step].set_expanded(current)
            self._spoilers[step].expand(is_current)

    @check_error
    def _rect_complete(self):
        self._task_session.set_int_x((self.inputRectX1.value(), self.inputRectX2.value()))
        self._task_session.set_int_y((self.inputRectY1.value(), self.inputRectY2.value()))
        self._next_step()
        # self._plot_controller.set_rect_fill(False)

    @check_error
    def _points_generate(self):
        x = self._task_session.int_x
        y = self._task_session.int_y
        p = (x[0] + random.random() * (x[1] - x[0]), y[0] + random.random() * (y[1] - y[0]))
        self._task_session.generate_point(p)

        self.viewPointsX.setText(f'{p[0]:.3g}')
        self.viewPointsY.setText(f'{p[1]:.3g}')
        self.viewPointsFY.setText(f'{self._task_session.task.f(p[0]):.3g}')
        # self._plot_controller.add_point(p)

    @check_error
    def _points_count(self):
        hits = self._task_session.point_hits
        self.viewPointsMiss.display(sum(not e for e in hits))
        self.viewPointsHit.display(sum(bool(e) for e in hits))

    @check_error
    def _points_miss(self):
        self._task_session.count_point(False)
        self._points_count()

    @check_error
    def _points_hit(self):
        self._task_session.count_point(True)
        self._points_count()

    @check_error
    def _points_complete(self):
        self._next_step()

    @check_error
    def _integral_complete(self):
        self._next_step()
