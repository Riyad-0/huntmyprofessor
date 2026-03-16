from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def open_login_page(s: requests.Session) -> Output:
  response = send_request(s)
  return parse_response(response)
