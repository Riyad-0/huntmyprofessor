from dataclasses import dataclass

from scrape._eval_url import EvalUrl

# Example absolute url: https://orapp.hunter.cuny.edu/ords/f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
# Url always starts with https://orapp.hunter.cuny.edu/ords/f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:
# Ends with something like 1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
# We only store the end.

pattern = "::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:"

@dataclass
class EvalUrlCode:
  code: str

  # Takes a relative path of the form f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
  @staticmethod
  def from_url(url: EvalUrl) -> 'EvalUrlCode':
    rel_path = url.rel_path
    i = rel_path.find(pattern)
    if i == -1:
      raise ValueError()
    end = rel_path[i+len(pattern):]
    return EvalUrlCode(code=end)

  def build(self, p_instance: str) -> str:
    return f"https://orapp.hunter.cuny.edu/ords/f?p=116:5:{p_instance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:{self.code}"