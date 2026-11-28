import os
from pathlib import Path
from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(BACKEND_ROOT / ".env")


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Configure uma SECRET_KEY com pelo menos "
        "32 caracteres no arquivo .env."
    )


def load_config():
    return {

        

        "DB_HOST": os.getenv(
            "DB_HOST",
            "127.0.0.1"
        ),

        "DB_PORT": int(
            os.getenv("DB_PORT", "3306")
        ),

        "DB_USER": os.getenv(
            "DB_USER",
            "root"
        ),

        "DB_PASSWORD": os.getenv(
            "DB_PASSWORD",
            ""
        ),

        "DB_NAME": os.getenv(
            "DB_NAME",
            "alimenta_escola"
        ),

       

        "FLASK_HOST": os.getenv(
            "FLASK_HOST",
            "127.0.0.1"
        ),

        "FLASK_PORT": int(
            os.getenv("FLASK_PORT", "5000")
        ),

        "FLASK_DEBUG": os.getenv(
            "FLASK_DEBUG",
            "false"
        ).lower() == "true",

      

        "CORS_ORIGINS": os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8501"
        ),

       
        "MODELS_DIR": str((
            BACKEND_ROOT / os.getenv(
                "MODELS_DIR",
                "app/machine_learning/models"
            )
        ).resolve()),

      

        "SECRET_KEY": SECRET_KEY,

        "SESSION_COOKIE_HTTPONLY": True,

        "SESSION_COOKIE_SAMESITE": "Lax",

        "SESSION_COOKIE_SECURE": os.getenv(
            "SESSION_COOKIE_SECURE",
            "false"
        ).lower() == "true",

    }