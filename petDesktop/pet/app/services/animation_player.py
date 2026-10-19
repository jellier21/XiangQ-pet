"""Timer-driven animation playback."""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from app.config import FRAME_INTERVAL_MS, PetState
from app.models.animation import Animation


class AnimationPlayer(QObject):
    """Play a selected animation and return to idle after one-shot states."""

    frame_changed = pyqtSignal(object)
    state_changed = pyqtSignal(object)
    animation_finished = pyqtSignal(object)

    def __init__(self, animations: dict[PetState, Animation], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._animations = animations
        self._state = PetState.IDLE
        self._frame_index = 0
        self._loop_override: bool | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._advance)

    @property
    def state(self) -> PetState:
        return self._state

    def start(self, state: PetState, loop: bool | None = None) -> None:
        """Start or restart a state animation, optionally overriding its loop mode."""
        animation = self._animations[state]
        self._state = state
        self._frame_index = 0
        self._loop_override = loop
        self.frame_changed.emit(animation.frames[0])
        self.state_changed.emit(state)
        self._timer.start()

    def _advance(self) -> None:
        animation = self._animations[self._state]
        next_index = self._frame_index + 1

        if next_index < animation.frame_count:
            self._frame_index = next_index
            self.frame_changed.emit(animation.frames[self._frame_index])
            return

        should_loop = animation.loop if self._loop_override is None else self._loop_override
        if should_loop:
            self._frame_index = 0
            self.frame_changed.emit(animation.frames[0])
            return

        self.animation_finished.emit(self._state)
        self.start(PetState.IDLE)
