

from dataclasses import dataclass

from bs4 import BeautifulSoup
from httpx import Cookies

from scrape._data import Data
from scrape._parse_cookie import parse_cookie
from scrape._course_search.parse_response import CourseSection, PaginateCodes, parse_course_sections, parse_paginate_codes

@dataclass
class Output():
  cookie: str | None
  course_sections: list[CourseSection]
  paginate_codes: PaginateCodes | None

def parse_response(res_text: str, cookies: Cookies, data: Data) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
  cookie = parse_cookie(cookies)
  output = parse_course_sections(soup=soup, data=data)
  paginate_codes = parse_paginate_codes(soup=soup, res_text=res_text)
  return Output(
    cookie=cookie,
    course_sections=output.course_sections,
    paginate_codes=paginate_codes,
  )