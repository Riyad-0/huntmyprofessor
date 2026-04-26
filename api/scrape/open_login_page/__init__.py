from scrape.log import log_get

from .parse_response import Output, parse_response
from . import request
import requests
from scrape.log import log

async def open_login_page(s: requests.Session) -> Output:
  # response = send_request(s)
  log.info("Opening login page")
  res = s.get(url=request.url, headers=request.headers)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=s.cookies,
  )
  return parse_response(res_text=res.text, cookies=s.cookies)
