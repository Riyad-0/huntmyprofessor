from .input import Input

from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def open_eval_report(
  s: requests.Session,
  cookie: str,
  url: str,
) -> Output:
  input = Input(cookie=cookie, url=url)
  response = send_request(s, input)
  return parse_response(response)