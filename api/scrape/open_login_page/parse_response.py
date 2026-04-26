from bs4 import BeautifulSoup
from requests.sessions import RequestsCookieJar
from ..parse_cookie import parse_cookie
from ..scrape_error import ScrapeError
from typing import override

class Output:
  def __init__(
    self,
    cookie: str,
    p_instance: str,
    p_page_items_protected: str,
    p_page_submission_id: str
  ) -> None:
    self.cookie = cookie
    self.p_instance = p_instance
    self.p_page_items_protected = p_page_items_protected
    self.p_page_submission_id = p_page_submission_id

loginPageCookieErrorMessage = """expected cookie was not set after
accessing the login page. The login page may have changed since this web
scraper was last updated."""

loginPageHTMLErrorMessage = """expected HTML elements were not found in the
login page. The login page may have changed since this web scraper was last
updated."""

class CookieError(ScrapeError):
  @override
  def message(self) -> str:
    return loginPageCookieErrorMessage

class HTMLError(ScrapeError):
  @override
  def message(self) -> str:
    return loginPageHTMLErrorMessage

def parse_response(res_text: str, cookies: RequestsCookieJar) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
  p_instance_element = soup.find(id='pInstance')
  p_page_submission_id_element = soup.find(id='pPageSubmissionId')
  p_page_items_protected_element = soup.find(id='pPageItemsProtected')
  if (
    p_instance_element is None or
    p_page_submission_id_element is None or
    p_page_items_protected_element is None
  ):
    raise HTMLError()
  p_instance = p_instance_element.get("value")
  p_page_submission_id = p_page_submission_id_element.get("value")
  p_page_items_protected = p_page_items_protected_element.get("value")
  if (
    not isinstance(p_instance, str) or
    not isinstance(p_page_submission_id, str) or
    not isinstance(p_page_items_protected, str)
  ):
    raise HTMLError()

  cookie = parse_cookie(cookies)
  if cookie is None:
    raise CookieError()
  return Output(
    cookie=cookie,
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    p_page_items_protected=p_page_items_protected
  )