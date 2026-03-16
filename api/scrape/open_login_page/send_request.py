# class RawResponseData {
#   text: string,
#   cookies: string[]
# }

from . import request
import requests

class Response:
  def __init__(self, text: str, cookies: requests.sessions.RequestsCookieJar):
    self.text = text
    self.cookies = cookies

def send_request(s: requests.Session):
  res = s.get(url=request.url, headers=request.headers)
  return Response(text=res.text, cookies=s.cookies)