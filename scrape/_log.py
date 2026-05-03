# import json
# import os
# from typing import Any
# from pathlib import Path
# from httpx import Cookies, Response
# from urllib.parse import parse_qs
import logging
from urllib.parse import parse_qs

from httpx import URL, Cookies, Headers, Response
# from logging import FileHandler, Formatter, StreamHandler

log = logging.getLogger("huntmyprofessor")

# def _init():
#   formatter = Formatter('%(asctime)s %(levelname)s %(message)s')
#   file_handler = FileHandler(filename="a.log", encoding='utf-8', mode='w')
#   file_handler.setFormatter(formatter)
#   console_handler = StreamHandler()
#   console_handler.setFormatter(formatter)
#   log.setLevel(logging.DEBUG)
#   log.addHandler(file_handler)
#   log.addHandler(console_handler)

def log_response_error(
  message: str,
  res: Response,
  cookies: Cookies,
):
  raw_body = res.request.read().decode('utf-8')
  parsed_body = parse_request_body(raw_body)
  message += '\n  Response headers:\n' + format_headers(res.headers) \
    + '\n\n  Cookies:\n' + format_cookies(cookies) \
    + f'\n\n  Request: {res.request.method} {format_url(res.url)}' \
    + '\n\n  Request headers:\n' + format_headers(res.request.headers) \
    + '\n\n  Request parsed body:\n    ' + str(parsed_body) \
    + '\n\n  Request raw body:\n    ' + raw_body
  log.error(message)

def format_cookies(cookies: Cookies) -> str:
  s = ''
  for i, (name, value) in enumerate(cookies.items()):
    if i > 0:
      s += '\n'
    if len(value) > 30:
      value = value[:13] + ' ... ' + value[-18:]
    s += f'    {name}={value}'
  return s

def format_headers(headers: Headers) -> str:
  s = ''
  for i, (key, value) in enumerate(headers.items()):
    if i > 0:
      s += '\n'
    s += f'    {key}: {value}'
  return s

def parse_request_body(raw_body: str) -> dict[str, str]:
  parsed_body = parse_qs(raw_body)
  parsed_body = {k: v[0] for k, v in parsed_body.items()}
  return parsed_body

def format_url(url: URL) -> str:
  formatted_url = str(url)
  if len(formatted_url) > 100:
    formatted_url = formatted_url[:85] + ' ... ' + formatted_url[90:]
  return formatted_url

# _init()

# dir_name = os.path.dirname(__file__)
# log_file_path = os.path.join(dir_name, "log.json")

# def clear_log():
#   Path(log_file_path).unlink(missing_ok=True)

# def read_log() -> Any:
#   try:
#     with open(log_file_path) as log_file:
#       text = log_file.read()
#       if text.strip() == "":
#         return []
#       return json.loads(text)
#   except FileNotFoundError:
#     return []

# def log_get(
#   url: str,
#   headers: dict[str, str],
#   res: Response,
#   cookies: Cookies,
# ):
#   data = read_log()
#   data.append({
#     "my-url": url,
#     "my-headers": headers,
#     "url": res.request.url,
#     "headers": res.request.headers,
#     "cookies": cookies,
#     "res": [res.text],
#   })
#   with open(log_file_path, "w") as log_file:
#     json.dump(data, log_file, indent=2, default=json_default)

# def log_post(
#   url: str,
#   headers: dict[str, str],
#   form_data: dict[str, str],
#   res: Response,
#   cookies: Cookies,
# ):
#   raw_body = res.request.read().decode('utf-8')
#   parsed_body = parse_qs(raw_body)
#   parsed_body = {k: v[0] for k, v in parsed_body.items()}
#   data = read_log()
#   data.append({
#     "my-url": url,
#     "my-headers": headers,
#     "my-form-data": form_data,
#     "url": res.request.url,
#     "headers": res.request.headers,
#     "raw-body": raw_body,
#     "body": parsed_body,
#     "cookies": cookies,
#     "res": [res.text],
#   })
#   with open(log_file_path, "w") as log_file:
#     json.dump(data, log_file, indent=2, default=json_default)

# def log_post_json(
#   url: str,
#   headers: dict[str, str],
#   form_data: dict[str, str],
#   res: Response,
#   cookies: Cookies,
#   res_json: Any,
# ):
#   raw_body = res.request.read().decode('utf-8')
#   parsed_body = parse_qs(raw_body)
#   parsed_body = {k: v[0] for k, v in parsed_body.items()}
#   data = read_log()
#   data.append({
#     "my-url": url,
#     "my-headers": headers,
#     "my-form-data": form_data,
#     "url": res.request.url,
#     "headers": res.request.headers,
#     "raw-body": raw_body,
#     "body": parsed_body,
#     "cookies": cookies,
#     "res": [res.text],
#     "res_json": res_json,
#   })
#   with open(log_file_path, "w") as log_file:
#     json.dump(data, log_file, indent=2, default=json_default)

# def json_default(obj: Any):
#   if hasattr(obj, "__dict__"):
#       return obj.__dict__
#   return f"[Object {obj.__class__.__name__}]"

# # def log(s: str):
# #   with open(log_file_path, "w") as log_file:
# #     log_file.write(s)

# def log_to(file_name: str, s: str):
#   file_path = rel_path(file_name)
#   with open(file_path, "w") as log_file:
#     log_file.write(s)

# def rel_path(file_name: str) -> str:
#   return os.path.join(dir_name, file_name)
