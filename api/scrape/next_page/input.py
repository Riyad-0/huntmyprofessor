from dataclasses import dataclass

from scrape.course_search.parse_response import PaginateCodes

# from .. import course_search

@dataclass
class Input():
  cookie: str
  p_instance: str
  p_page_submission_id: str
  paginate_codes: PaginateCodes

  # @staticmethod
  # def from_course_search(
  #   output: course_search.Output,
  # ) -> Input:
  #   return Input(
  #     p_instance=output.p_instance,
  #     p_page_submission_id=output.p_page_submission_id,
  #     cookie=output.cookie,
  #     paginate_codes=output.paginate_codes,
  #   )
