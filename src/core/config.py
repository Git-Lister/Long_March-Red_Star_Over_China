"""Game configuration constants."""


class Config:
    DATA_PATH: str = "data/"
    SAVE_PATH: str = "saves/"
    ASSETS_PATH: str = "assets/"
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 720
    FPS: int = 60

    STRATEGIC_TIME_SCALE: int = 60
    EVENT_TIME_SCALE: int = 1

    BASE_SPEED_KMPH: float = 4.0
    DAILY_RICE_KG_PER_PERSON: float = 0.6

    # AI Settings
    AI_BACKEND: str = "ollama"  # "ollama" or "llama_cpp" (future)
    OLLAMA_MODEL: str = (
        "llama3:8b-instruct-q4_K_M"  # exactly as listed in `ollama list`
    )
    OLLAMA_HOST: str = "http://localhost:11434"
    USE_AI: bool = True
    AI_MAX_TOKENS: int = 256

    COMBAT_DICE_SIDES: int = 20
