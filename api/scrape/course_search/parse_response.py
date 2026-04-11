from dataclasses import dataclass
import json
from typing import override

from bs4 import BeautifulSoup

from scrape.parse_cookie import parse_cookie
from scrape.scrape_error import ScrapeError

from .input import Input
from .send_request import Response

@dataclass
class Output():
  p_instance: str
  p_page_submission_id: str
  cookie: str
  eval_reports: list[EvalReport]
  paginate_codes: PaginateCodes | None

@dataclass
class EvalReport:
  course: str
  semester: str | None
  professor: str | None
  # Relative path; should be prefixed by 'https://orapp.hunter.cuny.edu/ords/'.
  url: str | None

@dataclass
class PaginateCodes:
  x01: str
  p_request: str

@dataclass
class HTMLError(ScrapeError):
  @override
  def message(self):
    return "HTML error"
  
@dataclass
class CookieError(ScrapeError):
  @override
  def message(self):
    return "Cookie error"

def parse_paginate_codes(res_text: str) -> PaginateCodes | None:
  pattern = "widget.report.paginate('"
  i = res_text.find(pattern)
  if i == -1:
    return None
  start = i + len(pattern)
  i = res_text.find("'", start)
  if i == -1:
    return None
  end = i
  x01 = res_text[start:end]
  i = res_text.find("'", end + 1)
  if i == -1:
    return None
  start = i + 1
  i = res_text.find("'", start)
  if i == -1:
    return None
  end = i
  raw_p_request = res_text[start:end]

  # This is necessary to replace escape sequences (e.g. \\u002F) with the
  # proper character (e.g. /).
  p_request = json.loads(f'"{raw_p_request}"')

  return PaginateCodes(x01=x01, p_request=p_request)

def parse_response(response: Response, input: Input) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
  p_instance_element = soup.find(id='pInstance')
  p_page_submission_id_element = soup.find(id='pPageSubmissionId')
  if (
    p_instance_element is None or
    p_page_submission_id_element is None
  ):
    raise HTMLError()
  p_instance = p_instance_element.get("value")
  p_page_submission_id = p_page_submission_id_element.get("value")
  if (
    not isinstance(p_instance, str) or
    not isinstance(p_page_submission_id, str)
  ):
    raise HTMLError()

  cookie = parse_cookie(response.cookies)
  if cookie is None:
    raise CookieError()
  
  course_elements = soup.find_all(name="td", attrs={'headers': 'COURSE'})
  eval_reports: list[EvalReport] = []
  for course_element in course_elements:
    semester_el = course_element.find_next_sibling(name="td", attrs={'headers': 'SEMETER'})
    professor_el = course_element.find_next_sibling(name="td", attrs={'headers': 'INST_NAME'})
    eval_el = course_element.find_next_sibling(name="td", attrs={'headers': 'EVAL_TYPE'})
    course = course_element.text
    semester = None
    professor = None
    url = None
    if semester_el is not None:
      semester = semester_el.text
    if professor_el is not None:
      professor = professor_el.text
    if eval_el is not None:
      link_el = eval_el.find(name="a")
      if link_el is not None:
        href = link_el.get('href')
        if isinstance(href, str):
          url = href
    eval_reports.append(EvalReport(
      course=course,
      semester=semester,
      professor=professor,
      url=url,
    ))
  paginate_codes = parse_paginate_codes(response.text)
      
  # courses = [course_element.text for course_element in soup.find_all(attrs={'headers': 'COURSE'})]
  return Output(
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    cookie=cookie,
    eval_reports=eval_reports,
    paginate_codes=paginate_codes,
  )
