import abc

class Notification(abc.ABC):
    @abc.abstractmethod
    def notify(self, **kwargs):
        pass
