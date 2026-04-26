from .. import open_login_page

class Input(open_login_page.Output):
  def __init__(
    self,
    output: open_login_page.Output,
    username: str,
    password: str
  ):
    super().__init__(
      cookie=output.cookie,
      p_instance=output.p_instance,
      p_page_items_protected=output.p_page_items_protected,
      p_page_submission_id=output.p_page_submission_id
    )
    self.username = username
    self.password = password
