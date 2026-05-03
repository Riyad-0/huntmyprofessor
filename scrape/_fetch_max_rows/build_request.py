import json
import os

from .input import Input;

headers_file_path = os.path.join(os.path.dirname(__file__), "request_headers.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

partial_url = "https://orapp.hunter.cuny.edu/ords/wwv_flow.ajax?p_context=116:6:"
partial_headers = parse_headers()

class Request:
  def __init__(
    self,
    url: str,
    headers: dict[str, str],
    form_data: dict[str, str]
  ):
    self.url = url
    self.headers = headers
    self.form_data = form_data

def build_request(input: Input):
  cookie = input.cookie
  p_instance = input.p_instance
  p_page_submission_id = input.p_page_submission_id
  salt = p_page_submission_id
  p_request = input.paginate_codes.p_request
  x01 = input.paginate_codes.x01
  return Request(
    url=partial_url + p_instance,
    headers=partial_headers | {
      "Cookie": cookie
    },
    form_data={
      'p_flow_id': '116',
      'p_flow_step_id': '6',
      'p_instance': p_instance,
      'p_debug': '',
      'p_request': f'PLUGIN={p_request}',
      'p_widget_action': 'paginate',
      'p_pg_min_row': '1', # Normally 21
      'p_pg_max_rows': '2000', # Normally 20
      'p_pg_rows_fetched': '20',
      'x01': x01,
      'p_json': f'{{"salt":"{salt}"}}',
    },
  )