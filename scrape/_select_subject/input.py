from dataclasses import dataclass

from scrape import _parse_course_search_page

@dataclass
class Input():
  ajax_identifier: str
  cookie: str
  p_instance: str
  p_page_submission_id: str
  p_page_items_protected: str

  @staticmethod
  def from_course_search_page(
    output: _parse_course_search_page.CourseSearchPage,
  ) -> 'Input':
    return Input(
      ajax_identifier=output.subject_ajax_identifier,
      cookie=output.cookie,
      p_instance=output.p_instance,
      p_page_submission_id=output.p_page_submission_id,
      p_page_items_protected=output.p_page_items_protected,
    )
