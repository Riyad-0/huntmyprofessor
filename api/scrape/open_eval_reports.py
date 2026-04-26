from dataclasses import dataclass
from typing import Generator
import requests

# from scrape import course_search, fetch_max_rows
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
#   cookie = course_search_output.cookie
#   eval_reports: list[EvalReport] = []
#   match course_search_output.parse_result:
#     case Parsed(course_sections):
#       open_eval_reports(s, cookie=cookie, course_sections=course_sections):
#     case NeedsPaginate(paginate_codes):
#       did_fetch_max_rows = True
#       output = fetch_max_rows(
#         s,
#         cookie=cookie,
#         p_instance=course_search_output.p_instance,
#         p_page_submission_id=course_search_output.p_page_submission_id,
#         paginate_codes=paginate_codes
#       )
#       if output.cookie is not None:
#         cookie = output.cookie
#       course_sections = output.course_sections
#       l = 0
#       for output in open_eval_reports(s, cookie=cookie, course_sections=course_sections):
#         if output.cookie is not None:
#           cookie = output.cookie
#         eval_report = output.eval_report
#         eval_reports.append(eval_report)
#         data.add(eval_report)
#         data.write()
#         data.write_json()
#         l += 1
#         if l >= 30:
#           break

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

