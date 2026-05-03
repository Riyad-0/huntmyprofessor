from .build_request import build_request
from scrape._log import log
from scrape import _parse_course_search_page
from scrape._parse_course_search_page import parse_course_search_page
from httpx import AsyncClient

async def open_course_search_page(
  client: AsyncClient,
  cookie: str,
) -> _parse_course_search_page.CourseSearchPage:
  request = build_request(cookie)
  log.info("Opening course search page with cookie")
  res = await client.get(url=request.url, headers=request.headers)
  # log_get(
  #   url=request.url,
  #   headers=request.headers,
  #   res=res,
  #   cookies=client.cookies,
  # )
  return parse_course_search_page(res_text=res.text, cookie=cookie)
  # response = send_request(s, input)
  # return parse_response(response)