from dataclasses import dataclass
from typing import Any

from fastavro import writer, reader, parse_schema

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
  i = l.index(item)
  if i == -1:
    i = len(l)
    l.append(item)
  return i

@dataclass
class SchemaDB:
  courses: list[str] = []
  semesters: list[str] = []
  professors: list[str] = []
  urls: list[str] = []

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
  data: bytearray = bytearray()
  cell: int = 0
  cell_num_bits: int = 0

  def append(self, x: int, num_bits: int):
    cell_bits_left = 8 - self.cell_num_bits
    n = min(cell_bits_left, num_bits)
    bits = lbits(x, n)
    x >>= n
    num_bits = max(num_bits - n, 0)
    self.cell += bits << self.cell_num_bits
      
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
      if self.cell_num_bits == 8:
        self.data.append(self.cell)
        self.cell = 0
        self.cell_num_bits = 0
        
  def finish(self) -> bytearray:
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
    
def serialize(eval_reports: list[EvalReport]):
  schema_db = SchemaDB()
  for eval_report in eval_reports:
    if eval_report.semester is None or eval_report.professor is None:
      continue
    course = schema_db.add_course(eval_report.course)
    semester = schema_db.add_semester(eval_report.semester)
    professor = schema_db.add_professor(eval_report.professor)

    bit_packer = BitPacker()
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

    with open("a.txt", "wb") as f:
      f.write(bit_packer.finish())

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



def deserialize(schema_db: SchemaDB) -> list[EvalReport]:
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


s = {
  'name': 'EvalReport',
  'namespace': 'test',
  'type': 'record',
  'fields': [
    {'name': 'course', 'type': 'string'},
    {'name': 'semester', 'type': ''},
    {'name': 'professor', 'type': ''},
    {'name': 'page', 'type': ''},
  ],
}
g = 4035 << 50
schema = {
  'doc': 'A weather reading.',
  'name': 'Weather',
  'namespace': 'test',
  'type': 'record',
  'fields': [
    {'name': 'station', 'type': 'string'},
    {'name': 'time', 'type': 'long'},
    {'name': 'temp', 'type': 'int'},
  ],
}
parsed_schema = parse_schema(schema)

# 'records' can be an iterable (including generator)
records = [
  {u'station': u'011990-99999', u'temp': 0, u'time': 1433269388},
  {u'station': u'011990-99999', u'temp': 22, u'time': 1433270389},
  {u'station': u'011990-99999', u'temp': -11, u'time': 1433273379},
  {u'station': u'012650-99999', u'temp': 111, u'time': 1433275478},
]

# Writing
with open('weather.avro', 'wb') as out:
  writer(out, parsed_schema, records)

# Reading
with open('weather.avro', 'rb') as fo:
  for record in reader(fo):
    print(record)