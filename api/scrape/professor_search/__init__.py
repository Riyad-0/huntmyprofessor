from .input import Input

from .. import log_in
from .build_request import build_request
from .parse_response import Output, parse_response
import requests

async def professor_search(
  s: requests.Session,
  sign_in_output: log_in.Output,
  search_text: str
) -> Output:
  input = Input.from_sign_in(output=sign_in_output, search_text=search_text)
  request = build_request(input)
  res = s.post(
    url=request.url,
    headers=request.headers,
    data=request.form_data,
  )
  return parse_response(res_text=res.text, input=input)