from dataclasses import dataclass

from scrape.data import Data

from .. import open_course_search_page

@dataclass
class Input():
  cookie: str
  p_instance: str
  p_page_submission_id: str
  p_page_items_protected: str
  data: Data
  department: str
  subject: str
  course_num: str

  @staticmethod
  def from_open_course_search_page(
    output: open_course_search_page.Output,
    data: Data,
    department: str,
    subject: str,
    course_num: str,
  ) -> Input:
    return Input(
      cookie=output.cookie,
      p_instance=output.p_instance,
      p_page_submission_id=output.p_page_submission_id,
      p_page_items_protected=output.p_page_items_protected,
      data=data,
      department=department,
      subject=subject,
      course_num=course_num,
    )
