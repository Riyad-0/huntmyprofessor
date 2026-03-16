from abc import abstractmethod

class ScrapeError(Exception):
  @abstractmethod
  def message(self) -> str:
    raise NotImplementedError()