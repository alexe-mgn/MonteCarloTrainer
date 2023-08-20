from enum import Enum, Flag, auto


class STEP(Enum):
    START = 0
    RECT = 1
    POINTS = 2
    INTEGRAL = 3
    ERROR = 4
    END = 5


class ACTION(Flag):
    X_0 = auto()
    X_1 = auto()
    Y_0 = auto()
    Y_1 = auto()
    RECT_COMPLETE = auto()

    GENERATE = auto()
    COUNT = auto()
    COUNT_MISS = auto()
    COUNT_HIT = auto()
    POINTS_COMPLETE = auto()

    AREA = auto()
    HIT = auto()
    POINTS = auto()
    RESULT = auto()
    INTEGRAL_COMPLETE = auto()


class ERROR(Flag):
    X_0 = auto()
    X_1 = auto()
    Y_0 = auto()
    Y_1 = auto()
    RECT_WRONG_STEP = auto()

    COUNT_BEFORE_GENERATE = auto()
    POINT = auto()
    GENERATE_BEFORE_COUNT = auto()
    COUNT = auto()
    NOT_ENOUGH_POINTS = auto()
    POINTS_WRONG_STEP = auto()

    AREA = auto()
    HIT = auto()
    POINTS = auto()
    RESULT = auto()
    INTEGRAL_WRONG_STEP = auto()


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
