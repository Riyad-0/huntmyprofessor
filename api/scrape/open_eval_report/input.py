from dataclasses import dataclass

@dataclass
class Input():
  cookie: str

  # Relative path; should be prefixed by 'https://orapp.hunter.cuny.edu/ords/'.
  url: str
