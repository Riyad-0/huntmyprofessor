import json
import os
from typing import Any
from pathlib import Path
import requests
from requests.sessions import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from urllib.parse import parse_qs

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

def log_get(
  url: str,
  headers: dict[str, str],
  res: requests.Response,
  cookies: RequestsCookieJar,
):
  data = read_log()
  data.append({
    "my-url": url,
    "my-headers": headers,
    "url": res.request.url,
    "headers": res.request.headers,
    "cookies": cookies,
    "res": [res.text],
  })
  with open(log_file_path, "w") as log_file:
    json.dump(data, log_file, indent=2, default=serialize_default)

def log_post(
  url: str,
  headers: dict[str, str],
  form_data: dict[str, str],
  res: requests.Response,
  cookies: RequestsCookieJar
):
  if isinstance(res.request.body, str):    
    parsed_body = parse_qs(res.request.body)
    parsed_body = {k: v[0] for k, v in parsed_body.items()}
  else:
    parsed_body = res.request.body
  data = read_log()
  data.append({
    "my-url": url,
    "my-headers": headers,
    "my-form-data": form_data,
    "url": res.request.url,
    "headers": res.request.headers,
    "raw-body": res.request.body,
    "body": parsed_body,
    "cookies": cookies,
    "res": [res.text],
  })
  with open(log_file_path, "w") as log_file:
    json.dump(data, log_file, indent=2, default=serialize_default)

def log_post_json(
  url: str,
  headers: dict[str, str],
  form_data: dict[str, str],
  res: requests.Response,
  cookies: RequestsCookieJar,
  res_json: Any,
):
  if isinstance(res.request.body, str):    
    parsed_body = parse_qs(res.request.body)
    parsed_body = {k: v[0] for k, v in parsed_body.items()}
  else:
    parsed_body = res.request.body
  data = read_log()
  data.append({
    "my-url": url,
    "my-headers": headers,
    "my-form-data": form_data,
    "url": res.request.url,
    "headers": res.request.headers,
    "raw-body": res.request.body,
    "body": parsed_body,
    "cookies": cookies,
    "res": [res.text],
    "res_json": res_json,
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
