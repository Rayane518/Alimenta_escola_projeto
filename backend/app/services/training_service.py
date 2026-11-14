from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository
from app.machine_learning.model_service import MealDemandModel


class TrainingService:
    def __init__(self, repository=None, model=None):
        self.repository = repository or MySQLMealRepository()
        self.model = model or MealDemandModel()

    def train(self, school_id=None):
        # Buscar histórico da escola no MySQL
        history = self.repository.fetch_training_history(school_id)

        # Treinar o modelo de presença
        resultado_presenca = self.model.train_attendance(history)

        # Treinar o modelo de refeições
        resultado_refeicoes = self.model.train(history)

        # Retornar os resultados dos dois treinamentos
        return {
            "status": "treinado",
            "escola": school_id,
            "modelo_presenca": resultado_presenca,
            "modelo_refeicoes": resultado_refeicoes
        }
