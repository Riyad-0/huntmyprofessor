from dataclasses import dataclass

from bs4 import BeautifulSoup

from .input import Input
from typing import Any

@dataclass
class Output():
  courses: list[Any]

def parse_response(res_text: str, input: Input) -> Output:
  soup = BeautifulSoup(res_text, 'html.parser')
  courses = [course_element.text for course_element in soup.find_all(attrs={'headers': 'COURSE'})]
  return Output(courses=courses)
