from dataclasses import dataclass, field
import json
from typing import Any

# Schema
# 1124 bits (141 bytes)
# 14 bits course
# 10 bits semester
# 12 bits professor

# 1088 bits page

# 18 bits url

# 1010 bits score_sections
# 630 bits 9 questions - 7 options
# 200 bits 5 questions - 4 options
# 180 bits 6 questions - 3 options
# (10 bits option)

# 60 bits expected_grades - 6 options
# 10 bits option


@dataclass
class Output:
 cookie: str
 eval_reports: list[EvalReport]

@dataclass
class EvalReport:
 course: str
 semester: str | None
 professor: str | None
 page: EvalReportPage | None

@dataclass
class EvalReportPage:
 url: str
 score_sections: list[ScoreSection]
 expected_grades: list[int]

@dataclass
class ScoreSection:
 questions: list[EvalReportQuestion]

@dataclass
class EvalReportQuestion:
  scores: list[int]

def add[T](l: list[T], item: T) -> int:
  try:
    return l.index(item)
  except ValueError:
    i = len(l)
    l.append(item)
    return i

@dataclass
class SchemaDB:
  courses: list[str] = field(default_factory=list[str])
  semesters: list[str] = field(default_factory=list[str])
  professors: list[str] = field(default_factory=list[str])
  urls: list[str] = field(default_factory=list[str])

  def add_course(self, course: str) -> int:
    return add(self.courses, course)

  def add_semester(self, semester: str) -> int:
    return add(self.semesters, semester)

  def add_professor(self, professor: str) -> int:
    return add(self.professors, professor)
  
  def add_url(self, url: str) -> int:
    return add(self.urls, url)
  
@dataclass
class BitPacker:
  data: bytearray
  cell: int = 0
  cell_num_bits: int = 0

  def append(self, x: int, num_bits: int):
    cell_bits_left = 8 - self.cell_num_bits
    n = min(cell_bits_left, num_bits)
    bits = lbits(x, n)
    x >>= n
    num_bits = max(num_bits - n, 0)
    self.cell += bits << self.cell_num_bits
    self.cell_num_bits += n
      
    if self.cell_num_bits == 8:
      self.data.append(self.cell)
      self.cell = 0
      self.cell_num_bits = 0
    
    while num_bits > 0:
      n = min(num_bits, 8)
      bits = lbits(x, n)
      x >>= n
      num_bits = max(num_bits - n, 0)
      self.cell += bits << self.cell_num_bits
      self.cell_num_bits += n
      if self.cell_num_bits == 8:
        self.data.append(self.cell)
        self.cell = 0
        self.cell_num_bits = 0
  
  def finish_byte(self) -> bytearray:
    if self.cell_num_bits != 0:
      self.data.append(self.cell)
      self.cell = 0
      self.cell_num_bits = 0
    return self.data
        
  # def finish(self) -> bytearray:
  #   if self.cell_num_bits != 0:
  #     self.data.append(self.cell)
  #     self.cell = 0
  #     self.cell_num_bits = 0
  #   return self.data

# Get the lower `n` bits of `x`.
def lbits(x: int, n: int) -> int:
  return x & ((1 << n) - 1)

# Get the `n` bits of `x` starting from `start`.
def bitspan(x: int, n: int, start: int):
  return lbits(x >> start, n)
    
def serialize(
  data: Data,
  eval_reports: list[EvalReport],
):
  schema_db, evals = data
  bit_packer = BitPacker(data=evals)
  for eval_report in eval_reports:
    if eval_report.semester is None or eval_report.professor is None:
      continue
    course = schema_db.add_course(eval_report.course)
    semester = schema_db.add_semester(eval_report.semester)
    professor = schema_db.add_professor(eval_report.professor)

    bit_packer.append(course, 14)
    bit_packer.append(semester, 10)
    bit_packer.append(professor, 12)
    if eval_report.page is None:
      bit_packer.append((1 << 1088) - 1, 1088)
      # TODO: remove
      continue
    else:
      url = schema_db.add_url(eval_report.page.url)
      bit_packer.append(url, 18)
      for section in eval_report.page.score_sections:
        for question in section.questions:
          for score in question.scores:
            bit_packer.append(score, 10)
      for score in eval_report.page.expected_grades:
        bit_packer.append(score, 10)
    bit_packer.finish_byte()
  # return bit_packer.data

