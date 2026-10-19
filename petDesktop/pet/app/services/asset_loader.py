"""Load and validate desktop pet frame assets."""

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap

from app.config import IDLE_DISPLAY_SCALE, PetState
from app.models.animation import Animation, AnimationSource


class AssetLoadError(RuntimeError):
    """Raised when a required animation asset cannot be loaded."""


class AssetLoader:
    """Load ordered PNG frames from the project's assets directory."""

    def __init__(self, assets_root: Path) -> None:
        self.assets_root = assets_root

    def load_animations(self) -> dict[PetState, Animation]:
        """Load all initial states and return them keyed by state."""
        sources = (
            AnimationSource(
                PetState.IDLE,
                self.assets_root / "idle",
                loop=True,
                scale=IDLE_DISPLAY_SCALE,
            ),
            AnimationSource(PetState.GREET, self.assets_root / "greet", loop=False),
            AnimationSource(PetState.CONSULT, self.assets_root / "consult", loop=False),
        )
        return {source.state: self._load_animation(source) for source in sources}

    def _load_animation(self, source: AnimationSource) -> Animation:
        if not source.directory.is_dir():
            raise AssetLoadError(f"Animation directory does not exist: {source.directory}")

        frame_paths = sorted(source.directory.glob("*.png"), key=lambda path: path.name.lower())
        if not frame_paths:
            raise AssetLoadError(f"No PNG frames found in: {source.directory}")

        frames: list[QPixmap] = []
        for frame_path in frame_paths:
            pixmap = QPixmap(str(frame_path))
            if pixmap.isNull():
                raise AssetLoadError(f"Unable to load frame: {frame_path}")
            pixmap = self._scale_frame(pixmap, source.scale)
            frames.append(pixmap)

        return Animation(state=source.state, frames=tuple(frames), loop=source.loop)

    @staticmethod
    def _scale_frame(pixmap: QPixmap, scale: float) -> QPixmap:
        """Scale a complete frame while preserving its transparent composition."""
        if scale == 1.0:
            return pixmap

        target_size = QSize(
            round(pixmap.width() * scale),
            round(pixmap.height() * scale),
        )
        return pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
