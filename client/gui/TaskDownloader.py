from io import StringIO

from PySide6.QtCore import Signal, QObject
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from common.TaskBatch import read_task_batch


class TaskDownloader(QObject):
    updated = Signal()
    # HEADERS = {
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     "accept-language": "ru",
    #     "cache-control": "no-cache",
    #     "pragma": "no-cache",
    #     "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Opera GX\";v=\"102\"",
    #     "sec-ch-ua-arch": "\"x86\"",
    #     "sec-ch-ua-bitness": "\"64\"",
    #     "sec-ch-ua-full-version-list": "\"Chromium\";v=\"116.0.5845.180\", \"Not)A;Brand\";v=\"24.0.0.0\", \"Opera GX\";v=\"102.0.4880.55\"",
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-model": "\"\"",
    #     "sec-ch-ua-platform": "\"Windows\"",
    #     "sec-ch-ua-platform-version": "\"15.0.0\"",
    #     "sec-ch-ua-wow64": "?0",
    #     "sec-fetch-dest": "document",
    #     "sec-fetch-mode": "navigate",
    #     "sec-fetch-site": "none",
    #     "sec-fetch-user": "?1",
    #     "upgrade-insecure-requests": "1",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x65) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.180 Safari/537.36"
    # }

    def __init__(self):
        super().__init__()
        self._src = None

        self._manager = QNetworkAccessManager()
        self._manager.finished.connect(self._finished)

        self._task_batch = None

    @property
    def task_batch(self):
        return self._task_batch

    def set_source(self, src: str):
        self._src = src

    def update_tasks(self):
        if not self._src:
            raise RuntimeError(f"{self} tasks source not set during update.")
        r = QNetworkRequest(f"https://docs.google.com/spreadsheets/d/{self._src}/export?format=csv")
        # for k, v in self.HEADERS.items():
        #     r.setRawHeader(k.encode('utf-8'), v.encode('utf-8'))
        self._manager.get(r)

    def _finished(self, resp: QNetworkReply):
        if resp.error() != resp.NetworkError.NoError:
            raise RuntimeError(f"Не удалось загрузить задание: {resp.errorString()}")
        else:
            data = resp.readAll()
            io = StringIO(bytes(data).decode('utf-8'))
            self._task_batch = read_task_batch(io, delimiter=',')
            self.updated.emit()
