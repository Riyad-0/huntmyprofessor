from dataclasses import dataclass
import json
from typing import override

from bs4 import BeautifulSoup
from httpx import Cookies

from scrape._data import Data
from scrape._eval_url import EvalUrl
from scrape._parse_cookie import parse_cookie
from scrape._error import MyError
from scrape._log import log

type ParseResult = Parsed | NeedsPaginate

@dataclass
class Parsed:
  course_sections: list[CourseSection]

@dataclass
class NeedsPaginate:
  paginate_codes: PaginateCodes

@dataclass
class Output():
  p_instance: str
  p_page_submission_id: str
  cookie: str
  # course_sections: list[CourseSection]
  parse_result: ParseResult
  paginate_codes: PaginateCodes | None
  eval_count: int | None
  more_than: bool

@dataclass
class CourseSection:
  course: str
  section: str | None
  semester: str
  professor: str
  url: EvalUrl

  def full_name(self) -> str:
    if self.section is None:
      return self.course
    else:
      return f"{self.course} Sec: {self.section}"

@dataclass
class PaginateCodes:
  x01: str
  p_request: str

@dataclass
class HTMLError(MyError):
  @override
  def message(self):
    return "HTML error"
  
@dataclass
class CookieError(MyError):
  @override
  def message(self):
    return "Cookie error"
  
@dataclass
class ParseCourseSectionsOutput:
  course_sections: list[CourseSection]
  eval_count: int

def parse_course_sections(soup: BeautifulSoup, data: Data) -> ParseCourseSectionsOutput:
  course_elements = soup.find_all(name="td", attrs={'headers': 'COURSE'})
  course_sections: list[CourseSection] = []
  n = 0
  for course_element in course_elements:
    n += 1
    semester_el = course_element.find_next_sibling(name="td", attrs={'headers': 'SEMETER'})
    professor_el = course_element.find_next_sibling(name="td", attrs={'headers': 'INST_NAME'})
    eval_el = course_element.find_next_sibling(name="td", attrs={'headers': 'EVAL_TYPE'})
    course_str = course_element.text
    if not isinstance(course_str, str):
      continue
    split = course_str.split(sep="Sec:", maxsplit=1)
    if len(split) == 2:
      course = split[0].rstrip()
      section = split[1].lstrip()
    else:
      course = course_str
      section = None

    if semester_el is None:
      continue
    semester = semester_el.text
    if not isinstance(semester, str):
      continue
    if professor_el is None:
      continue
    professor = professor_el.text
    if not isinstance(professor, str):
      continue
    if eval_el is None:
      continue
    link_el = eval_el.find(name="a")
    if link_el is None:
      continue
    href = link_el.get('href')
    if not isinstance(href, str):
      continue
    url = href

    if data.contains(
      course=course,
      section=section,
      semester=semester,
      professor=professor,
    ):
      log.debug(f"Skipping already-scraped: {course} Sec: {section}, {semester}, {professor}")
      continue

    course_sections.append(CourseSection(
      course=course,
      section=section,
      semester=semester,
      professor=professor,
      url=EvalUrl(rel_path=url),
    ))
  return ParseCourseSectionsOutput(
    course_sections=course_sections,
    eval_count=n,
  )

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

def parse_response(
  res_text: str,
  cookies: Cookies,
  did_fetch_max_rows: bool,
  data: Data,
) -> Output:
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
  eval_count = None
  paginate_codes = parse_paginate_codes(soup=soup, res_text=res_text)
  if did_fetch_max_rows or paginate_codes is None:
    output = parse_course_sections(soup=soup, data=data)
    eval_count = output.eval_count
    parse_result = Parsed(course_sections=output.course_sections)
  else:
    parse_result = NeedsPaginate(paginate_codes=paginate_codes)
  # course_sections = parse_course_sections(soup)
  paginate_select_el = soup.find(attrs={'name': 'X01'})
  more_than = False
  if paginate_select_el is not None:
    paginate_select_text = paginate_select_el.text
    if isinstance(paginate_select_text, str):
      if "more than 2000" in paginate_select_text:
        eval_count = 2000
        more_than = True
      else:
        try:
          i = paginate_select_text.rindex(" of ")
          i += len(" of ")
          eval_count = int(paginate_select_text[i:])
        except ValueError:
          pass


      
  # courses = [course_element.text for course_element in soup.find_all(attrs={'headers': 'COURSE'})]
  return Output(
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    cookie=cookie,
    # course_sections=course_sections,
    parse_result=parse_result,
    paginate_codes=paginate_codes,
    eval_count=eval_count,
    more_than=more_than,
  )