@dataclass
class BitUnpacker:
  data: bytes
  cell_index: int = 0
  cell_bit: int = 0

  def pop(self, num_bits: int) -> int:
    cell_bits_left = 8 - self.cell_bit
    n = min(cell_bits_left, num_bits)
    num_bits -= n
    cell = bitspan(self.data[self.cell_index], n, self.cell_bit)
    self.cell_bit += n
    if self.cell_bit == 8:
      self.cell_bit = 0
      self.cell_index += 1
    offset = n
    while num_bits > 0:
      n = min(num_bits, 8)
      num_bits -= n
      cell += lbits(self.data[self.cell_index], n) << offset
      offset += n
      self.cell_bit += n
      if self.cell_bit == 8:
        self.cell_bit = 0
        self.cell_index += 1
    return cell

  def finish_byte(self):
    if self.cell_bit > 0:
      self.cell_bit = 0
      self.cell_index += 1



def deserialize() -> list[EvalReport]:
  with open("schema.json") as f:
    schema_json = json.load(f)
    schema_db = SchemaDB(
      courses=schema_json["courses"],
      semesters=schema_json["semesters"],
      professors=schema_json["professors"],
      urls=schema_json["urls"],
    )
  with open("a.txt", "rb") as f:
    data = f.read()
    unpacker = BitUnpacker(data)
    eval_reports: list[EvalReport] = []
    
    while len(data) - unpacker.cell_index >= 141:
      course = schema_db.courses[unpacker.pop(14)]
      semester = schema_db.semesters[unpacker.pop(10)]
      professor = schema_db.professors[unpacker.pop(12)]
      url = schema_db.urls[unpacker.pop(18)]

      sections: list[ScoreSection] = []
      sections.append(pop_section(unpacker, 9, 7))
      sections.append(pop_section(unpacker, 5, 4))
      sections.append(pop_section(unpacker, 6, 3))
      expected_grades: list[int] = []
      for _ in range(6):
        expected_grades.append(unpacker.pop(10))
      unpacker.finish_byte()
      eval_reports.append(EvalReport(
        course,
        semester,
        professor,
        EvalReportPage(
          url,
          score_sections=sections,
          expected_grades=expected_grades,
        ),
      ))
    return eval_reports


def pop_section(
  unpacker: BitUnpacker,
  num_questions: int,
  num_options: int,
) -> ScoreSection:
  questions: list[EvalReportQuestion] = []
  for _ in range(num_questions):
    scores: list[int] = []
    for _ in range(num_options):
      score = unpacker.pop(10)
      scores.append(score)
    questions.append(EvalReportQuestion(scores))
  return ScoreSection(questions=questions)

# @dataclass
# class Data:
#   schema_db: SchemaDB
#   evals: bytearray\

type Data = tuple[SchemaDB, bytearray]

def fetch_schema() -> SchemaDB:
  try:
    with open("schema.json") as f:
      serialized = json.load(f)
      return SchemaDB(
        courses=serialized["courses"],
        semesters=serialized["semesters"],
        professors=serialized["professors"],
        urls=serialized["urls"],
      )
  except FileNotFoundError:
    return SchemaDB()
  
def fetch_evals() -> bytearray:
  try:
    with open("evals.txt", "rb") as f:
      return bytearray(f.read())
  except FileNotFoundError:
    return bytearray()

def fetch_data() -> Data:
  return fetch_schema(), fetch_evals()

def test():
  a = [
    EvalReport(
      course="CSCI 49900",
      semester="Fall 2024",
      professor="WASHBURN, ALEXANDER",
      page=EvalReportPage(
        url="f?p=0000:::::",
        score_sections=[
          fake_section(9, 7),
          fake_section(5, 4),
          fake_section(6, 3),
        ],
        expected_grades=[0, 0, 0, 0, 0, 0],
      ),
    ),
    EvalReport(
      course="CSCI 23500",
      semester="Spring 2023",
      professor="MARYASH, GENNADY",
      page=EvalReportPage(
        url="f?p=0000:::::",
        score_sections=[
          fake_section(9, 7),
          fake_section(5, 4),
          fake_section(6, 3),
        ],
        expected_grades=[0, 0, 0, 0, 0, 0],
      ),
    ),
  ]
  schema_db, evals = fetch_data()
  serialize(data=(schema_db, evals), eval_reports=a)
  with open("schema.json", "w") as f:
    json.dump(schema_db.__dict__, f, indent=2)
  with open("a.txt", "wb") as f:
    f.write(evals)
  b = deserialize()
  with open("b.json", "w") as f:
    json.dump(b, f, indent=2, default=json_default)

def fake_section(num_questions: int, num_options: int) -> ScoreSection:
  questions: list[EvalReportQuestion] = []
  for _ in range(num_questions):
    scores: list[int] = []
    for _ in range(num_options):
      scores.append(0)
    questions.append(EvalReportQuestion(scores))
  return ScoreSection(questions=questions)

def json_default(obj: Any):
  if hasattr(obj, "__dict__"):
      return obj.__dict__
  raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

test()