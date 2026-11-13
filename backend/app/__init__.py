from flask import Flask, jsonify
from flask_cors import CORS

from app.controllers.health_controller import health_bp
from app.controllers.history_controller import history_bp
from app.controllers.prediction_controller import prediction_bp
from app.controllers.training_controller import training_bp
from app.infrastructure.config import load_config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(load_config())
    if test_config:
        app.config.update(test_config)

    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, origins=origins.split(",") if isinstance(origins, str) and origins != "*" else origins)

    app.register_blueprint(health_bp)
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(prediction_bp, url_prefix="/api")
    app.register_blueprint(training_bp, url_prefix="/api")

    @app.get("/sobre")
    def about():
        return jsonify({"projeto": "Alimenta Escola", "objetivo": "Apoiar o planejamento da merenda escolar."})

    @app.get("/objetivo")
    def objective():
        return jsonify({"objetivo": "Estimar a demanda de refeições por escola, data e turno, apoiando o planejamento e a redução de desperdício."})

    @app.get("/")
    def index():
        return jsonify({"sistema": "Alimenta Escola", "status": "online"})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"erro": "Rota não encontrada"}), 404

    return app
