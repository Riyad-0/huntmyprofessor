# class RawResponseData {
#   text: string,
#   cookies: string[]
# }

from scrape.log import log_post

from .input import Input

from .build_request import build_request
import requests

from scrape.course_search.parse_response import Response

# class Response:
#   def __init__(self, text: str, cookies: requests.sessions.RequestsCookieJar):
#     self.text = text
#     self.cookies = cookies

def send_request(s: requests.Session, input: Input):
  request = build_request(input)
  print("Opening next page...")
  res = s.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  log_post(
    url=request.url,
    headers=request.headers,
    form_data=request.form_data,
    res=res,
    cookies=s.cookies
  )
  return Response(text=res.text, cookies=s.cookies)