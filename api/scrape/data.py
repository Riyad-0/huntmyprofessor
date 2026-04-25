from dataclasses import dataclass, field
import json
import os
from typing import Any

from scrape.eval_url_code import EvalUrlCode
from scrape.eval_report import EvalReport, EvalReportPage, EvalReportQuestion, ScoreSection

# Schema
# 1124 bits (141 bytes)
# 14 bits course
# 10 bits semester
# 12 bits professor

# 1088 bits page

# 18 bits url
# Url always starts with https://orapp.hunter.cuny.edu/ords/f?p=116:5:{pInstance}::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:
# Ends with something like 1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC
# Only store the end.

# 1010 bits score_sections
# 630 bits 9 questions - 7 options
# 200 bits 5 questions - 4 options
# 180 bits 6 questions - 3 options
# (10 bits option)

# 60 bits expected_grades - 6 options
# 10 bits option

dir_name = os.path.dirname(__file__)
schema_path = os.path.join(dir_name, "schema.json")
evals_path = os.path.join(dir_name, "evals.txt")
json_path = os.path.join(dir_name, "evals.json")

# @dataclass
# class Output:
#  cookie: str
#  eval_reports: list[EvalReport]

# @dataclass
# class EvalReport:
#  course: str
#  semester: str | None
#  professor: str | None
#  page: EvalReportPage | None

# @dataclass
# class EvalReportPage:
#  url: str
#  score_sections: list[ScoreSection]
#  expected_grades: list[int]

# @dataclass
# class ScoreSection:
#  questions: list[EvalReportQuestion]

# @dataclass
# class EvalReportQuestion:
#   scores: list[int]

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
  schema_db = data.schema_db
  evals = data.evals
  bit_packer = BitPacker(data=evals)
  for eval_report in eval_reports:
    course = schema_db.add_course(eval_report.course)
    semester = schema_db.add_semester(eval_report.semester)
    professor = schema_db.add_professor(eval_report.professor)

    bit_packer.append(course, 14)
    bit_packer.append(semester, 10)
    bit_packer.append(professor, 12)
    url = schema_db.add_url(eval_report.page.url.code)
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

  def skip(self, num_bits: int):
    self.cell_index += num_bits // 8
    self.pop(num_bits=num_bits % 8)



def deserialize() -> list[EvalReport]:
  with open(schema_path) as f:
    schema_json = json.load(f)
    schema_db = SchemaDB(
      courses=schema_json["courses"],
      semesters=schema_json["semesters"],
      professors=schema_json["professors"],
      urls=schema_json["urls"],
    )
  with open(evals_path, "rb") as f:
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
          url=EvalUrlCode(url),
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

@dataclass
class Data:
  schema_db: SchemaDB
  evals: bytearray

  def contains(
    self,
    course: str,
    semester: str,
    professor: str,
  ) -> bool:
    try:
      schema_db = self.schema_db
      evals = self.evals
      course_i = schema_db.courses.index(course)
      semester_i = schema_db.semesters.index(semester)
      professor_i = schema_db.professors.index(professor)

      unpacker = BitUnpacker(evals)      
      while len(evals) - unpacker.cell_index >= 141:
        found_course_i = unpacker.pop(14)
        found_semester_i = unpacker.pop(10)
        found_professor_i = unpacker.pop(12)
        if (
          found_course_i == course_i and
          found_semester_i == semester_i and
          found_professor_i == professor_i
        ):
          return True
        unpacker.skip(141*8 - 14 - 10 - 12)
      return False
    except ValueError:
      return False
  
  def add(
    self,
    eval_report: EvalReport,
  ):
    self.add_all([eval_report])
    
  def add_all(
    self,
    eval_reports: list[EvalReport],
  ):
    schema_db = self.schema_db
    evals = self.evals
    bit_packer = BitPacker(data=evals)
    for eval_report in eval_reports:
      course = schema_db.add_course(eval_report.course)
      semester = schema_db.add_semester(eval_report.semester)
      professor = schema_db.add_professor(eval_report.professor)

      bit_packer.append(course, 14)
      bit_packer.append(semester, 10)
      bit_packer.append(professor, 12)
      url = schema_db.add_url(eval_report.page.url.code)
      bit_packer.append(url, 18)
      for section in eval_report.page.score_sections:
        for question in section.questions:
          for score in question.scores:
            bit_packer.append(score, 10)
      for score in eval_report.page.expected_grades:
        bit_packer.append(score, 10)
      bit_packer.finish_byte()

  def write(self):
    with (
      open(schema_path, "w") as schema_file,
      open(evals_path, "wb") as evals_file,
    ):
      json.dump(self.schema_db.__dict__, schema_file, indent=2)
      evals_file.write(self.evals)
  
  def deserialize(self) -> list[EvalReport]:
    schema_db = self.schema_db
    evals = self.evals
    unpacker = BitUnpacker(evals)
    eval_reports: list[EvalReport] = []
    
    while len(evals) - unpacker.cell_index >= 141:
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
          url=EvalUrlCode(url),
          score_sections=sections,
          expected_grades=expected_grades,
        ),
      ))
    return eval_reports

  def write_json(self):
    with open(json_path, "w") as f:
      json.dump(self.deserialize(), f, indent=2, default=json_default)
# type Data = tuple[SchemaDB, bytearray]

def fetch_schema() -> SchemaDB:
  try:
    with open(schema_path) as f:
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
    with open(evals_path, "rb") as f:
      return bytearray(f.read())
  except FileNotFoundError:
    return bytearray()

def fetch_data() -> Data:
  return Data(fetch_schema(), fetch_evals())

def test():
  parsed = [
    EvalReport(
      course="CSCI 49900",
      semester="Fall 2024",
      professor="WASHBURN, ALEXANDER",
      page=EvalReportPage(
        url=EvalUrlCode("f?p=116:5:0000000::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC"),        score_sections=[
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
        url=EvalUrlCode("f?p=116:5:0000000::::P5_STRM,P5_CLASS_NBR,P5_TECODE,P5_TYPE:1079,946,00,N&cs=174A380F03ABCA947D15A5D7D1C174FEC"),
        score_sections=[
          fake_section(9, 7),
          fake_section(5, 4),
          fake_section(6, 3),
        ],
        expected_grades=[0, 0, 0, 0, 0, 0],
      ),
    ),
  ]
  data = fetch_data()
  a: list[EvalReport] = []
  for e in parsed:
    if not data.contains(e.course, e.semester, e.professor):
      a.append(e)
  serialize(data=data, eval_reports=a)
  with open(schema_path, "w") as f:
    json.dump(data.schema_db.__dict__, f, indent=2)
  with open(evals_path, "wb") as f:
    f.write(data.evals)
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

# test()