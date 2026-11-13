import os
from pathlib import Path
from dotenv import load_dotenv

# .env fica na raiz backend/, um nível acima da pasta app/.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


def load_config():
    return {
        "DB_HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "DB_PORT": int(os.getenv("DB_PORT", "3306")),
        "DB_USER": os.getenv("DB_USER", "root"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "DB_NAME": os.getenv("DB_NAME", "alimenta_escola"),
        "FLASK_HOST": os.getenv("FLASK_HOST", "127.0.0.1"),
        "FLASK_PORT": int(os.getenv("FLASK_PORT", "5000")),
        "FLASK_DEBUG": os.getenv("FLASK_DEBUG", "true").lower() == "true",
        "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "*"),
        "MODEL_PATH": str((BACKEND_ROOT / os.getenv("MODEL_PATH", "app/machine_learning/models/modelo_merenda.joblib")).resolve()),
    }
