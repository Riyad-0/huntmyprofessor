import json
import os

from .input import Input;

headers_file_path = os.path.join(os.path.dirname(__file__), "requestHeaders.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

partial_url = "https://orapp.hunter.cuny.edu/ords/f?p=116:6:"
url_suffix = ":::::"
partial_headers = parse_headers()

class Request:
  def __init__(
    self,
    url: str,
    headers: dict[str, str],
  ):
    self.url = url
    self.headers = headers

def build_request(input: Input):
  cookie = input.cookie
  p_instance = input.p_instance
  return Request(
    url=partial_url + p_instance + url_suffix,
    headers=partial_headers | {
      "Cookie": cookie
    }
  )