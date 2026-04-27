from dataclasses import dataclass

from scrape.eval_url_code import EvalUrlCode

@dataclass
class EvalReport:
  course: str
  section: str | None
  semester: str
  professor: str
  page: EvalReportPage

  def formatted(self) -> str:
    return f"{self.course} Sec: {self.section}, {self.semester}, {self.professor}"

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
