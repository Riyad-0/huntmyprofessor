from dataclasses import dataclass

from scrape.eval_url import EvalUrl

@dataclass
class Input():
  cookie: str
  url: EvalUrl
