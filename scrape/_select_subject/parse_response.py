from httpx import Cookies, Response
from json import JSONDecodeError

from .build_request import Request
from scrape._json_error import JsonError
from dataclasses import dataclass

@dataclass
class Output:
  course_number_options: list[str]

def parse_response(request: Request, res: Response, cookies: Cookies) -> Output:
  try:
    res_json = res.json()
  except JSONDecodeError as e:
    raise JsonError(e, res=res, cookies=cookies)
  options: list[str] = []
  for x in res_json["values"]:
    option = x["d"]
    if option is None:
      option = x["r"]
    options.append(option)
  
  return Output(course_number_options=options)

