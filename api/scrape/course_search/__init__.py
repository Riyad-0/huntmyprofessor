from .input import Input

from .. import open_course_search_page
from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def course_search(
  s: requests.Session,
  open_course_search_page_output: open_course_search_page.Output,
  department: str,
  subject: str,
  course_num: str,
) -> Output:
  input = Input.from_open_course_search_page(
    output=open_course_search_page_output,
    department=department,
    subject=subject,
    course_num=course_num,
  )
  response = send_request(s, input)
  return parse_response(response)