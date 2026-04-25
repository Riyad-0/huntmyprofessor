from dataclasses import dataclass

from scrape.eval_url_code import EvalUrlCode

@dataclass
class EvalReport:
  course: str
  semester: str
  professor: str
  page: EvalReportPage

@dataclass
class EvalReportPage:
  url: EvalUrlCode
  score_sections: list[ScoreSection]
  expected_grades: list[int]

@dataclass
class ScoreSection:
  questions: list[EvalReportQuestion]

@dataclass
class EvalReportQuestion:
  scores: list[int]
