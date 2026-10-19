"""Animation data structures."""

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtGui import QPixmap

from app.config import PetState


@dataclass(frozen=True, slots=True)
class Animation:
    """A preloaded animation and the state it represents."""

    state: PetState
    frames: tuple[QPixmap, ...]
    loop: bool = False

    @property
    def frame_count(self) -> int:
        return len(self.frames)


@dataclass(frozen=True, slots=True)
class AnimationSource:
    """A state-to-directory mapping used while loading frame assets."""

    state: PetState
    directory: Path
    loop: bool
    scale: float = 1.0
