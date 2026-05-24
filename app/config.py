import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def database_url():
    configured = os.environ.get("DATABASE_URL")
    if not configured:
        return f"sqlite:///{BASE_DIR / 'instance' / 'gift_studio.sqlite'}"
    if configured.startswith("postgres://"):
        return configured.replace("postgres://", "postgresql://", 1)
    if configured.startswith("sqlite:///") and not configured.startswith("sqlite:////"):
        relative_path = configured.replace("sqlite:///", "", 1)
        return f"sqlite:///{BASE_DIR / relative_path}"
    return configured


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    AUTO_CREATE_DB = os.environ.get("AUTO_CREATE_DB", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}
    ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "m4a"}
    ALLOWED_MEDIA_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS

    @classmethod
    def init_app(cls, app):
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "instance").mkdir(parents=True, exist_ok=True)
        if not cls.SECRET_KEY:
            app.logger.warning("SECRET_KEY is not set. Set it in .env before production.")


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    AUTO_CREATE_DB = False


class DevelopmentConfig(Config):
    AUTO_CREATE_DB = os.environ.get("AUTO_CREATE_DB", "true").lower() == "true"


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AUTO_CREATE_DB = True
