from dataclasses import dataclass

from bs4 import BeautifulSoup

from .input import Input
from .send_request import Response
from typing import Any

@dataclass
class Output():
  courses: list[Any]

def parse_response(response: Response, input: Input) -> Output:
  soup = BeautifulSoup(response.text, 'html.parser')
  courses = [course_element.text for course_element in soup.find_all(attrs={'headers': 'COURSE'})]
  return Output(courses=courses)
