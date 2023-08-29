from enum import Enum, Flag, auto


class STEP(Enum):
    START = 0
    RECT = 1
    POINTS = 2
    INTEGRAL = 3
    ERROR = 4
    END = 5


class ACTION(Flag):
    X_0 = auto(), STEP.RECT
    X_1 = auto(), STEP.RECT
    Y_0 = auto(), STEP.RECT
    Y_1 = auto(), STEP.RECT
    RECT_COMPLETE = auto(), STEP.RECT

    GENERATE = auto(), STEP.POINTS
    COUNT = auto(), STEP.POINTS
    COUNT_MISS = auto(), STEP.POINTS
    COUNT_HIT = auto(), STEP.POINTS
    POINTS_COMPLETE = auto(), STEP.POINTS

    AREA = auto(), STEP.INTEGRAL
    HIT = auto(), STEP.INTEGRAL
    POINTS = auto(), STEP.INTEGRAL
    RESULT = auto(), STEP.INTEGRAL
    INTEGRAL_COMPLETE = auto(), STEP.INTEGRAL

    def __new__(cls, value, step: STEP):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.step = step
        return obj


class ERROR(Flag):
    X_0 = auto(), STEP.RECT, ACTION.X_0
    X_1 = auto(), STEP.RECT, ACTION.X_1
    Y_0 = auto(), STEP.RECT, ACTION.Y_0
    Y_1 = auto(), STEP.RECT, ACTION.Y_1
    RECT_WRONG_STEP = auto(), STEP.RECT

    COUNT_BEFORE_GENERATE = auto(), STEP.POINTS, ACTION.COUNT
    POINT = auto(), STEP.POINTS, ACTION.GENERATE
    GENERATE_BEFORE_COUNT = auto(), STEP.POINTS, ACTION.GENERATE
    COUNT = auto(), STEP.POINTS, ACTION.COUNT
    NOT_ENOUGH_POINTS = auto(), STEP.POINTS, ACTION.POINTS_COMPLETE
    POINTS_WRONG_STEP = auto(), STEP.POINTS

    AREA = auto(), STEP.INTEGRAL, ACTION.AREA
    HIT = auto(), STEP.INTEGRAL, ACTION.HIT
    POINTS = auto(), STEP.INTEGRAL, ACTION.POINTS
    RESULT = auto(), STEP.INTEGRAL, ACTION.RESULT
    INTEGRAL_WRONG_STEP = auto(), STEP.INTEGRAL

    def __new__(cls, value, step: STEP, actions: ACTION = ACTION(0)):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.step = step
        obj.actions = actions
        return obj


class ERRORS:
    class RECT:
        X_0 = ERROR.X_0
        X_1 = ERROR.X_1
        Y_0 = ERROR.Y_0
        Y_1 = ERROR.Y_1
        WRONG_STEP = ERROR.RECT_WRONG_STEP

    class POINTS:
        COUNT_BEFORE_GENERATE = ERROR.COUNT_BEFORE_GENERATE
        POINT = ERROR.POINT
        GENERATE_BEFORE_COUNT = ERROR.GENERATE_BEFORE_COUNT
        COUNT = ERROR.COUNT
        NOT_ENOUGH_POINTS = ERROR.NOT_ENOUGH_POINTS
        WRONG_STEP = ERROR.POINTS_WRONG_STEP

    class INTEGRAL:
        AREA = ERROR.AREA
        HIT = ERROR.HIT
        POINTS = ERROR.POINTS
        RESULT = ERROR.RESULT
        WRONG_STEP = ERROR.INTEGRAL_WRONG_STEP
