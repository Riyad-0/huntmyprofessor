

from dataclasses import dataclass

from bs4 import BeautifulSoup

from scrape.parse_cookie import parse_cookie
from scrape.course_search.parse_response import CourseSection, PaginateCodes, parse_course_sections, parse_paginate_codes

from .send_request import Response

@dataclass
class Output():
  cookie: str | None
  course_sections: list[CourseSection]
  paginate_codes: PaginateCodes | None

def parse_response(response: Response) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
  cookie = parse_cookie(response.cookies)
  course_sections = parse_course_sections(soup)
  paginate_codes = parse_paginate_codes(soup=soup, res_text=response.text)
  return Output(
    cookie=cookie,
    course_sections=course_sections,
    paginate_codes=paginate_codes,
  )