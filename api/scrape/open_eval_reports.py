from dataclasses import dataclass
import requests

from scrape.open_eval_report import open_eval_report
from scrape.open_eval_report.parse_response import ScoreSection
from scrape.course_search.parse_response import CourseSection

@dataclass
class Output:
  cookie: str
  eval_reports: list[EvalReport]

@dataclass
class EvalReport:
  course: str
  semester: str
  professor: str
  page: EvalReportPage

@dataclass
class EvalReportPage:
  url: str
  score_sections: list[ScoreSection]
  expected_grades: list[int]

def open_eval_reports(
  s: requests.Session,
  cookie: str,
  course_sections: list[CourseSection],
) -> Output:
  eval_reports: list[EvalReport] = []
  for course_section in course_sections:
    output = open_eval_report(s, cookie=cookie, url=course_section.url)
    cookie = output.cookie
    eval_reports.append(EvalReport(
      course=course_section.course,
      semester=course_section.semester,
      professor=course_section.professor,
      page=EvalReportPage(
        url=course_section.url,
        score_sections=output.score_sections,
        expected_grades=output.expected_grades
      ),
    ))
  return Output(
    cookie=cookie,
    eval_reports=eval_reports,
  )
