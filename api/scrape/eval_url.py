from dataclasses import dataclass

# Example absolute url: https://orapp.hunter.cuny.edu/ords/f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
# We only store the relative path: f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
@dataclass
class EvalUrl:
  rel_path: str

  def absolute(self) -> str:
    return "https://orapp.hunter.cuny.edu/ords/" + self.rel_path