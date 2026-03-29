from .input import Input

from .. import sign_in
from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def professor_search(
  s: requests.Session,
  sign_in_output: sign_in.Output,
  search_text: str
) -> Output:
  input = Input.from_sign_in(output=sign_in_output, search_text=search_text)
  response = send_request(s, input)
  return parse_response(response, input)