from requests import Response
from requests.sessions import RequestsCookieJar
from requests.exceptions import JSONDecodeError

from scrape.log import log_post_json
from .build_request import Request
from scrape.scrape_error import JsonError
from dataclasses import dataclass

@dataclass
class Output:
  course_number_options: list[str]

def parse_response(request: Request, res: Response, cookies: RequestsCookieJar) -> Output:
  try:
    res_json = res.json()
    log_post_json(
      url=request.url,
      headers=request.headers,
      form_data=request.form_data,
      res=res,
      cookies=cookies,
      res_json=res_json,
    )
  except JSONDecodeError as e:
    log_post_json(
      url=request.url,
      headers=request.headers,
      form_data=request.form_data,
      res=res,
      cookies=cookies,
      res_json=None,
    )
    raise JsonError(e)
  options: list[str] = []
  for x in res_json["values"]:
    option = x["d"]
    if option is None:
      option = x["r"]
    options.append(option)
  
  return Output(course_number_options=options)

