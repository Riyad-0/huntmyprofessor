from abc import abstractmethod
from dataclasses import dataclass
from typing import override

import requests

class ScrapeError(Exception):
  @abstractmethod
  def message(self) -> str:
    raise NotImplementedError()

@dataclass
class JsonError(ScrapeError):
  e: requests.exceptions.JSONDecodeError

  @override
  def message(self) -> str:
    return "unable to decode json response, got exception:\n" + self.e.msg
