from abc import abstractmethod
from dataclasses import dataclass
from json import JSONDecodeError
from typing import override

class ScrapeError(Exception):
  @abstractmethod
  def message(self) -> str:
    raise NotImplementedError()

@dataclass
class JsonError(ScrapeError):
  e: JSONDecodeError

  @override
  def message(self) -> str:
    return "unable to decode json response, got exception:\n" + self.e.msg
