from app.repositories.mysql.mysql_meal_repository import MySQLMealRepository


class HistoryService:

    def __init__(self, repository=None):
        self.repository = repository or MySQLMealRepository()

    def get_history(self, school_id=None):
        return self.repository.fetch_training_history(school_id)

    def get_indicators(self, school_id=None):
        rows = self.get_history(school_id)

        prepared = sum(
            float(r.get("refeicoes_preparadas") or 0)
            for r in rows
        )

        served = sum(
            float(r.get("refeicoes_servidas") or 0)
            for r in rows
        )

        leftovers = sum(
            float(r.get("sobras") or 0)
            for r in rows
        )

        return {
            "registros": len(rows),
            "total_refeicoes_preparadas": prepared,
            "total_refeicoes_servidas": served,
            "total_sobras": leftovers,
            "percentual_sobras_sobre_preparadas": (
                round(leftovers / prepared * 100, 2)
                if prepared else None
            ),
        }

    def get_predictions_history(self, school_id):
        return self.repository.get_predictions_history(school_id)

