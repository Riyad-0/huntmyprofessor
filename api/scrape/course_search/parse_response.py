from dataclasses import dataclass
import json
from typing import override

from bs4 import BeautifulSoup
from requests.sessions import RequestsCookieJar

from scrape.eval_url import EvalUrl
from scrape.parse_cookie import parse_cookie
from scrape.scrape_error import ScrapeError

from .send_request import Response

@dataclass
class Output():
  p_instance: str
  p_page_submission_id: str
  cookie: str
  course_sections: list[CourseSection]
  paginate_codes: PaginateCodes | None

@dataclass
class CourseSection:
  course: str
  semester: str
  professor: str
  url: EvalUrl

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
  
def parse_course_sections(soup: BeautifulSoup) -> list[CourseSection]:
  course_elements = soup.find_all(name="td", attrs={'headers': 'COURSE'})
  course_sections: list[CourseSection] = []
  for course_element in course_elements:
    semester_el = course_element.find_next_sibling(name="td", attrs={'headers': 'SEMETER'})
    professor_el = course_element.find_next_sibling(name="td", attrs={'headers': 'INST_NAME'})
    eval_el = course_element.find_next_sibling(name="td", attrs={'headers': 'EVAL_TYPE'})
    course = course_element.text
    if semester_el is None:
      continue
    semester = semester_el.text
    if professor_el is None:
      continue
    professor = professor_el.text
    if eval_el is None:
      continue
    link_el = eval_el.find(name="a")
    if link_el is None:
      continue
    href = link_el.get('href')
    if not isinstance(href, str):
      continue
    url = href

    course_sections.append(CourseSection(
      course=course,
      semester=semester,
      professor=professor,
      url=EvalUrl(rel_path=url),
    ))
  return course_sections

def parse_paginate_codes(soup: BeautifulSoup, res_text: str) -> PaginateCodes | None:
  next_page_button = soup.find(class_="t-Report-paginationLink--next")
  if next_page_button is None:
    return None

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

def parse_response(res_text: str, cookies: RequestsCookieJar) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
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

  cookie = parse_cookie(cookies)
  if cookie is None:
    raise CookieError()
  
  # course_elements = soup.find_all(name="td", attrs={'headers': 'COURSE'})
  # course_sections: list[CourseSection] = []
  # for course_element in course_elements:
  #   semester_el = course_element.find_next_sibling(name="td", attrs={'headers': 'SEMETER'})
  #   professor_el = course_element.find_next_sibling(name="td", attrs={'headers': 'INST_NAME'})
  #   eval_el = course_element.find_next_sibling(name="td", attrs={'headers': 'EVAL_TYPE'})
  #   course = course_element.text
  #   semester = None
  #   professor = None
  #   url = None
  #   if semester_el is not None:
  #     semester = semester_el.text
  #   if professor_el is not None:
  #     professor = professor_el.text
  #   if eval_el is not None:
  #     link_el = eval_el.find(name="a")
  #     if link_el is not None:
  #       href = link_el.get('href')
  #       if isinstance(href, str):
  #         url = href    

  #   course_sections.append(CourseSection(
  #     course=course,
  #     semester=semester,
  #     professor=professor,
  #     url=url,
  #   ))
  # next_page_button = soup.find(class_="t-Report-paginationLink--next")
  # if next_page_button is None:
  #   paginate_codes = None
  # else:
  course_sections = parse_course_sections(soup)
  paginate_codes = parse_paginate_codes(soup=soup, res_text=res_text)
      
  # courses = [course_element.text for course_element in soup.find_all(attrs={'headers': 'COURSE'})]
  return Output(
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    cookie=cookie,
    course_sections=course_sections,
    paginate_codes=paginate_codes,
  )
