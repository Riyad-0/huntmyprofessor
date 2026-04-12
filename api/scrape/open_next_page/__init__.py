from scrape.course_search.parse_response import PaginateCodes

from .input import Input

from .parse_response import parse_response, Output
from .send_request import send_request
import requests

def open_next_page(
  s: requests.Session,
  cookie: str,
  p_instance: str,
  p_page_submission_id: str,
  paginate_codes: PaginateCodes,
) -> Output:
  input = Input(
    cookie=cookie,
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    paginate_codes=paginate_codes,
  )
  response = send_request(s, input)
  return parse_response(response)