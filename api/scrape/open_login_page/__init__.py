from httpx import AsyncClient

from scrape.log import log_get

from .parse_response import Output, parse_response
from . import request
from scrape.log import log

async def open_login_page(client: AsyncClient) -> Output:
  # response = send_request(s)
  log.info("Opening login page")
  res = await client.get(url=request.url, headers=request.headers)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=client.cookies,
  )
  return parse_response(res_text=res.text, cookies=client.cookies)
