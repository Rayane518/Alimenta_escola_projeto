
from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository


class HistoryService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLMealRepository()

    def get_history(self, school_id=None):
        return self.repository.fetch_training_history(school_id)

    def get_indicators(self, school_id=None):
        return self.repository.get_meal_indicators(school_id)

    def get_predictions_history(self, school_id):
        return self.repository.get_predictions_history(school_id)
