from .input import Input

from .. import sign_in
from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def open_course_search_page(
  s: requests.Session,
  sign_in_output: sign_in.Output,
) -> Output:
  input = Input.from_sign_in(output=sign_in_output)
  response = send_request(s, input)
  return parse_response(response)