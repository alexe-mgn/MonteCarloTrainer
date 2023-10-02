import dataclasses
import time

from common.task.const import STEP, ACTION, ERROR, Interval, Point


@dataclasses.dataclass
class TaskState:
    step = STEP.START
    int_x: Interval | None = None
    int_y: Interval | None = None
    points: list[Point] = dataclasses.field(default_factory=list)
    point_hits: list[bool] = dataclasses.field(default_factory=list)
    point_counted: bool = True
    result: float | None = None


@dataclasses.dataclass
class TaskStats:
    state: TaskState | None = None
    step_time: dict[STEP, float] = dataclasses.field(default_factory=dict)

    @dataclasses.dataclass
    class Action:
        action: ACTION
        time: float
        args: tuple
        kwargs: dict

        def __init__(self, action: ACTION, args: tuple = (), kwargs: dict = None):
            self.action = action
            self.time = time.time()
            self.args = args
            self.kwargs = kwargs if kwargs is not None else {}

    actions: dict[STEP, list[Action]] = dataclasses.field(default_factory=dict)

    def append_action(self, action: ACTION, args: tuple = (), kwargs: dict = None):
        if self.state is None:
            step = action.step
            raise UserWarning(f"{self} appending action {action} without state set, arguments: {args, kwargs}.")
        else:
            step = self.state.step
        res = self.Action(action, args, kwargs)
        self.actions.setdefault(step, []).append(res)
        return res

    @dataclasses.dataclass
    class Error:
        code: ERROR
        action: ACTION
        time: float
        args: tuple
        kwargs: dict

        def __init__(self, error: ERROR, args: tuple = (), kwargs: dict = None):
            self.code = error
            self.time = time.time()
            self.args = args
            self.kwargs = kwargs if kwargs is not None else {}

    errors: dict[STEP, list[Error]] = dataclasses.field(default_factory=dict)

    def append_error(self, error: ERROR, args: tuple = (), kwargs: dict = None):
        if self.state is None:
            step = error.step
            raise UserWarning(f"{self} appending error {error} without state set, arguments: {args, kwargs}.")
        else:
            step = self.state.step
        res = self.Error(error, args, kwargs)
        self.errors.setdefault(step, []).append(res)
        return res
