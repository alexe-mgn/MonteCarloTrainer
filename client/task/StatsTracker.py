import dataclasses

from common.task.const import ACTION
from common.task.data import TaskStats
from common.task.exceptions import TaskError


@dataclasses.dataclass
class TrackedTaskStats(TaskStats):
    stats_tracker: dataclasses.InitVar['StatsTracker'] = None

    def __post_init__(self, stats_tracker: 'StatsTracker'):
        self.tracker = stats_tracker

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        self.tracker.notify_set(key, value)

    def append_error(self, error: TaskError, args: tuple = (), kwargs: dict = None):
        res = super().append_error(error, args, kwargs)
        self.tracker.notify_error(res)
        return res

    def append_action(self, action: ACTION, args: tuple = (), kwargs: dict = None):
        res = super().append_action(action, args, kwargs)
        self.tracker.notify_action(res)
        return res


class StatsTracker:

    def __init__(self, stats: TrackedTaskStats):
        self.stats = stats

    def notify_set(self, key: str, value):
        ...

    def notify_action(self, action: TrackedTaskStats.Action):
        ...

    def notify_error(self, error: TrackedTaskStats.Error):
        ...
