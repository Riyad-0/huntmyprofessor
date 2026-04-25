from scrape.course_search.parse_response import CourseSection
from scrape.log import log_get

from .input import Input

from .build_request import build_request
from .parse_response import parse_response, Output, parse_response2
from .send_request import send_request
from scrape.log import log
import requests

def open_eval_report(
  s: requests.Session,
  cookie: str,
  url: str,
) -> Output:
  input = Input(cookie=cookie, url=url)
  response = send_request(s, input)
  return parse_response(response)

def open_eval_report2(
  s: requests.Session,
  cookie: str,
  course_section: CourseSection,
) -> Output:
  input = Input(cookie=cookie, url=course_section.url.absolute())
  request = build_request(input)
  log.info(f"Opening eval: {course_section.course}, {course_section.semester}, {course_section.professor}")
  res = s.get(url=request.url, headers=request.headers, timeout=5)
  log_get(
    url=request.url,
    headers=request.headers,
    res=res,
    cookies=s.cookies,
  )
  return parse_response2(res_text=res.text, cookies=s.cookies)