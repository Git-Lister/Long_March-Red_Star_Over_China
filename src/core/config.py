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

    LLM_MODEL_PATH: str = "models/llama-3-8b-q4.gguf"
    USE_AI: bool = True
    AI_MAX_TOKENS: int = 256

    COMBAT_DICE_SIDES: int = 20

