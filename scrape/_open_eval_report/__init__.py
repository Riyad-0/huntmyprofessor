from scrape._course_search.parse_response import CourseSection
from scrape._log import log

from .input import Input

from .build_request import build_request
from .parse_response import Output, parse_response
from httpx import AsyncClient

async def open_eval_report(
  client: AsyncClient,
  cookie: str,
  course_section: CourseSection,
) -> Output:
  input = Input(cookie=cookie, url=course_section.url)
  request = build_request(input)
  log.debug(f"Opening eval: {course_section.full_name()}, {course_section.semester}, {course_section.professor}")
  res = await client.get(url=request.url, headers=request.headers, timeout=5)
  # log_get(
  #   url=request.url,
  #   headers=request.headers,
  #   res=res,
  #   cookies=client.cookies,
  # )
  return parse_response(res_text=res.text, cookies=client.cookies)