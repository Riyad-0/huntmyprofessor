from dataclasses import dataclass
from typing import Awaitable
from collections.abc import Iterator

from httpx import AsyncClient

from scrape._data import Data
from scrape import _open_eval_reports_helper
from scrape._course_search.parse_response import NeedsPaginate, Parsed
from scrape import _course_search
from scrape._fetch_max_rows import fetch_max_rows


@dataclass
class Output:
  outputs: Iterator[Awaitable[_open_eval_reports_helper.Output]]
  did_fetch_max_rows: bool
  cookie: str

async def open_eval_reports(
  client: AsyncClient,
  course_search_output: _course_search.Output,
  data: Data,
  did_fetch_max_rows: bool,
  limit: int | None,
):
  cookie = course_search_output.cookie
  match course_search_output.parse_result:
    case Parsed(course_sections):
      outputs = await _open_eval_reports_helper.open_eval_reports_helper(
        client,
        cookie=cookie,
        course_sections=course_sections,
        limit=limit
      )
    case NeedsPaginate(paginate_codes):
      did_fetch_max_rows = True
      output = await fetch_max_rows(
        client,
        data=data,
        cookie=cookie,
        p_instance=course_search_output.p_instance,
        p_page_submission_id=course_search_output.p_page_submission_id,
        paginate_codes=paginate_codes
      )
      if output.cookie is not None:
        cookie = output.cookie
      course_sections = output.course_sections
      outputs = await _open_eval_reports_helper.open_eval_reports_helper(
        client,
        cookie=cookie,
        course_sections=course_sections,
        limit=limit,
      )
  return Output(
    outputs=outputs,
    did_fetch_max_rows=did_fetch_max_rows,
    cookie=cookie,
  )