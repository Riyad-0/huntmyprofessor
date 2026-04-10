import json
import os

from .input import Input

headers_file_path = os.path.join(os.path.dirname(__file__), "requestHeaders.json")

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
  ajax_identifier = input.ajax_identifier
  cookie = input.cookie
  p_instance = input.p_instance
  salt = input.p_page_submission_id
  protected = input.p_page_items_protected
  dept = "CSCI-HTR"
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
      'p_request': f'PLUGIN={ajax_identifier}',
      'p_json': f'{{"pageItems":{{"itemsToSubmit":[{{"n":"P6_DEPT","v":"{dept}"}}],"protected":"{protected}","rowVersion":"","formRegionChecksums":[]}},"salt":"{salt}"}}',
    }
  )