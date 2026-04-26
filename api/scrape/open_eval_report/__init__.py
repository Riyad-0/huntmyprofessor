from scrape.course_search.parse_response import CourseSection
from scrape.log import log_get

from .input import Input

from .build_request import build_request
from .parse_response import Output, parse_response
from scrape.log import log
import requests

async def open_eval_report(
  s: requests.Session,
  cookie: str,
  course_section: CourseSection,
) -> Output:
  input = Input(cookie=cookie, url=course_section.url)
  request = build_request(input)
  log.info(f"Opening eval: {course_section.full_name()}, {course_section.semester}, {course_section.professor}")
  res = s.get(url=request.url, headers=request.headers, timeout=5)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=s.cookies,
  )
  return parse_response(res_text=res.text, cookies=s.cookies)