from scrape.log import log_post, log
from scrape.data import Data

from .input import Input

from .. import open_course_search_page
from .build_request import build_request
from .parse_response import Output, parse_response
import requests

def course_search(
  s: requests.Session,
  open_course_search_page_output: open_course_search_page.Output,
  data: Data,
  department: str,
  subject: str,
  course_num: str,
  did_fetch_max_rows: bool,
) -> Output:
  input = Input.from_open_course_search_page(
    output=open_course_search_page_output,
    data=data,
    department=department,
    subject=subject,
    course_num=course_num,
  )

  request = build_request(input)
  log.info(f"Searching: {subject} {course_num}")
  res = s.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  log_post(
    url=request.url,
    headers=request.headers,
    form_data=request.form_data,
    res=res,
    cookies=s.cookies
  )
  output = parse_response(
    res_text=res.text,
    cookies=s.cookies,
    did_fetch_max_rows=did_fetch_max_rows,
    data=data,
  )
  if output.eval_count is None:
    log.warning(f"Couldn't count evals for: {subject} {course_num}")
  else:
    if output.more_than:
      log.warning(f"Found more than {output.eval_count} evals for: {subject} {course_num}")
    else:
      log.info(f"Found {output.eval_count} evals for: {subject} {course_num}")
  return output
