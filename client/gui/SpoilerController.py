import logging

from PySide6.QtCore import QSize, QPropertyAnimation
from PySide6.QtWidgets import QWidget


class SpoilerController:

    def __init__(self, w: QWidget):
        self._w = w
        # self._w.
        self.hidden_height = 20
        self._w_size = self._w.size()
        self._w_m_size = self._w.maximumSize()
        self._w_l_enabled = self._w.layout().isEnabled() if self._w.layout() is not None else None

        self._anim = QPropertyAnimation(self._w, b"maximumSize")
        self._anim.finished.connect(self.set_expanded)
        self._anim.setDuration(500)

        self._expanded = True
        self._adjusted = True

        # self._w.setStyleSheet("border: 1px solid red")

    def _save_expanded_state(self):
        self._debug_size()

        if self.is_expanded() and self.is_adjusted():  # TODO Not guaranteed adjusted size.
            self._w_size = self._w.size()
            self._w_m_size = self._w.maximumSize()
            self._w_l_enabled = self._w.layout().isEnabled() if self._w.layout() is not None else None

        self._debug_size()

    def is_expanded(self):
        return self._expanded

    def is_adjusted(self):
        return self._adjusted

    def set_expanded(self, expanded: bool = None):
        if expanded is None:
            expanded = self._expanded

        self._save_expanded_state()
        if expanded:
            self._w.setMaximumSize(self._w_m_size)
            self._w.resize(self._w.size().width(), self._w_size.height())
            if self._w.layout() is not None:
                self._w.layout().setEnabled(self._w_l_enabled)
                self._w.layout().activate()
        else:
            if self._w.layout() is not None:
                self._w.layout().setEnabled(False)
            self._w.setMaximumSize(self._w_m_size.width(), self.hidden_height)
            self._w.resize(self._w.size().width(), self.hidden_height)

        self._adjusted = True
        self._expanded = expanded

        self._debug_size()

    def expand(self, expand: bool):
        self._save_expanded_state()
        self._adjusted = False

        if self._w.layout() is not None:
            self._w.layout().setEnabled(False)

        self._anim.setStartValue(self._w.size())
        self._anim.setEndValue(QSize(self._w.size().width(), self._w_size.height() if expand else self.hidden_height))
        self._anim.setCurrentTime(0)
        self._anim.start()

        self._expanded = expand

    def is_animation_finished(self):
        return self._anim.state() == QPropertyAnimation.State.Stopped

    def _debug_size(self):
        logging.getLogger('client.ui').debug(
            f"{self.__class__.__name__}({self._w.objectName()})\n"
            f"\t{self._w.size().toTuple()}-{self._w.maximumSize().toTuple()}"
            f"\t{self._w_size.toTuple()}-{self._w_m_size.toTuple()}"
            f"\tsizeHint {self._w.sizeHint()}"
            f"\tlayout {self._w.layout().geometry().size() if self._w.layout() else None}"
        )
