import json
import os

from .input import Input;

headers_file_path = os.path.join(os.path.dirname(__file__), "requestHeaders.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

partial_url = "https://orapp.hunter.cuny.edu/ords/wwv_flow.accept?p_context=116:6:"
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
  protected = input.p_page_items_protected
  dept = input.department
  subject = input.subject
  course_num = input.course_num
  return Request(
    url=partial_url + p_instance,
    # url="http://localhost:3000/api/req",
    headers=partial_headers | {
      "Cookie": cookie
    },
    form_data={
      'p_json': f'{{"salt":"{salt}","pageItems":{{"itemsToSubmit":[{{"n":"P6_DEPT","v":"{dept}"}},{{"n":"P6_SUBJECT","v":"{subject}"}},{{"n":"P6_CATALOG_NUM","v":"{course_num}"}}],"protected":"{protected}","rowVersion":"","formRegionChecksums":[]}}}}',
      'p_flow_id': '116',
      'p_flow_step_id': '6',
      'p_instance': p_instance,
      'p_page_submission_id': p_page_submission_id,
      'p_request': 'P6_GO',
      'p_reload_on_submit': 'A',
    },
  )