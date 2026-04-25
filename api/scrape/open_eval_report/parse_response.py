from bs4 import BeautifulSoup

from scrape.eval_report import EvalReportQuestion, ScoreSection
from ..parse_cookie import parse_cookie
from .send_request import Response
from ..scrape_error import ScrapeError
from typing import override
from dataclasses import dataclass
from requests.sessions import RequestsCookieJar

@dataclass
class SelectElementOption:
  name: str
  value: str | None

@dataclass
class Output:
  cookie: str | None
  score_sections: list[ScoreSection]
  expected_grades: list[int]

course_search_page_cookie_error_message = """expected cookie was not set after
accessing the course search page. The course search page may have changed
since this web scraper was last updated."""

eval_report_html_error_message = """expected HTML elements were not found in the
evaluation report page. The page may have changed since this web scraper was 
last updated."""

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
  missing: str
  @override
  def message(self) -> str:
    return eval_report_html_error_message + \
      f"\nMissing: {self.missing}" + \
      "\nResponse text:\n" + self.res_text
  
def parse_response(response: Response) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')

  cookie = parse_cookie(response.cookies)
  
  question_elements = soup.find_all(name="td", attrs={'headers': 'QUESTION'})
  sections: list[ScoreSection] = []
  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[0:9]:
    question_scores: list[int] = []
    for i in range(7):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(response.text, f"Section 0, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[9:14]:
    question_scores: list[int] = []
    for i in range(4):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(response.text, f"Section 1, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[14:20]:
    question_scores: list[int] = []
    for i in range(3):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(response.text, f"Section 2, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  grade_names = ["A", "B", "C", "D", "F", "Credit, No Credit, Audit"]
  grades: list[int] = []
  for grade_name in grade_names:
    grade_name_el = soup.find(name="td", string=grade_name)
    if grade_name_el is None:
      raise HTMLError(response.text, f"Grade name element for '{grade_name}'")
    grade_count_el = grade_name_el.find_next_sibling(name="td")
    if grade_count_el is None:
      raise HTMLError(response.text, f"Grade count element for '{grade_name}'")
    grade_count = grade_count_el.text
    grades.append(int(grade_count))

  return Output(
    cookie=cookie,
    score_sections=sections,
    expected_grades=grades,
  )

def parse_response2(res_text: str, cookies: RequestsCookieJar) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')

  cookie = parse_cookie(cookies)
    
  question_elements = soup.find_all(name="td", attrs={'headers': 'QUESTION'})
  sections: list[ScoreSection] = []
  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[0:9]:
    question_scores: list[int] = []
    for i in range(7):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(res_text, f"Section 0, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[9:14]:
    question_scores: list[int] = []
    for i in range(4):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(res_text, f"Section 1, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  questions: list[EvalReportQuestion] = []
  for question_element in question_elements[14:20]:
    question_scores: list[int] = []
    for i in range(3):
      headers = f'COL{i+1}'
      score_el = question_element.find_next_sibling(name="td", attrs={'headers': headers})
      if score_el is None:
        raise HTMLError(res_text, f"Section 2, row {i}, headers '{headers}'")
      score = int(score_el.text)
      question_scores.append(score)
    questions.append(EvalReportQuestion(question_scores))
  sections.append(ScoreSection(questions))

  grade_names = ["A", "B", "C", "D", "F", "Credit, No Credit, Audit"]
  grades: list[int] = []
  for grade_name in grade_names:
    grade_name_el = soup.find(name="td", string=grade_name)
    if grade_name_el is None:
      raise HTMLError(res_text, f"Grade name element for '{grade_name}'")
    grade_count_el = grade_name_el.find_next_sibling(name="td")
    if grade_count_el is None:
      raise HTMLError(res_text, f"Grade count element for '{grade_name}'")
    grade_count = grade_count_el.text
    grades.append(int(grade_count))

  return Output(
    cookie=cookie,
    score_sections=sections,
    expected_grades=grades,
  )
