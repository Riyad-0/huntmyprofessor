

from dataclasses import dataclass

from bs4 import BeautifulSoup
from requests.sessions import RequestsCookieJar

from scrape.data import Data
from scrape.parse_cookie import parse_cookie
from scrape.course_search.parse_response import CourseSection, PaginateCodes, parse_course_sections, parse_paginate_codes

@dataclass
class Output():
  cookie: str | None
  course_sections: list[CourseSection]
  paginate_codes: PaginateCodes | None

def parse_response(res_text: str, cookies: RequestsCookieJar, data: Data) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
  cookie = parse_cookie(cookies)
  output = parse_course_sections(soup=soup, data=data)
  paginate_codes = parse_paginate_codes(soup=soup, res_text=res_text)
  return Output(
    cookie=cookie,
    course_sections=output.course_sections,
    paginate_codes=paginate_codes,
  )