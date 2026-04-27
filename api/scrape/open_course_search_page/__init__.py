from scrape.log import log_get, log

from .input import Input

from .. import log_in
from .build_request import build_request
from .parse_response import Output, parse_response
from httpx import AsyncClient

async def open_course_search_page(
  client: AsyncClient,
  sign_in_output: log_in.Output,
) -> Output:
  input = Input.from_sign_in(output=sign_in_output)
  request = build_request(input)
  log.info("Opening course search page")
  res = await client.get(url=request.url, headers=request.headers)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=client.cookies,
  )
  return parse_response(res_text=res.text, cookies=client.cookies)
  # response = send_request(s, input)
  # return parse_response(response)