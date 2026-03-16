from .input import Input

from .. import open_login_page
from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def sign_in(
  s: requests.Session,
  open_login_page_output: open_login_page.Output,
  username: str,
  password: str
) -> Output:
  input = Input(open_login_page_output, username, password)
  response = send_request(s, input)
  return parse_response(response, input)