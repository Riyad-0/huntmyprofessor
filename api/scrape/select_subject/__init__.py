from .input import Input

from .. import open_course_search_page
from .build_request import build_request
from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def select_subject(
  s: requests.Session,
  open_course_search_page_output: open_course_search_page.Output,
) -> Output:
  input = Input.from_open_course_search_page(output=open_course_search_page_output)
  req = build_request(input)
  res = send_request(s, req)
  return parse_response(req, res)