from dataclasses import dataclass

from .. import log_in

@dataclass
class Input():
  cookie: str
  p_instance: str
  p_page_submission_id: str
  p_page_items_protected: str

  @staticmethod
  def from_sign_in(
    output: log_in.Output,
  ) -> Input:
    return Input(
      cookie=output.cookie,
      p_instance=output.p_instance,
      p_page_submission_id=output.p_page_submission_id,
      p_page_items_protected=output.p_page_items_protected,
    )
