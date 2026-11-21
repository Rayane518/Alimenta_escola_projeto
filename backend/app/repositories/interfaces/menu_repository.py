
from abc import ABC, abstractmethod


class MenuRepository(ABC):

    @abstractmethod
    def save_menu(self, menu):
        raise NotImplementedError

    @abstractmethod
    def get_menus(self, school_id, target_date=None):
        raise NotImplementedError
