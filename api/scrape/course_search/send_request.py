# class RawResponseData {
#   text: string,
#   cookies: string[]
# }

from .input import Input

from .build_request import build_request
import requests

class Response:
  def __init__(self, text: str, cookies: requests.sessions.RequestsCookieJar):
    self.text = text
    self.cookies = cookies

def send_request(s: requests.Session, input: Input):
  request = build_request(input)
  res = s.post(
    url=request.url,
    headers=request.headers,
  )
  return Response(text=res.text, cookies=s.cookies)