import json

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
  
def parse_response(response: Response) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
  question_elements = soup.find_all(name="td", attrs={'headers': 'QUESTION'})
  eval_reports: list[EvalReport] = []
  scores = []
  question_elements0 = question_elements[0:9]
  question_elements1 = question_elements[9:14]
  question_elements2 = question_elements[14:20]
  for question_element in question_elements0:
    question_scores = []
    for i in range(7):
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': f'COL{i+1}'})
      score = int(score_el.text)
      question_scores.append(score)
    scores.append(question_scores)
  for question_element in question_elements1:
    question_scores = []
    for i in range(4):
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': f'COL{i+1}'})
      score = int(score_el.text)
      question_scores.append(score)
  for question_element in question_elements2:
    question_scores = []
    for i in range(3):
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': f'COL{i+1}'})
      score = int(score_el.text)
      question_scores.append(score)

  grade_names = ["A", "B", "C", "D", "F", "Credit, No Credit, Audit"]
  grades = []
  for grade_name in grade_names:
    grade_name_el = soup.find(string=grade_name)
    if grade_name_el is None:
      raise HTMLError(response.text)
    gradle_el = grade_name_el.next_sibling
    grade_el_text = grade_el.text
    grades.push(int(grade_el_text))

  for question_element in question_elements:
    for i in range(7):

    question_element.find_next_siblings
    semester_el = question_element.find_next_sibling(name="td", attrs={'headers': 'SEMETER'})
    professor_el = question_element.find_next_sibling(name="td", attrs={'headers': 'INST_NAME'})
    eval_el = question_element.find_next_sibling(name="td", attrs={'headers': 'EVAL_TYPE'})
    course = question_element.text
    semester = None
    professor = None
    url = None
    if semester_el is not None:


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
    dept_ajax_identifier=dept_ajax_identifier,
    subject_ajax_identifier=subject_ajax_identifier,
    cookie=cookie,
    p_instance=p_instance,
    p_page_submission_id=p_page_submission_id,
    p_page_items_protected=p_page_items_protected,
    dept_options=dept_options,
  )

