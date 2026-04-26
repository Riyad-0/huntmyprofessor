from .input import Input

from .. import open_course_search_page
from .build_request import build_request
from .parse_response import parse_response, Output
import requests

async def select_dept(
  s: requests.Session,
  open_course_search_page_output: open_course_search_page.Output,
) -> Output:
  input = Input.from_open_course_search_page(output=open_course_search_page_output)
  req = build_request(input)
  res = s.post(
    url=req.url,
    headers=req.headers,
    data=req.form_data,
  )
  return parse_response(req, res, s.cookies)