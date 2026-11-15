from flask import Flask, jsonify
from flask_cors import CORS

from app.controllers.health_controller import health_bp
from app.controllers.history_controller import history_bp
from app.controllers.prediction_controller import prediction_bp
from app.controllers.training_controller import training_bp
from app.controllers.auth_controller import auth_bp

from app.infrastructure.config import load_config


def create_app(test_config=None):
    app = Flask(__name__)

    # Carregar as configurações do sistema
    app.config.update(load_config())

    if test_config:
        app.config.update(test_config)

    # Configurar CORS para o frontend React
    origins = app.config.get(
        "CORS_ORIGINS",
        "http://localhost:5173"
    )

    if isinstance(origins, str):
        allowed_origins = [
            origin.strip()
            for origin in origins.split(",")
            if origin.strip()
        ]
    else:
        allowed_origins = origins

    # Não permitir origem curinga com cookies
    if not allowed_origins or "*" in allowed_origins:
        raise ValueError(
            "Configure CORS_ORIGINS com as origens permitidas."
        )

    CORS(
        app,
        origins=allowed_origins,
        supports_credentials=True
    )

    # Registrar os controllers
    app.register_blueprint(health_bp)
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(prediction_bp, url_prefix="/api")
    app.register_blueprint(training_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")

    # Verificar se o backend está online
    @app.get("/")
    def index():
        return jsonify({
            "sistema": "Alimenta Escola",
            "status": "online"
        })

    # Tratar rotas inexistentes
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({
            "erro": "Rota não encontrada"
        }), 404

    return app