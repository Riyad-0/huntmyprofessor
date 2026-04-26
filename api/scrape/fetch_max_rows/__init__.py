from scrape.data import Data
from scrape.log import log_post, log
from scrape.course_search.parse_response import PaginateCodes

from .input import Input

from .parse_response import Output, parse_response
from .build_request import build_request
import requests

async def fetch_max_rows(
  s: requests.Session,
  data: Data,
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

  request = build_request(input)
  log.info("Fetching max rows")
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

  # response = send_request(s, input)
  return parse_response(res_text=res.text, cookies=s.cookies, data=data)