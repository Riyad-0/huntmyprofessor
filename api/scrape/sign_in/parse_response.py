from bs4 import BeautifulSoup

from .input import Input
from ..parse_cookie import parse_cookie
from .send_request import Response
from ..scrape_error import ScrapeError
from typing import Literal, override

class Output:
  def __init__(
    self,
    ck: str,
    cookie: str,

    # Even though pInstance remains the same throughout the session, it also
    # reappears in each page so I choose to refresh it whenever possible just
    # in case it can "expire."
    p_instance: str,

    p_page_items_protected: str,
    p_page_submission_id: str
  ) -> None:
    self.ck = ck
    self.cookie = cookie
    self.p_instance = p_instance
    self.p_page_items_protected = p_page_items_protected
    self.p_page_submission_id = p_page_submission_id

log_in_html_error_message = """expected HTML elements were not found \
after logging in. The successful login page may have changed since this web \
scraper was last updated."""

log_in_cookie_error_message = """expected cookie was not set after logging \
in. This web scraper may need to be updated."""

class CookieError(ScrapeError):
  @override
  def message(self) -> str:
    return log_in_cookie_error_message

class HTMLError(ScrapeError):
  def __init__(self, missing: set[MissingElement], response_text: str) -> None:
    self.missing = missing
    self.response_text = response_text

  @override
  def message(self) -> str:
    missing_message = f"missing elements: {self.missing}"
    response_text_message = f"response text:\n{self.response_text}"
    return log_in_html_error_message + "\n" + \
      missing_message + "\n" + \
      response_text_message
  
type MissingElement = Literal["data-for=P3_LINK", "pPageItemsProtected", "pPageSubmissionId"]

def parse_response(response: Response, input: Input) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
  ck_element = soup.find(attrs={'data-for': 'P3_LINK'})
  p_instance_element = soup.find(id='pInstance')
  p_page_items_protected_element = soup.find(id='pPageItemsProtected')
  p_page_submission_id_element = soup.find(id='pPageSubmissionId')
  if (
    ck_element is None or
    p_page_items_protected_element is None or
    p_page_submission_id_element is None
  ):
    missing_elements = set[MissingElement]()
    if ck_element is None:
      missing_elements.add("data-for=P3_LINK")
    if p_page_items_protected_element is None:
      missing_elements.add("pPageItemsProtected")
    if p_page_submission_id_element is None:
      missing_elements.add("pPageSubmissionId")
    raise HTMLError(missing=missing_elements, response_text=response.text)
  p_instance = None if p_instance_element is None \
    else p_instance_element.get("value")
  if not isinstance(p_instance, str):
    p_instance = input.p_instance
  # p_instance = input.p_instance if p_instance_element is None \
  #   else p_instance_element.get("value")
  ck = ck_element.get("value")
  p_page_submission_id = p_page_submission_id_element.get("value")
  p_page_items_protected = p_page_items_protected_element.get("value")
  if (
    not isinstance(ck, str) or
    not isinstance(p_page_submission_id, str) or
    not isinstance(p_page_items_protected, str)
  ):
    missing_elements = set[MissingElement]()
    if not isinstance(ck, str):
      missing_elements.add("data-for=P3_LINK")
    if not isinstance(p_page_items_protected, str):
      missing_elements.add("pPageItemsProtected")
    if not isinstance(p_page_submission_id, str):
      missing_elements.add("pPageSubmissionId")
    raise HTMLError(missing=missing_elements, response_text=response.text)

  cookie = parse_cookie(response.cookies)
  if cookie is None:
    raise CookieError()
  return Output(
    ck=ck,
    cookie=cookie,
    p_instance=p_instance,
    p_page_items_protected=p_page_items_protected,
    p_page_submission_id=p_page_submission_id
  )

