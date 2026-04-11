# class RawResponseData {
#   text: string,
#   cookies: string[]
# }

from scrape.log import log_get

from . import request
import requests

class Response:
  def __init__(self, text: str, cookies: requests.sessions.RequestsCookieJar):
    self.text = text
    self.cookies = cookies

def send_request(s: requests.Session):
  print("Opening login page...")
  res = s.get(url=request.url, headers=request.headers)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=s.cookies,
  )
  return Response(text=res.text, cookies=s.cookies)