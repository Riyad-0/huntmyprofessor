from scrape._data import Data
from scrape._log import log
from scrape._course_search.parse_response import PaginateCodes

from .input import Input

from .parse_response import Output, parse_response
from .build_request import build_request
from httpx import AsyncClient

async def fetch_max_rows(
  client: AsyncClient,
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
  res = await client.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  # log_post(
  #   url=request.url,
  #   headers=request.headers,
  #   form_data=request.form_data,
  #   res=res,
  #   cookies=client.cookies
  # )

  # response = send_request(s, input)
  return parse_response(res_text=res.text, cookies=client.cookies, data=data)