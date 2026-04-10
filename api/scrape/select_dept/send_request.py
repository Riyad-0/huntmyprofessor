from dataclasses import dataclass

from .build_request import Request
import requests
from requests.sessions import RequestsCookieJar

@dataclass
class Response:
  res: requests.Response
  cookies: RequestsCookieJar

def send_request(s: requests.Session, request: Request):
  res = s.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  return Response(res=res, cookies=s.cookies)