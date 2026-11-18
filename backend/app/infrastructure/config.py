import os
from pathlib import Path
from dotenv import load_dotenv

# LOCALIZAÇÃO DA PASTA BACKEND

BACKEND_ROOT = Path(__file__).resolve().parents[2]

# CARREGAMENTO DAS VARIÁVEIS .ENV


load_dotenv(BACKEND_ROOT / ".env")

# VALIDAÇÃO DA CHAVE DE SEGURANÇA

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "Configure uma SECRET_KEY com pelo menos "
        "32 caracteres no arquivo .env."
    )


def load_config():
    return {
        # BANCO DE DADOS MYSQL

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

        # CONFIGURAÇÕES DO FLASK

        "FLASK_HOST": os.getenv(
            "FLASK_HOST",
            "127.0.0.1"
        ),

        "FLASK_PORT": int(
            os.getenv("FLASK_PORT", "5000")
        ),

        "FLASK_DEBUG": os.getenv(
            "FLASK_DEBUG",
            "true"
        ).lower() == "true",

        # COMUNICAÇÃO COM REACT

        "CORS_ORIGINS": os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173"
        ),

        # MACHINE LEARNING

        "MODEL_PATH": str((
            BACKEND_ROOT / os.getenv(
                "MODEL_PATH",
                "app/machine_learning/models/modelo_merenda.joblib"
            )
        ).resolve()),

        # AUTENTICAÇÃO E SESSÃO

        "SECRET_KEY": SECRET_KEY,

        # Impede que JavaScript leia o cookie
        "SESSION_COOKIE_HTTPONLY": True,

        # Permite cookies em requisições same-site
        "SESSION_COOKIE_SAMESITE": "Lax",

        # False somente para desenvolvimento HTTP local
        "SESSION_COOKIE_SECURE": False,

    }
