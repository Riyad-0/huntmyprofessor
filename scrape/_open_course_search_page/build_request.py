import json
import os

headers_file_path = os.path.join(os.path.dirname(__file__), "request_headers.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

url = "https://orapp.hunter.cuny.edu/ords/f?p=116:6"
partial_headers = parse_headers()

class Request:
  def __init__(
    self,
    url: str,
    headers: dict[str, str],
  ):
    self.url = url
    self.headers = headers

def build_request(cookie: str):
  return Request(
    url=url,
    headers=partial_headers | {
      "Cookie": cookie
    }
  )