from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository
from app.machine_learning.model_service import MealDemandModel
from app.domain.exceptions.business_error import BusinessError

class PredictionService:
    def __init__(self, repository=None, model=None):
        self.repository = repository or MySQLMealRepository()
        self.model = model or MealDemandModel()

    def predict(self, request):
        students = request.students_reference
        if students is None:
            enrollment = self.repository.get_active_enrollment(request.school_id, request.shift)
            if enrollment <= 0:
                raise BusinessError("Não há turmas ativas com alunos cadastrados para esse turno.")
            rate = self.repository.get_attendance_rate(request.school_id, request.shift)
            # Sem histórico de presença, usa a matrícula ativa como estimativa conservadora.
            students = round(enrollment * rate) if rate is not None else enrollment
        if students < 0:
            raise BusinessError("A quantidade de alunos não pode ser negativa.")

        history = self.repository.fetch_training_history(request.school_id)
        if not history:
            raise BusinessError("Ainda não há histórico de merenda e presença suficiente para estimar a demanda.")
        result = self.model.predict(history, request.target_date, request.shift, students, request.menu_description)
        record = {
            "id_escola": request.school_id,
            "data_prevista": request.target_date,
            "turno": request.shift,
            "alunos_referencia": students,
            "quantidade_prevista": result["refeicoes_estimadas"],
            "tipo_previsao": request.prediction_type,
            "modelo_utilizado": result["modelo"],
        }
        prediction_id = self.repository.save_prediction(record)
        return {**record, "id_previsao": prediction_id, **result, "alunos_referencia": students}
