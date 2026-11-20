
from flask import Blueprint, jsonify, session, current_app, request

from app.services.class_service import ClassService
from app.domain.exceptions.business_error import BusinessError


class_bp = Blueprint("classes", __name__)

service = ClassService()


# LISTAR TURMAS
@class_bp.get("/turmas")
def list_classes():
    school_id = session.get("id_escola")
    user_id = session.get("id_usuario")

    if not user_id or not school_id:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    try:
        classes = service.list_classes(school_id)

        return jsonify({
            "total": len(classes),
            "turmas": classes
        }), 200

    except Exception:
        current_app.logger.exception("Erro ao consultar turmas.")
        return jsonify({"erro": "Erro interno ao consultar turmas."}), 500


# CADASTRAR TURMA
@class_bp.post("/turmas")
def create_class():
    school_id = session.get("id_escola")
    user_id = session.get("id_usuario")

    if not user_id or not school_id:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    try:
        data = request.get_json(silent=True)
        turma = service.create_class(school_id, data)

        return jsonify({
            "mensagem": "Turma cadastrada com sucesso.",
            "turma": turma
        }), 201

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 400

    except Exception:
        current_app.logger.exception("Erro ao cadastrar turma.")
        return jsonify({"erro": "Erro interno ao cadastrar turma."}), 500


# CONSULTAR TURMA PELO ID
@class_bp.get("/turmas/<int:class_id>")
def get_class(class_id):
    school_id = session.get("id_escola")
    user_id = session.get("id_usuario")

    if not user_id or not school_id:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    try:
        turma = service.get_class(school_id, class_id)
        return jsonify(turma), 200

    except BusinessError as error:
        return jsonify({"erro": str(error)}), 404

    except Exception:
        current_app.logger.exception("Erro ao consultar turma.")
        return jsonify({"erro": "Erro interno ao consultar turma."}), 500


# ATUALIZAR TURMA
@class_bp.put("/turmas/<int:class_id>")
def update_class(class_id):
    school_id = session.get("id_escola")
    user_id = session.get("id_usuario")

    if not user_id or not school_id:
        return jsonify({"erro": "Usuário não autenticado."}), 401

    try:
        data = request.get_json(silent=True)

        turma = service.update_class(
            school_id,
            class_id,
            data
        )

        return jsonify({
            "mensagem": "Turma atualizada com sucesso.",
            "turma": turma
        }), 200

    except BusinessError as error:
        mensagem = str(error)
        status = 404 if mensagem == "Turma não encontrada." else 400

        return jsonify({"erro": mensagem}), status

    except Exception:
        current_app.logger.exception("Erro ao atualizar turma.")
        return jsonify({"erro": "Erro interno ao atualizar turma."}), 500

    # ATIVAR OU DESATIVAR TURMA
@class_bp.patch("/turmas/<int:class_id>/status")
def update_class_status(class_id):
    school_id = session.get("id_escola")
    user_id = session.get("id_usuario")

    if not user_id or not school_id:
        return jsonify({
            "erro": "Usuário não autenticado."
        }), 401

    try:
        data = request.get_json(silent=True)

        turma = service.update_class_status(
            school_id,
            class_id,
            data
        )

        return jsonify({
            "mensagem": "Status da turma atualizado com sucesso.",
            "turma": turma
        }), 200

    except BusinessError as error:
        mensagem = str(error)

        status = 404 if mensagem == "Turma não encontrada." else 400

        return jsonify({
            "erro": mensagem
        }), status

    except Exception:
        current_app.logger.exception(
            "Erro ao atualizar status da turma."
        )

        return jsonify({
            "erro": "Erro interno ao atualizar status da turma."
        }), 500

    
