from scrape.log import log_post, log

from .input import Input

from .. import open_login_page
from .build_request import build_request
from .parse_response import Output, parse_response
import requests

async def log_in(
  s: requests.Session,
  open_login_page_output: open_login_page.Output,
  username: str,
  password: str
) -> Output:
  input = Input(open_login_page_output, username, password)
  request = build_request(input)
  log.info("Logging in")
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
  return parse_response(res_text=res.text, cookies=s.cookies, input=input)