import json

from bs4 import BeautifulSoup
from ..parse_cookie import parse_cookie
from ..scrape_error import ScrapeError
from typing import override
from dataclasses import dataclass
from httpx import Cookies

@dataclass
class SelectElementOption:
  name: str
  value: str | None

@dataclass
class Output:
  cookie: str
  p_instance: str
  p_page_items_protected: str
  p_page_submission_id: str
  dept_ajax_identifier: str
  subject_ajax_identifier: str
  dept_options: list[SelectElementOption]

course_search_page_cookie_error_message = """expected cookie was not set after
accessing the course search page. The course search page may have changed
since this web scraper was last updated."""

course_search_page_html_error_message = """expected HTML elements were not found in the
course search page. The course search page may have changed since this web
scraper was last updated."""

course_search_page_ajax_identifier_error_message = """ajaxIdentifier was not 
found in the course search page. The course search page may have changed since 
this web scraper was last updated."""

class CookieError(ScrapeError):
  @override
  def message(self) -> str:
    return course_search_page_cookie_error_message

@dataclass
class HTMLError(ScrapeError):
  res_text: str
  @override
  def message(self) -> str:
    return course_search_page_html_error_message + \
      "\nResponse text:\n" + self.res_text
  
@dataclass
class AjaxIdentifierError(ScrapeError):
  res_text: str
  @override
  def message(self) -> str:
    return course_search_page_ajax_identifier_error_message + \
      "\nResponse text:\n" + self.res_text

def get_ajax_identifier(res_text: str, pattern_id: str):
  pattern = f'(function(){{apex.widget.selectList("#{pattern_id}"'
  i = res_text.find(pattern)
  if i == -1:
    raise AjaxIdentifierError(res_text=res_text)
  i += len(pattern)
  pattern = '"ajaxIdentifier":"'
  j = res_text.find(pattern, i)
  if j == -1:
    raise AjaxIdentifierError(res_text=res_text)
  start = j + len(pattern)
  end = res_text.find('"', start)
  if end == -1:
    raise AjaxIdentifierError(res_text=res_text)
  raw_ajax_identifier = res_text[start:end]

  # This is necessary to replace escape sequences (e.g. \\u002F) with the
  # proper character (e.g. /).
  ajax_identifier = json.loads(f'"{raw_ajax_identifier}"')
  return ajax_identifier

def parse_response(res_text: str, cookies: Cookies) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
  pattern = '(function(){apex.widget.selectList("#P6_SUBJECT"'
  i = res_text.find(pattern)
  if i == -1:
    raise AjaxIdentifierError(res_text=res_text)
  i += len(pattern)
  pattern = '"ajaxIdentifier":"'
  j = res_text.find(pattern, i)
  if j == -1:
    raise AjaxIdentifierError(res_text=res_text)
  start = j + len(pattern)
  end = res_text.find('"', start)
  if end == -1:
    raise AjaxIdentifierError(res_text=res_text)
  raw_ajax_identifier = res_text[start:end]

  # This is necessary to replace escape sequences (e.g. \\u002F) with the
  # proper character (e.g. /).
  dept_ajax_identifier = json.loads(f'"{raw_ajax_identifier}"')

  subject_ajax_identifier = get_ajax_identifier(res_text, "P6_CATALOG_NUM")
  
  dept_select_element = soup.find(id='P6_DEPT')
  p_instance_element = soup.find(id='pInstance')
  p_page_submission_id_element = soup.find(id='pPageSubmissionId')
  p_page_items_protected_element = soup.find(id='pPageItemsProtected')
  if (
    dept_select_element is None or
    p_instance_element is None or
    p_page_submission_id_element is None or
    p_page_items_protected_element is None
  ):
    raise HTMLError(res_text)
  dept_options: list[SelectElementOption] = []
  for select_el in dept_select_element.find_all(name='option'):
    text = select_el.text
    value = select_el.get("value")
    if isinstance(value, str):
      dept_options.append(SelectElementOption(name=text, value=value))
  p_instance = p_instance_element.get("value")
  p_page_submission_id = p_page_submission_id_element.get("value")
  p_page_items_protected = p_page_items_protected_element.get("value")
  if (
    not isinstance(p_instance, str) or
    not isinstance(p_page_submission_id, str) or
    not isinstance(p_page_items_protected, str)
  ):
    raise HTMLError(res_text)

  cookie = parse_cookie(cookies)
  if cookie is None:
    raise CookieError()
  return Output(
    dept_ajax_identifier=dept_ajax_identifier,
    subject_ajax_identifier=subject_ajax_identifier,
    cookie=cookie,
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    p_page_items_protected=p_page_items_protected,
    dept_options=dept_options,
  )
