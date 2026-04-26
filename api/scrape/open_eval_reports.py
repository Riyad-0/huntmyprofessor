from dataclasses import dataclass
from typing import Generator
import requests

# from scrape import course_search
from scrape.eval_url_code import EvalUrlCode
from scrape.eval_report import EvalReport, EvalReportPage
from scrape.open_eval_report import open_eval_report
from scrape.course_search.parse_response import CourseSection

@dataclass
class Output:
  cookie: str | None
  eval_report: EvalReport

# def open_eval_reports_from_search(
#   s: requests.Session,
#   course_search_output: course_search.Output
# ) -> Generator[Output]:
#   open_eval_reports()

def open_eval_reports(
  s: requests.Session,
  cookie: str,
  course_sections: list[CourseSection],
) -> Generator[Output]:
  for course_section in course_sections:
    output = open_eval_report(s, cookie=cookie, course_section=course_section)
    yield Output(
      cookie=output.cookie,
      eval_report=EvalReport(
        course=course_section.course,
        section=course_section.section,
        semester=course_section.semester,
        professor=course_section.professor,
        page=EvalReportPage(
          url=EvalUrlCode.from_url(course_section.url),
          score_sections=output.score_sections,
          expected_grades=output.expected_grades
        ),
      ),
    )

