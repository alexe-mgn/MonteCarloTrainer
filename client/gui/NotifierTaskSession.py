from PySide6.QtCore import QObject, Signal

from common.task.const import ACTION, ERROR
from common.task.exceptions import TaskError

from client.task.Task import Task
from client.task.TaskSession import TaskSession


class StatsSignalNotifier(QObject):
    on_action = Signal(ACTION)
    on_error = Signal(ERROR)


class NotifierTaskSession(TaskSession):

    def __init__(self, task: Task):
        self._notifier = StatsSignalNotifier()
        super().__init__(task)

    @property
    def notifier(self) -> StatsSignalNotifier:
        return self._notifier

    def _notify_action(self, action: ACTION, args: tuple, kwargs: dict):
        self._notifier.on_action.emit(action)

    def _notify_error(self, error: ERROR, args: tuple, kwargs: dict):
        self._notifier.on_error.emit(error)
        super()._notify_error(error, args, kwargs)
