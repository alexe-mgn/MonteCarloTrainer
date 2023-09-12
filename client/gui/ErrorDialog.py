from typing import *
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from client.gui.UI.ErrorDialog import Ui_ErrorDialog


class ErrorDialog(QDialog, Ui_ErrorDialog):
    EXCEPTHOOK_SET = False

    def __init__(self,
                 exc_type: Type[BaseException] = None,
                 exc_value: BaseException = None,
                 exc_traceback=None):
        super().__init__()
        self.setupUi(self)

        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.buttonDetails.clicked.connect(lambda: self.toggle_details())
        self.dialogButtons.clicked.connect(self.reject)
        self.toggle_details(False)

        self.setWindowTitle("Ошибка" if exc_type is None else exc_type.__name__)
        if exc_value is not None:
            self.text = str(exc_value)
        if exc_traceback is not None:
            self.details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    @classmethod
    def excepthook(cls, exc_type, exc_value, exc_traceback):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

        d = cls(exc_type, exc_value, exc_traceback)
        d.setModal(True)
        d.exec()

    @classmethod
    def setup_excepthook(cls):
        import logging
        log = logging.getLogger('client.app')
        if cls.EXCEPTHOOK_SET:
            log.warning(f"{cls} setting up excepthook not for a first time.")
        log.info(f"Setting up {cls} as sys excepthook.")
        sys.excepthook = cls.excepthook

    @classmethod
    def get_from_exc(cls):
        d = cls(*sys.exc_info())
        d.setModal(True)
        return d

    @classmethod
    def invoke(cls):
        cls.get_from_exc().exec()

    @property
    def text(self) -> str:
        return self.textMain.toPlainText()

    @text.setter
    def text(self, text: str = None):
        self.textMain.setText(text if text else "")
        self.textMain.verticalScrollBar().setValue(self.textMain.verticalScrollBar().maximum())

    @property
    def details(self) -> str:
        return self.textDetails.toPlainText()

    @details.setter
    def details(self, text: str = None):
        if not text:
            self.toggle_details(False)
            self.buttonDetails.hide()
        self.textDetails.setText(text if text else "")
        self.textDetails.verticalScrollBar().setValue(self.textDetails.verticalScrollBar().maximum())

    def toggle_details(self, expand: bool = None):
        if expand is None:
            expand = self.groupDetails.isHidden()
        self.buttonDetails.setText(f"{'Подробнее'} {'-' if expand else '+'}")
        self.groupDetails.setHidden(not expand)
        self.textDetails.verticalScrollBar().setValue(self.textDetails.verticalScrollBar().maximum())
        self.adjustSize()
