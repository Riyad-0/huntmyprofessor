import json
import os
from typing import Any
from pathlib import Path
import requests;
from requests.sessions import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

dir_name = os.path.dirname(__file__)
log_file_path = os.path.join(dir_name, "log.json")

def clear_log():
  Path(log_file_path).unlink(missing_ok=True)

def read_log() -> Any:
  try:
    with open(log_file_path) as log_file:
      text = log_file.read()
      if text.strip() == "":
        return []
      return json.loads(text)
  except FileNotFoundError:
    return []

def log_get(res: requests.Response, cookies: RequestsCookieJar):
  data = read_log()
  data.append({
    "url": res.request.url,
    "headers": res.request.headers,
    "cookies": cookies,
    "res": [res.text],
  })
  with open(log_file_path, "w") as log_file:
    json.dump(data, log_file, indent=2, default=serialize_default)

def log_post(res: requests.Response, cookies: RequestsCookieJar):
  data = read_log()
  data.append({
    "url": res.request.url,
    "headers": res.request.headers,
    "body": res.request.body,
    "cookies": cookies,
    "res": [res.text],
  })
  with open(log_file_path, "w") as log_file:
    json.dump(data, log_file, indent=2, default=serialize_default)

def serialize_default(x: Any):
  if isinstance(x, CaseInsensitiveDict) or isinstance(x, RequestsCookieJar):
    return dict(x)
  raise TypeError(f"Object of type {type(x).__name__} is not JSON serializable")

def log(s: str):
  with open(log_file_path, "w") as log_file:
    log_file.write(s)

def log_to(file_name: str, s: str):
  file_path = rel_path(file_name)
  with open(file_path, "w") as log_file:
    log_file.write(s)

def rel_path(file_name: str) -> str:
  return os.path.join(dir_name, file_name)
