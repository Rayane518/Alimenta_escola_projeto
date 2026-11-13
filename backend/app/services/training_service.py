from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository
from app.machine_learning.model_service import MealDemandModel

class TrainingService:
    def __init__(self, repository=None, model=None):
        self.repository = repository or MySQLMealRepository()
        self.model = model or MealDemandModel()

    def train(self, school_id=None):
        history = self.repository.fetch_training_history(school_id)
        return self.model.train(history)
