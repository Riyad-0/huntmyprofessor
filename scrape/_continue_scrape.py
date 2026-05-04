import time

from httpx import AsyncClient, TimeoutException
from httpx_limiter import AsyncRateLimitedTransport, Rate # type: ignore
from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter # type: ignore
from scrape import _parse_course_search_page
from scrape._cookie_name import cookie_name
from scrape._course_search import course_search
from scrape._data import Data
from scrape._error import MyError
from scrape._eval_report import EvalReport
from scrape._log import log
from scrape._open_eval_reports import open_eval_reports
from scrape._select_dept import select_dept
from scrape._select_subject import select_subject

async def continue_scrape(
  course_search_page: _parse_course_search_page.CourseSearchPage,
  cookie_value: str,
  data: Data,
  limit: int | None = None,
):
  cookies={cookie_name: cookie_value}
  limiter = AiolimiterAsyncLimiter.create(Rate.create(magnitude=1, duration=0.1))
  async with AsyncClient(
    cookies=cookies,
    follow_redirects=True,
    transport=AsyncRateLimitedTransport.create(limiter=limiter),
  ) as client:
    t = time.time()
    count = await continue_scrape_inner(client, course_search_page, data, limit)
    dt = time.time() - t
    m, s = divmod(dt, 60)
    h, m = divmod(m, 60)
    duration = f'{round(s)}s'
    if h > 0 or m > 0:
      duration = f'{int(m)}m {duration}'
    if h > 0:
      duration = f'{int(h)}h {duration}'
    log.info(f'Collected {count} evals in {duration}')

async def continue_scrape_inner(
  client: AsyncClient,
  course_search_page: _parse_course_search_page.CourseSearchPage,
  data: Data,
  limit: int | None,
) -> int:
  output = await select_dept(client, course_search_page)
  output = await select_subject(client, course_search_page)
  course_number_options = output.course_number_options
  did_fetch_max_rows = False
  errors = 0
  count = 0
  # unknown_exception: Exception | None = None
  for course_num in course_number_options:
    try:
      if limit is not None and limit == 0:
        break
      search_output = await course_search(
        client,
        course_search_page,
        data,
        department="CSCI-HTR",
        subject="CSCI",
        course_num=course_num,
        did_fetch_max_rows=did_fetch_max_rows,
      )
      # cookie = search_output.cookie
      # match search_output.parse_result:
      #   case Parsed(course_sections):
      #     evals_iter = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
      #   case NeedsPaginate(paginate_codes):
      #     did_fetch_max_rows = True
      #     output = fetch_max_rows(
      #       s,
      #       cookie=cookie,
      #       p_instance=search_output.p_instance,
      #       p_page_submission_id=search_output.p_page_submission_id,
      #       paginate_codes=paginate_codes
      #     )
      #     if output.cookie is not None:
      #       cookie = output.cookie
      #     course_sections = output.course_sections
      #     evals_iter = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
      eval_reports_output = await open_eval_reports(
        client,
        data=data,
        course_search_output=search_output,
        did_fetch_max_rows=did_fetch_max_rows,
        limit=limit,
      )
      did_fetch_max_rows = eval_reports_output.did_fetch_max_rows
      eval_reports: list[EvalReport] = []
      # l = 0
      i = 0
      for aoutput in eval_reports_output.outputs:
        # if output.cookie is not None:
          # cookie = output.cookie
        output = await aoutput
        eval_report = output.eval_report
        eval_reports.append(eval_report)
        data.add(eval_report)
        data.write()
        data.write_json(str(data.path))
        log.debug(f"Collected eval: {eval_report.formatted()}")
        i += 1
        count += 1
      if limit is not None:
        limit = max(limit - i, 0)
    except Exception as e:
      errors += 1
      if isinstance(e, MyError):
        log.error(f'failed on: CSCI {course_num}; {e.message()}')
      elif isinstance(e, TimeoutException):
        log.error(f'failed on: CSCI {course_num}; timed out; {e}')
      else:
        log.error(f'failed on: CSCI {course_num}; {e}')
        raise e
      if errors == 5:
        return count
        # if unknown_exception is None:
        #   return
        # else:
        #   raise unknown_exception
  return count