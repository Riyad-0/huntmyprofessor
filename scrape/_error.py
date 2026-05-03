from abc import abstractmethod
from dataclasses import dataclass

@dataclass
class MyError(Exception):
  @abstractmethod
  def message(self) -> str:
    raise NotImplementedError()