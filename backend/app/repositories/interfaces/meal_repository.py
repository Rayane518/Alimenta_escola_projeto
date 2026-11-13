from abc import ABC, abstractmethod

class MealRepository(ABC):
    @abstractmethod
    def fetch_training_history(self, school_id=None):
        raise NotImplementedError

    @abstractmethod
    def get_active_enrollment(self, school_id, shift):
        raise NotImplementedError

    @abstractmethod
    def get_attendance_rate(self, school_id, shift):
        raise NotImplementedError

    @abstractmethod
    def save_prediction(self, prediction):
        raise NotImplementedError
