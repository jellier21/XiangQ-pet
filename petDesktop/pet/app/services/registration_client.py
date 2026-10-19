"""Asynchronous user registration client."""

import json
from typing import Any

from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtNetwork import (
    QHttpMultiPart,
    QHttpPart,
    QNetworkAccessManager,
    QNetworkReply,
    QNetworkRequest,
)

from app.config import REGISTER_URL
from app.models.auth import AuthProfile


class RegistrationClient(QObject):
    """Submit the first-launch name without blocking the Qt event loop."""

    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._manager = QNetworkAccessManager(self)
        self._reply: QNetworkReply | None = None

    def register(self, name: str) -> None:
        """POST the user's name as multipart/form-data."""
        if self._reply is not None:
            self.failed.emit("注册请求正在进行中，请稍候")
            return

        part = QHttpPart()
        part.setHeader(
            QNetworkRequest.KnownHeaders.ContentDispositionHeader,
            'form-data; name="name"',
        )
        part.setBody(name.encode("utf-8"))

        multipart = QHttpMultiPart(QHttpMultiPart.ContentType.FormDataType)
        multipart.append(part)

        request = QNetworkRequest(QUrl(REGISTER_URL))
        self._reply = self._manager.post(request, multipart)
        multipart.setParent(self._reply)
        self._reply.finished.connect(self._handle_finished)

    def _handle_finished(self) -> None:
        reply = self._reply
        self._reply = None
        if reply is None:
            return

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                raise ValueError(reply.errorString() or "注册请求失败")

            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if isinstance(status, int) and not 200 <= status < 300:
                raise ValueError(f"注册接口返回 HTTP {status}")

            payload: Any = json.loads(bytes(reply.readAll()).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("注册接口返回格式无效")
            self.succeeded.emit(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self.failed.emit(str(error))
        finally:
            reply.deleteLater()
