import functools
import logging
import math
import random
from typing import Self

from PySide6.QtCore import QSignalBlocker
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

from common.exceptions import AppError
from common.task.exceptions import TaskError
from common.task.const import STEP, ERROR, ACTION

from client.utils import STATE
from client.task.Task import Task
from client.task.LaplaceError import LaplaceError

from client.gui.NotifierTaskSession import NotifierTaskSession
from client.gui.UI.TaskWidget import Ui_TaskWidget
from client.gui.ErrorTableWidget import ErrorTableWidget

from client.gui.controllers.SpoilerController import SpoilerController
from client.gui.controllers.error_controllers import ErrorPaletteController
from client.gui.plot.PlotController import PlotController
from client.gui.controllers.StatsController import StatsController


class TaskWidget(QWidget, Ui_TaskWidget):
    RECT_ALLOWED_DISTANCE = 1.0
    INPUT_BUFFER = 10

    _STEPS = (STEP.RECT, STEP.POINTS, STEP.INTEGRAL, STEP.ERROR)
    _HINTS = {
        STEP.RECT: "Выставьте прямоугольник так,"
                   " чтобы он заключал в себе функцию на заданном интервале и касался оси абсцисс.",
        STEP.POINTS: "Сгенерируйте несколько точек внутри прямоугольника,"
                     " подсчитывая, какие попадают под прямую, а какие - нет.",
        # STEP.INTEGRAL: "На основе полученных ранее чисел вычислите примерное значение определённого интеграла",
        STEP.INTEGRAL: UserWarning("DEFINED BY .labelIntHint"),
        STEP.ERROR: UserWarning("DEFINED BY .labelErrorHint"),
        STEP.END: "Поздравляем, всё правильно!",
    }

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._error_table = None

        font = QFont("Courier")
        font.setStyleHint(font.StyleHint.TypeWriter)
        self.viewTaskF.setFont(font)
        self.viewTaskInterval.__text = self.viewTaskInterval.text()

        self._step_widgets: dict[STEP, QWidget] = {k: v for k, v in zip(
            self._STEPS,
            (self.widgetRect, self.widgetPoints, self.widgetIntegral, self.widgetError)
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

        self._task_session: NotifierTaskSession | None = None
        self._error: TaskError | None = None
        self._error_controllers = {
            ERROR.X_0: ErrorPaletteController(self.inputRectX1),
            ERROR.X_1: ErrorPaletteController(self.inputRectX2),
            ERROR.Y_0: ErrorPaletteController(self.inputRectY1),
            ERROR.Y_1: ErrorPaletteController(self.inputRectY2),
            # ERROR.RECT_WRONG_STEP: None,

            # ERROR.COUNT_BEFORE_GENERATE: None,
            # ERROR.POINT: None,
            # ERROR.GENERATE_BEFORE_COUNT: None,
            ERROR.COUNT: None,
            ERROR.COUNT_MISS: ErrorPaletteController(self.buttonPointsMiss),
            ERROR.COUNT_HIT: ErrorPaletteController(self.buttonPointsHit),
            # ERROR.NOT_ENOUGH_POINTS: None,
            # ERROR.POINTS_WRONG_STEP: None,

            ERROR.RESULT: ErrorPaletteController(self.inputIntResult),
            # ERROR.INTEGRAL_WRONG_STEP: None,

            ERROR.ERROR: ErrorPaletteController(self.inputError),
            # ERROR.ERROR_WRONG_STEP: None
        }

        self._rect_power = [0, 0]

        self.hints = dict(self._HINTS)
        self.hints[STEP.INTEGRAL] = self.labelIntHint.text()
        self.hints[STEP.ERROR] = self.labelErrorHint.text()

        self._stats_controller = StatsController(self)

        self._connect_ui()

        for step, w in self._step_widgets.items():
            w.setEnabled(False)
            w.spoiler_controller.set_expanded(False)

        self.labelIntHint.hide()
        self.labelErrorHint.hide()

    def _connect_ui(self):
        self._plot_controller.loaded.connect(self._update_plot)

        self.inputRectX1.valueChanged.connect(self._update_input_rect)
        self.inputRectX2.valueChanged.connect(self._update_input_rect)
        self.inputRectY1.valueChanged.connect(self._update_input_rect)
        self.inputRectY2.valueChanged.connect(self._update_input_rect)
        self.inputRectX1.editingFinished.connect(self._round_input_rect)
        self.inputRectX2.editingFinished.connect(self._round_input_rect)
        self.inputRectY1.editingFinished.connect(self._round_input_rect)
        self.inputRectY2.editingFinished.connect(self._round_input_rect)
        self.buttonRectComplete.clicked.connect(self._rect_complete)

        self.buttonPointsMiss.clicked.connect(self._points_miss)
        self.buttonPointsHit.clicked.connect(self._points_hit)
        self.buttonPointsComplete.clicked.connect(self._points_complete)

        self.buttonIntComplete.clicked.connect(self._integral_complete)

        self.buttonErrorTable.clicked.connect(self._show_error_table)
        self.buttonErrorComplete.clicked.connect(self._error_complete)

    def task(self):
        return self._task_session.task

    def _update_plot(self):
        if self._plot_controller.is_loaded:
            ts = self._task_session
            if ts is not None:
                self._plot_controller.set_task(ts.task)
                state = ts.state
                if ts.state.int_x and ts.state.int_y:
                    self._plot_controller.set_rect(
                        *ts.state.int_x, *ts.state.int_y
                    )
                else:
                    self._plot_controller.set_rect(
                        self.inputRectX1.value(),
                        self.inputRectX2.value(),
                        self.inputRectY1.value(),
                        self.inputRectY2.value(),
                    )
                self._plot_controller.set_rect_fill(ts.step != STEP.RECT)
                points = ts.state.points
                self._plot_controller.set_points(points)
                self._plot_controller.select_point(None if ts.state.point_counted else (len(points) - 1))
                self._plot_controller.update_plot()
            else:
                self._plot_controller.reset_data()
                self._plot_controller.update_plot()

    def _task_init(self):
        task = self._task_session.task
        self.viewTaskF.setText(task.f_unicode_str())
        self.viewTaskInterval.setText(self.viewTaskInterval.__text.format(
            a=str(task.interval[0]),
            b=str(task.interval[1]),
            p=str(task.min_points),
            e=str(task.error),
            c=str(task.confidence)
        ))

        self._task_session.start()
        self._hint_step()
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            self._spoilers[step].set_expanded(is_current)

    def _update_stats(self):
        self._stats_controller.set_stats(self._task_session.stats)

    def _register_session_action(self, action: ACTION):
        self._update_stats()

    def _register_session_error(self, error: ERROR):
        self._update_stats()

    def set_task(self, task: Task):
        self._task_session = NotifierTaskSession(task)
        self._task_session.notifier.on_action.connect(self._register_session_action)
        self._task_session.notifier.on_error.connect(self._register_session_error)
        self._task_init()
        self._rect_init()

    def _hint_step(self):
        if self._task_session.step in self.hints:
            self.viewHint.setText(self.hints[self._task_session.step])
        else:
            logging.getLogger('client.ui').warning(f"{self} not found hint for step {self._task_session.step}.")

    def _spoil_step(self):
        current = self._task_session.step
        for step in self._STEPS:
            is_current = step == current
            self._step_widgets[step].setEnabled(is_current)
            self._spoilers[step].expand(is_current or (step < current < step.ERROR))

    def _set_error(self, error: TaskError | None = None):
        if self._error is not None:
            for code, controller in self._error_controllers.items():
                if controller is not None:
                    controller.set_error_state(False)
            self._error = None
        self._points_update_enough()
        unhandled = TaskError()
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
    def _session_next_step(self):
        self._task_session.next_step()
        self._hint_step()
        self._spoil_step()

    def _rect_init(self):
        ts = self._task_session
        for n, (interval, inputs) in enumerate(zip(
                (ts.task.interval, (ts.f_min, ts.f_max)),
                ((self.inputRectX1, self.inputRectX2), (self.inputRectY1, self.inputRectY2))
        )):
            dist = interval[1] - interval[0]
            margin = self.RECT_ALLOWED_DISTANCE * dist
            margin_interval = (interval[0] - margin, interval[1] + margin)
            power = int(math.ceil(math.log10(dist) if dist > 0 else 0)) - 1
            while any(abs(round(e, -power) - e) >= dist * ts.accuracy for e in interval):
                power -= 1
            self._rect_power[n] = power
            center = round((interval[0] + interval[1]) / 2, -power)
            for inp in inputs:
                inp.setDecimals(max(0, -power + 1))
                inp.setRange(*margin_interval)
                inp.setSingleStep(round(10 ** power, -power))
                inp.setValue(center)

        self._update_plot()

    def _update_input_rect(self):
        sender = self.sender()
        updatee = None
        match sender:
            case self.inputRectX1:
                updatee = self.inputRectX2
            case self.inputRectX2:
                updatee = self.inputRectX1
            case self.inputRectY1:
                updatee = self.inputRectY2
            case self.inputRectY2:
                updatee = self.inputRectY1
            case _:
                logging.warning(f"{self} rect input updatee not found for change of {sender}.")
        direction = None
        match sender:
            case self.inputRectX1 | self.inputRectY1:
                direction = True
            case self.inputRectX2 | self.inputRectY2:
                direction = False
            case _:
                logging.warning(f"{self} rect input direction not found for change of {sender}.")
        if updatee is not None and direction is not None:
            sb = QSignalBlocker(updatee)
            sv, uv = sender.value(), updatee.value()
            if (sv > uv) if direction else (sv < uv):
                updatee.setValue(sv)
        self._update_plot()

    def _round_input_rect(self):
        for p, inputs in zip(
                self._rect_power,
                ((self.inputRectX1, self.inputRectX2), (self.inputRectY1, self.inputRectY2))
        ):
            p_r = 3 - p
            for inp in inputs:
                inp.setValue(round(inp.value(), p_r))

    @check_error
    def _rect_complete(self):
        self._task_session.set_int_x((self.inputRectX1.value(), self.inputRectX2.value()))
        self._task_session.set_int_y((self.inputRectY1.value(), self.inputRectY2.value()))
        self._session_next_step()
        self._points_init()

    def _points_update_enough(self):
        self.buttonPointsComplete.setEnabled(len(self._task_session.state.points) >= self._task_session.task.min_points)

    def _points_init(self):
        self._points_update_enough()
        self._points_generate()

    def _points_generate(self):
        x = self._task_session.state.int_x
        y = self._task_session.state.int_y
        p = (x[0] + random.random() * (x[1] - x[0]), y[0] + random.random() * (y[1] - y[0]))
        self._task_session.generate_point(p)

        self.viewPointsX.setText(f'{p[0]:.3g}')
        self.viewPointsY.setText(f'{p[1]:.3g}')
        self.viewPointsFY.setText(f'{self._task_session.task.f(p[0]):.3g}')

    @check_error
    def _points_count(self):
        hits = self._task_session.state.point_hits
        self.viewPointsMiss.display(sum(not e for e in hits))
        self.viewPointsHit.display(sum(bool(e) for e in hits))
        self._points_generate()

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
        if not self._task_session.state.point_counted:
            self._task_session.discard_point()
        self._session_next_step()
        self._integral_init()

    def _integral_init(self):
        state = self._task_session.state
        int_x, int_y = state.int_x, state.int_y
        area = (int_x[1] - int_x[0]) * (int_y[1] - int_y[0])
        np = len(state.points)
        nph = sum(state.point_hits)
        negative = (int_x[1] - int_x[0]) * min(-int_y[0], 0)
        res = area * (nph / np) - negative
        self.inputIntResult.setRange(-res * self.INPUT_BUFFER, +res * self.INPUT_BUFFER)

    @check_error
    def _integral_complete(self):
        ts = self._task_session
        ts.set_result(self.inputIntResult.value())
        self._session_next_step()
        self._error_init()

    def _error_init(self):
        state = self._task_session.state
        task = self._task_session.task

        self.viewErrorP.setText(f'{sum(state.point_hits) / len(state.points):.3g}')
        self.viewErrorConfidence.setText(f'{task.confidence:.3g}')
        self.viewErrorError.setText(f'{task.error:.3g}')

        task = self._task_session.task
        state = self._task_session.state
        p = sum(state.point_hits) / len(state.points)
        error_true = p * (1 - p) / (task.error * LaplaceError().get_inverse(task.confidence)) ** 2
        self.inputError.setRange(1, error_true * 2)
        if STATE.DEBUG:
            self.inputError.setValue(error_true)

    def _show_error_table(self):
        if self._error_table is None:
            self._error_table = ErrorTableWidget()
        self._error_table.show()
        self._error_table.adjustSize()
        self._error_table.resize(self._error_table.sizeHint() / 2)

    @check_error
    def _error_complete(self):
        ts = self._task_session
        ts.set_error(self.inputError.value())
        self._session_next_step()
        self._complete()

    def _complete(self):
        ...
