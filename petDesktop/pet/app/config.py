"""Application-wide constants and animation settings."""

from enum import StrEnum


APP_NAME = "桌宠"
FRAME_INTERVAL_MS = 140
WINDOW_MARGIN = 16
REGISTER_URL = "http://127.0.0.1:8080/api/user/register"
# The idle source frames are 404px tall while the action characters are about 200px tall.
IDLE_DISPLAY_SCALE = 0.54


class PetState(StrEnum):
    """Animation states supported by the initial desktop pet."""

    IDLE = "idle"
    GREET = "greet"
    CONSULT = "consult"


STATE_LABELS = {
    PetState.IDLE: "待机",
    PetState.GREET: "打招呼",
    PetState.CONSULT: "查阅",
}
