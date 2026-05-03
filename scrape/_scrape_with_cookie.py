from typing import Literal

from httpx import AsyncClient
from httpx_limiter import AsyncRateLimitedTransport, Rate # type: ignore
from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter # type: ignore
from scrape._continue_scrape import continue_scrape_inner
from scrape._cookie_name import cookie_name
from scrape._data import Data
from scrape._error import MyError
from scrape._log import log
from scrape._open_course_search_page import open_course_search_page

async def scrape_with_cookie(
  cookie_value: str,
  data: Data,
) -> Literal['success', 'fail']:
  cookies={cookie_name: cookie_value}
  limiter = AiolimiterAsyncLimiter.create(Rate.create(magnitude=1, duration=0.1))
  async with AsyncClient(
    cookies=cookies,
    follow_redirects=True,
    transport=AsyncRateLimitedTransport.create(limiter=limiter),
  ) as client:
    try:
      course_search_page = await open_course_search_page(client, cookie=cookie_name + '=' + cookie_value)
    except Exception as e:
      if isinstance(e, MyError):
        log.info('error: could not use saved cookie; ' + e.message())
        return 'fail'
      else:
        raise e

    await continue_scrape_inner(client, course_search_page, data)
    return 'success'
