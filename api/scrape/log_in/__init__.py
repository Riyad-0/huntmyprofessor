from scrape.log import log_post, log
from httpx import AsyncClient


from .input import Input

from .. import open_login_page
from .build_request import build_request
from .parse_response import Output, parse_response

async def log_in(
  client: AsyncClient,
  open_login_page_output: open_login_page.Output,
  username: str,
  password: str,
) -> Output:
  input = Input(open_login_page_output, username, password)
  request = build_request(input)
  log.info("Logging in")
  res = await client.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  log_post(
    url=request.url,
    headers=request.headers,
    form_data=request.form_data,
    res=res,
    cookies=client.cookies
  )
  return parse_response(res_text=res.text, cookies=client.cookies, input=input)