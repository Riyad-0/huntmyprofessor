import logging
from urllib.parse import parse_qs

from httpx import URL, Cookies, Headers, Response

log = logging.getLogger("huntmyprofessor")

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
