import asyncio
from dataclasses import dataclass
from typing import Awaitable
from httpx import AsyncClient

from scrape._eval_url_code import EvalUrlCode
from scrape._eval_report import EvalReport, EvalReportPage
from scrape._open_eval_report import open_eval_report
from scrape._course_search.parse_response import CourseSection
from collections.abc import Iterator

@dataclass
class Output:
  cookie: str | None
  eval_report: EvalReport

async def open_eval_reports_helper(
  client: AsyncClient,
  cookie: str,
  course_sections: list[CourseSection],
  limit: int | None,
) -> Iterator[Awaitable[Output]]:
  if limit is not None:
    course_sections = course_sections[:limit]
  async with asyncio.TaskGroup() as tg:
    tasks = [
      tg.create_task(open_eval_report_helper(
        client,
        cookie=cookie,
        course_section=course_section
      ))
      for course_section in course_sections
    ]
  return asyncio.as_completed(tasks)
  
async def open_eval_report_helper(
  client: AsyncClient,
  cookie: str,
  course_section: CourseSection,
) -> Output:
  output = await open_eval_report(client, cookie=cookie, course_section=course_section)
  return Output(
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