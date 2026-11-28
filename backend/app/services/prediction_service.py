import math

from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository
from app.machine_learning.model_service import MealDemandModel
from app.domain.exceptions.business_error import BusinessError


class PredictionService:
    def __init__(self, repository=None, model=None):
        self.repository = repository or MySQLMealRepository()
        self.model = model or MealDemandModel()

    def predict(self, request):
       
        enrollment = self.repository.get_active_enrollment(
            request.school_id,
            request.shift
        )

        if enrollment <= 0:
            raise BusinessError(
                "Não há alunos matriculados neste turno."
            )

        students = request.students_reference

        if students is not None:
            if students < 0:
                raise BusinessError(
                    "A quantidade de alunos não pode ser negativa."
                )
            attendance_source = "informado_pelo_gestor"

        else:
            
            attendance = self.model.predict_attendance(
                target_date=request.target_date,
                shift=request.shift,
                expected_students=enrollment
            )

            students = attendance["alunos_estimados"]
            attendance_source = "machine_learning"

        history = self.repository.fetch_training_history(
            request.school_id
        )

        if not history:
            raise BusinessError(
                "Não há histórico suficiente para previsão."
            )

        result = self.model.predict(
            history,
            request.target_date,
            request.shift,
            students,
            request.menu_description
        )

        
        meals_estimated = result["refeicoes_estimadas"]
        safety_margin = request.safety_margin

        meals_recommended = math.ceil(
            meals_estimated * (1 + safety_margin / 100)
        )

        
        record = {
            "id_escola": request.school_id,
            "data_prevista": request.target_date,
            "turno": request.shift,
            "alunos_referencia": students,
            "quantidade_prevista": meals_estimated,
            "tipo_previsao": request.prediction_type,
            "modelo_utilizado": result["modelo"],
            "margem_seguranca": safety_margin,
            "refeicoes_recomendadas": meals_recommended
        }
       
        prediction_id = self.repository.save_prediction(record)

        return {
            **record,
            "id_previsao": prediction_id,
            **result,
            "alunos_estimados": students,
            "origem_presenca": attendance_source,
            "margem_seguranca": safety_margin,
            "refeicoes_recomendadas": meals_recommended
        }