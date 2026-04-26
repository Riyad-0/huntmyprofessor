import json
import os

from .input import Input;

headers_file_path = os.path.join(os.path.dirname(__file__), "request_headers.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

partial_url = "https://orapp.hunter.cuny.edu/ords/wwv_flow.accept?p_context=116:3:"
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
  protected = input.p_page_items_protected
  search_text = input.search_text
  ck = input.ck
  return Request(
    url=partial_url + p_instance,
    # url="http://localhost:3000/api/req",
    headers=partial_headers | {
      "Cookie": cookie
    },
    form_data={
      'p_json': f'{{"salt":"{p_page_submission_id}","pageItems":{{"itemsToSubmit":[{{"n":"P3_LAST_NAME","v":"{search_text}"}},{{"n":"P3_LINK","v":"", "ck":"{ck}"}}],"protected":"{protected}","rowVersion":"","formRegionChecksums":[]}}}}',
      'p_flow_id': '116',
      'p_flow_step_id': '3',
      'p_instance': p_instance,
      'p_page_submission_id': p_page_submission_id,
      'p_request': 'P3_GO',
      'p_reload_on_submit': 'A'
    }
  )