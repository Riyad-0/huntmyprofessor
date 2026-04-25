from dataclasses import dataclass
from typing import Generator
import requests

from scrape.eval_url_code import EvalUrlCode
from scrape.eval_report import EvalReport, EvalReportPage
from scrape.open_eval_report import open_eval_report2
from scrape.course_search.parse_response import CourseSection

@dataclass
class Output:
  cookie: str
  eval_reports: list[EvalReport]

def open_eval_reports(
  s: requests.Session,
  cookie: str,
  course_sections: list[CourseSection],
) -> Output:
  eval_reports: list[EvalReport] = []
  for course_section in course_sections:
    output = open_eval_report2(s, cookie=cookie, course_section=course_section)
    if output.cookie is not None:
      cookie = output.cookie
    eval_reports.append(EvalReport(
      course=course_section.course,
      semester=course_section.semester,
      professor=course_section.professor,
      page=EvalReportPage(
        url=EvalUrlCode.from_url(course_section.url),
        score_sections=output.score_sections,
        expected_grades=output.expected_grades
      ),
    ))
  return Output(
    cookie=cookie,
    eval_reports=eval_reports,
  )

@dataclass
class Output2:
  cookie: str | None
  eval_report: EvalReport

def eval_reports_iter(
  s: requests.Session,
  cookie: str,
  course_sections: list[CourseSection],
) -> Generator[Output2]:
  for course_section in course_sections:
    output = open_eval_report2(s, cookie=cookie, course_section=course_section)
    yield Output2(
      cookie=output.cookie,
      eval_report=EvalReport(
        course=course_section.course,
        semester=course_section.semester,
        professor=course_section.professor,
        page=EvalReportPage(
          url=EvalUrlCode.from_url(course_section.url),
          score_sections=output.score_sections,
          expected_grades=output.expected_grades
        ),
      ),
    )

