import functools
import logging
import math
import random
from typing import Self

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QWidget

from common.task.exceptions import TaskError
from common.task.const import STEP, ERROR, ACTION

from client.exceptions import AppError
from client.task.Task import Task

from client.gui.NotifierTaskSession import NotifierTaskSession
from client.gui.UI.TaskWidget import Ui_TaskWidget

from client.gui.controllers.SpoilerController import SpoilerController
from client.gui.controllers.error_controllers import ErrorPaletteController, ErrorMultiController, \
    ErrorPaletteDisablerController
from client.gui.plot.PlotController import PlotController
from client.gui.controllers.StatsController import StatsController


class TaskWidget(QWidget, Ui_TaskWidget):
    RECT_ALLOWED_DISTANCE = 0.5
    INPUT_BUFFER = 10

    _STEPS = (STEP.RECT, STEP.POINTS, STEP.INTEGRAL, STEP.ERROR)
    _HINTS = {
        STEP.RECT: "Выставьте прямоугольник так,"
                   " чтобы он заключал в себе функцию на заданном интервале и касался оси абсцисс.",
        STEP.POINTS: "Сгенерируйте несколько точек внутри прямоугольника,"
                     " подсчитывая, какие попадают под прямую, а какие - нет.",
        STEP.INTEGRAL: "На основе полученных ранее чисел вычислите примерное значение определённого интеграла",
        STEP.ERROR: "",
        STEP.END: "Поздравляем, всё правильно!",
    }

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

        self._task_session: NotifierTaskSession | None = None
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
            # ERROR.NOT_ENOUGH_POINTS: None,
            # ERROR.POINTS_WRONG_STEP: None,

            ERROR.AREA: ErrorPaletteController(self.inputIntArea),
            ERROR.HIT: ErrorPaletteController(self.inputIntHit),
            ERROR.POINTS: ErrorPaletteController(self.inputIntAll),
            ERROR.NEGATIVE: ErrorPaletteController(self.inputIntNegative),
            ERROR.RESULT: ErrorPaletteController(self.inputIntResult),
            # ERROR.INTEGRAL_WRONG_STEP: None,
        }
        c_count_gen.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_gen_miss.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_gen_hit.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_complete_miss.set_error_palette(ErrorPaletteController.PALETTE_HINT)
        c_complete_hit.set_error_palette(ErrorPaletteController.PALETTE_HINT)

        self.hints = dict(self._HINTS)

        self._stats_controller = StatsController(self)

        self._connect_ui()

        for step, w in self._step_widgets.items():
            w.setEnabled(False)
            w.spoiler_controller.set_expanded(False)
        self.widgetMError.hide()

    def _connect_ui(self):
        self._plot_controller.loaded.connect(self._update_plot)

        self.inputRectX1.valueChanged.connect(self._update_input_rect)
        self.inputRectX2.valueChanged.connect(self._update_input_rect)
        self.inputRectY1.valueChanged.connect(self._update_input_rect)
        self.inputRectY2.valueChanged.connect(self._update_input_rect)
        self.buttonRectComplete.clicked.connect(self._rect_complete)

        self.buttonPointsGenerate.clicked.connect(self._points_generate)
        self.buttonPointsMiss.clicked.connect(self._points_miss)
        self.buttonPointsHit.clicked.connect(self._points_hit)
        self.buttonPointsComplete.clicked.connect(self._points_complete)

        self.inputIntArea.valueChanged.connect(self._update_result_calc)
        self.inputIntHit.valueChanged.connect(self._update_result_calc)
        self.inputIntAll.valueChanged.connect(self._update_result_calc)
        self.inputIntNegative.valueChanged.connect(self._update_result_calc)
        self.buttonIntComplete.clicked.connect(self._integral_complete)

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
            b=str(task.interval[1])
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
        for step in self._STEPS:
            is_current = step == self._task_session.step
            self._step_widgets[step].setEnabled(is_current)
            self._spoilers[step].expand(is_current or step == STEP.RECT and self._task_session.step != STEP.END)

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
        for interval, inputs in zip(
                (self._task_session.task.interval, (self._task_session.f_min, self._task_session.f_max)),
                ((self.inputRectX1, self.inputRectX2), (self.inputRectY1, self.inputRectY2))
        ):
            dist = interval[1] - interval[0]
            margin = self.RECT_ALLOWED_DISTANCE * dist
            margin_interval = (interval[0] - margin, interval[1] + margin)
            power = int(math.ceil(math.log10(dist)) - 1)  # TODO Non-zero
            center = round((interval[0] + interval[1]) / 2, -power)
            for inp in inputs:
                inp.setMinimum(margin_interval[0])
                inp.setMaximum(margin_interval[1])
                inp.setSingleStep(10 ** power)
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

    @check_error
    def _rect_complete(self):
        self._task_session.set_int_x((self.inputRectX1.value(), self.inputRectX2.value()))
        self._task_session.set_int_y((self.inputRectY1.value(), self.inputRectY2.value()))
        self._session_next_step()
        self._points_init()

    def _points_update_enough(self):
        self.buttonPointsComplete.setEnabled(len(self._task_session.state.points) >= self._task_session.min_points)

    def _points_init(self):
        self._points_update_enough()

    @check_error
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
        self._session_next_step()
        self._integral_init()

    def _integral_init(self):
        state = self._task_session.state
        int_x, int_y = state.int_x, state.int_y
        area = (int_x[1] - int_x[0]) * (int_y[1] - int_y[0])
        self.inputIntArea.setMaximum(area * self.INPUT_BUFFER)
        self.inputIntNegative.setMaximum(area * self.INPUT_BUFFER)
        np = len(state.points)
        self.inputIntHit.setMaximum(np * self.INPUT_BUFFER)
        self.inputIntAll.setMaximum(np * self.INPUT_BUFFER)
        nph = sum(state.point_hits)
        negative = (int_x[1] - int_x[0]) * min(-int_y[0], 0)
        res = area * (nph / np) - negative
        self.inputIntResult.setRange(-res * self.INPUT_BUFFER, +res * self.INPUT_BUFFER)

        for inp in (self.inputIntHit, self.inputIntAll):
            inp.setEnabled(False)
        self.inputIntHit.setValue(nph)
        self.inputIntAll.setValue(np)

    def _update_result_calc(self):
        res = self.inputIntArea.value() * (
                self.inputIntHit.value() / self.inputIntAll.value()
        ) - self.inputIntNegative.value()
        self.viewIntResult.setText(f'{res:.3g}')

    @check_error
    def _integral_complete(self):
        ts = self._task_session
        ts.set_rect_area(self.inputIntArea.value())
        ts.set_points_hit(self.inputIntHit.value())
        ts.set_points_all(self.inputIntAll.value())
        ts.set_rect_negative(self.inputIntNegative.value())
        ts.set_result(self.inputIntResult.value())
        self._session_next_step()
