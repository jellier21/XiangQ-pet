"""Frameless, draggable desktop pet window and first-launch onboarding UI."""

from pathlib import Path

from PyQt6.QtCore import QPoint, QTimer, Qt
from PyQt6.QtGui import QAction, QContextMenuEvent, QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_NAME, PetState, STATE_LABELS, WINDOW_MARGIN
from app.models.auth import AuthProfile
from app.services.animation_player import AnimationPlayer
from app.services.asset_loader import AssetLoader
from app.services.auth_store import AuthStore
from app.services.registration_client import RegistrationClient


class PetWindow(QWidget):
    """Display the pet without a native window frame or background."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_offset: QPoint | None = None
        self._first_launch = False
        self._pending_name = ""

        self._label = QLabel(self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._speech_label = QLabel(self)
        self._speech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._speech_label.setWordWrap(True)
        self._speech_label.setStyleSheet(
            "QLabel {"
            " background: #fffdf7;"
            " border: 1px solid #d9c9b8;"
            " border-radius: 10px;"
            " color: #4a3b32;"
            " font-size: 14px;"
            " padding: 8px 12px;"
            "}"
        )
        self._speech_label.setMinimumWidth(230)
        self._speech_label.hide()

        self._name_input = QLineEdit(self)
        self._name_input.setPlaceholderText("请输入你的名字")
        self._name_input.setClearButtonEnabled(True)
        self._name_input.setMinimumWidth(180)
        self._name_input.returnPressed.connect(self._submit_name)

        self._confirm_button = QPushButton("确定", self)
        self._confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._confirm_button.clicked.connect(self._submit_name)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)
        input_layout.addWidget(self._name_input)
        input_layout.addWidget(self._confirm_button)

        self._input_panel = QWidget(self)
        self._input_panel.setLayout(input_layout)
        self._input_panel.hide()

        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        content_layout.addWidget(self._speech_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self._input_panel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet("background: transparent;")

        project_root = Path(__file__).resolve().parents[2]
        assets_root = project_root / "assets"
        self._auth_store = AuthStore(project_root / "config" / "auth.json")
        self._registration_client = RegistrationClient(self)
        self._registration_client.succeeded.connect(self._registration_succeeded)
        self._registration_client.failed.connect(self._registration_failed)

        animations = AssetLoader(assets_root).load_animations()
        self._player = AnimationPlayer(animations, self)
        self._player.frame_changed.connect(self._show_frame)
        self._player.animation_finished.connect(self._animation_finished)
        self._player.start(PetState.IDLE)

        self._place_on_screen()
        if self._auth_store.load() is None:
            self._first_launch = True
            QTimer.singleShot(0, lambda: self._player.start(PetState.GREET))

    def _show_frame(self, pixmap: QPixmap) -> None:
        self._label.setPixmap(pixmap)
        self._label.setFixedSize(pixmap.size())
        self.adjustSize()

    def _place_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        self.move(
            available.right() - self.width() - WINDOW_MARGIN,
            available.bottom() - self.height() - WINDOW_MARGIN,
        )

    def _animation_finished(self, state: PetState) -> None:
        if self._first_launch and state == PetState.GREET:
            self._show_onboarding()

    def _show_onboarding(self) -> None:
        self._speech_label.setText("你好，我是你的桌宠！\n请问你叫什么名字？")
        self._speech_label.show()
        self._input_panel.show()
        self._name_input.setFocus()
        self._keep_bottom_right_after_resize()

    def _keep_bottom_right_after_resize(self) -> None:
        old_bottom_right = self.frameGeometry().bottomRight()
        self.adjustSize()
        self.move(
            old_bottom_right.x() - self.width() + 1,
            old_bottom_right.y() - self.height() + 1,
        )

    def _submit_name(self) -> None:
        name = self._name_input.text().strip()
        if not name:
            self._speech_label.setText("请先输入你的名字，再点击确定。")
            self._name_input.setFocus()
            return

        self._pending_name = name
        self._name_input.setEnabled(False)
        self._confirm_button.setEnabled(False)
        self._speech_label.setText("我正在查阅资料，请稍候……")
        self._player.start(PetState.CONSULT, loop=True)
        self._registration_client.register(name)

    def _registration_succeeded(self, payload: object) -> None:
        try:
            if not isinstance(payload, dict):
                raise ValueError("注册接口返回格式无效")
            profile = AuthProfile.from_mapping(payload, self._pending_name)
            self._auth_store.save(profile)
        except (OSError, ValueError) as error:
            self._registration_failed(str(error))
            return

        self._first_launch = False
        self._pending_name = ""
        self._speech_label.hide()
        self._input_panel.hide()
        self._player.start(PetState.IDLE)
        self._keep_bottom_right_after_resize()

    def _registration_failed(self, message: str) -> None:
        self._player.start(PetState.IDLE)
        self._name_input.setEnabled(True)
        self._confirm_button.setEnabled(True)
        self._speech_label.setText(f"注册失败：{message}\n请检查服务后重试。")
        self._name_input.setFocus()
        self._keep_bottom_right_after_resize()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        greet_action = QAction(STATE_LABELS[PetState.GREET], self)
        consult_action = QAction(STATE_LABELS[PetState.CONSULT], self)
        exit_action = QAction("退出桌宠", self)

        greet_action.triggered.connect(lambda: self._player.start(PetState.GREET))
        consult_action.triggered.connect(lambda: self._player.start(PetState.CONSULT))
        exit_action.triggered.connect(self.close)

        menu.addAction(greet_action)
        menu.addAction(consult_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
