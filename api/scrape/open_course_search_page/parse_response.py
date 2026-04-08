from bs4 import BeautifulSoup
from ..parse_cookie import parse_cookie
from .send_request import Response
from ..scrape_error import ScrapeError
from typing import override
from dataclasses import dataclass

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
  dept_options: list[SelectElementOption]

course_search_page_cookie_error_message = """expected cookie was not set after
accessing the course search page. The course search page may have changed
since this web scraper was last updated."""

course_search_page_html_error_message = """expected HTML elements were not found in the
course search page. The course search page may have changed since this web
scraper was last updated."""

class CookieError(ScrapeError):
  @override
  def message(self) -> str:
    return course_search_page_cookie_error_message

@dataclass
class HTMLError(ScrapeError):
  html: str
  @override
  def message(self) -> str:
    return course_search_page_html_error_message + \
      "\nResponse text:\n" + self.html

def parse_response(response: Response) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
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
    raise HTMLError(response.text)
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
    raise HTMLError(response.text)

  cookie = parse_cookie(response.cookies)
  if cookie is None:
    raise CookieError()
  return Output(
    cookie=cookie,
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    p_page_items_protected=p_page_items_protected,
    dept_options=dept_options,
  )

