'''Base endpoint class'''
from abc import ABC, abstractmethod

class LogsEndpoint(ABC):

    @abstractmethod
    def nba_stats(self):
        pass

    @abstractmethod
    def bball_ref(self):
        pass

class StatsEndpoint(ABC):

    @abstractmethod
    def nba_stats(self):
        pass

    @abstractmethod
    def bball_ref(self):
        pass

    @abstractmethod
    def get_processed_logs(self):
        pass
