from dataclasses import dataclass

from scrape.data import fetch_data

@dataclass
class GradeFraction:
  grade_recipient_count: int
  student_count: int

  def add(self, other: GradeFraction):
    self.grade_recipient_count += other.grade_recipient_count
    self.student_count += other.student_count

  def compute(self) -> float:
    if self.student_count == 0:
      return 0
    return self.grade_recipient_count / self.student_count

@dataclass
class Professor:
  name: str
  grade_fraction: GradeFraction

def query():
  m: dict[str, GradeFraction] = {}
  data = fetch_data()
  evals = data.deserialize()
  for eval_report in evals:
    student_count = 0
    for n in eval_report.page.expected_grades:
      student_count += n
    grade_recipient_count = eval_report.page.expected_grades[0]

    frac = GradeFraction(
      grade_recipient_count=grade_recipient_count,
      student_count=student_count,
    )
    
    if eval_report.professor in m:
      m[eval_report.professor].add(frac)
    else:
      m[eval_report.professor] = frac
  
  l: list[Professor] = []
  for name, grade_fraction in m.items():
    l.append(Professor(
      name=name,
      grade_fraction=grade_fraction,
    ))
  l.sort(key=lambda x: x.grade_fraction.compute(), reverse=True)
  s = ""
  for x in l:
    s += f"{x.name}: {x.grade_fraction.compute():.0%} ({x.grade_fraction.grade_recipient_count}/{x.grade_fraction.student_count})\n"
  print(s)

query()
