from dataclasses import dataclass
from json import JSONDecodeError
from typing import override

from httpx import Cookies, Response

from scrape._error import MyError


@dataclass
class JsonError(MyError):
  e: JSONDecodeError
  res: Response
  cookies: Cookies

  @override
  def message(self):
    return 'error: unable to decode json response, got exception:\n' + self.e.msg
