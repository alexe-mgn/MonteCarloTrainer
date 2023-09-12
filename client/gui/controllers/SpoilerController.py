import logging

from PySide6.QtCore import QSize, QPropertyAnimation
from PySide6.QtWidgets import QWidget


class SpoilerController:

    def __init__(self, w: QWidget):
        self._widget = w
        # if hasattr(self._w, 'spoiler_controller'):
        #     raise AppError(f"Error initializing {self} on {w},"
        #                    f" widget already has spoiler controller {w.spoiler_controller}")
        # self._w.spoiler_controller = self
        self.hidden_height = 20
        self._w_size = self._widget.size()
        self._w_m_size = self._widget.maximumSize()
        self._w_l_enabled = self._widget.layout().isEnabled() if self._widget.layout() is not None else None

        self._anim = QPropertyAnimation(self._widget, b"maximumSize")
        self._anim.finished.connect(self.set_expanded)
        self._anim.setDuration(500)

        self._expanded = True
        self._adjusted = True

        # self._w.setStyleSheet("border: 1px solid red")

    def _save_expanded_state(self):
        self._debug_size()

        if self.is_expanded() and self.is_adjusted():  # TODO Not guaranteed adjusted size.
            self._w_size = self._widget.size()
            self._w_m_size = self._widget.maximumSize()
            self._w_l_enabled = self._widget.layout().isEnabled() if self._widget.layout() is not None else None

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
            self._widget.setMaximumSize(self._w_m_size)
            self._widget.resize(self._widget.size().width(), self._w_size.height())
            if self._widget.layout() is not None:
                self._widget.layout().setEnabled(self._w_l_enabled)
                self._widget.layout().activate()
        else:
            if self._widget.layout() is not None:
                self._widget.layout().setEnabled(False)
            self._widget.setMaximumSize(self._w_m_size.width(), self.hidden_height)
            self._widget.resize(self._widget.size().width(), self.hidden_height)

        self._adjusted = True
        self._expanded = expanded

        self._debug_size()

    def expand(self, expand: bool):
        self._save_expanded_state()
        self._adjusted = False

        if self._widget.layout() is not None:
            self._widget.layout().setEnabled(False)

        self._anim.setStartValue(self._widget.size())
        self._anim.setEndValue(QSize(self._widget.size().width(), self._w_size.height() if expand else self.hidden_height))
        self._anim.setCurrentTime(0)
        self._anim.start()

        self._expanded = expand

    def is_animation_finished(self):
        return self._anim.state() == QPropertyAnimation.State.Stopped

    def _debug_size(self):
        logging.getLogger('client.ui').debug(
            f"{self.__class__.__name__}({self._widget.objectName()})\n"
            f"\t{self._widget.size().toTuple()}-{self._widget.maximumSize().toTuple()}"
            f"\t{self._w_size.toTuple()}-{self._w_m_size.toTuple()}"
            f"\tsizeHint {self._widget.sizeHint()}"
            f"\tlayout {self._widget.layout().geometry().size() if self._widget.layout() else None}"
        )
