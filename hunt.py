import asyncio
from dataclasses import dataclass
import json
from logging import FileHandler, Formatter, StreamHandler
import logging
import os
from pathlib import Path
from typing import Any, Literal, override

from dotenv import load_dotenv
from httpx import AsyncClient

from scrape import Data, EvalReport, MyError, continue_scrape, fetch_data, log, log_in, read_saved_cookie_value, save_cookie_value

data_folder_name = 'data'
logs_folder_name = 'logs'
log_file_name = 'hunt.log'
workflow_file_name = 'scrape.yml'

async def main():
  try:
    await inner()
  except Exception as e:
    if isinstance(e, MyError):
      log.error(e.message())
    else:
      raise e

async def inner():
  init_log()
  dir_name = os.path.dirname(__file__)
  data_path = os.path.join(dir_name, data_folder_name)
  data = fetch_data(data_path)
  print(
    'HuntMyProfessor',
    '0. Quit',
    '1. Scrape',
    '2. Rank professors',
    '3. Rank courses',
    '4. Recent professors for a course',
    '5. Scrape with GitHub',
    sep='\n',
  )
  # print(data.count_course('CSCI 12000'))
  while True:
    choice = input('Choose: ').strip()
    # if choice not in ['0', '1', '2', '3', '4']:
    #   print('error: invalid selection')
    #   continue
    if choice == '0':
      print('Bye')
      return
    elif choice == '1':
      await scrape(data, mode='local')
    elif choice == '2':
      rank_professors(data)
    elif choice == '5':
      await scrape(data, mode='github')
    else:
      print('error: invalid selection')
  
async def scrape(data: Data, mode: Literal['local', 'github']):
  load_dotenv()
  email = os.getenv('EMAIL')
  password = os.getenv('PASSWORD')

  saved_cookie_value = read_saved_cookie_value(str(data.path))
  # if saved_cookie_value is not None:
  #   result = await scrape_with_cookie(cookie_value=saved_cookie_value, data=data)
  #   if result == 'success':
  #     return
    
  # otp = input('otp: ')
  output = await log_in(email=email, password=password, cookie_value=saved_cookie_value)
  # save_cookie_value(cookie_folder=str(data.path), cookie_value=output.cookie_value)
  if mode == 'local':
    await continue_scrape(
      course_search_page=output.course_search_page,
      cookie_value=output.cookie_value,
      data=data,
      limit=50,
    )
  elif mode == 'github':
    repo = os.getenv('GITHUB_REPOSITORY')
    if repo is None:
      print("expected GITHUB_REPOSITORY environment variable")
      return

    gh_token = os.getenv('GITHUB_TOKEN')
    if gh_token is None:
      print("expected GITHUB_TOKEN environment variable")
      return
    async with AsyncClient() as client:
      course_search_page = json.dumps(output.course_search_page, default=json_default)
      url = f'https://api.github.com/repos/{repo}/actions/workflows/{workflow_file_name}/dispatches'
      print(f"Running workflow at: {url}")
      await client.post(
        url,
        json={
          'ref': 'master',
          'inputs': {
            'cookieValue': output.cookie_value,
            'courseSearchPage': course_search_page,
          },
        },
        headers={
          'Accept': 'application/vnd.github+json',
          'Authorization': f'Bearer {gh_token}',
          'X-GitHub-Api-Version': '2026-03-10',
        },
      )

def rank_professors(data: Data):
  course = input('\nRank professors\nEnter a course, e.g. CSCI 26000\nLeave blank for overall rankings\nCourse: ')
  reports = data.deserialize()
  if course.strip() == '':
    matching = reports
  else:
    matching = [report for report in reports if report.course == course]
  query(matching)

@dataclass
class Fraction:
  num: int
  den: int

  def add(self, other: Fraction):
    self.num += other.num
    self.den += other.den

  def compute(self) -> float:
    if self.den == 0:
      return 0
    return self.num / self.den

@dataclass
class Item:
  name: str
  grade_fraction: Fraction

def query(evals: list[EvalReport]):
  m: dict[str, Fraction] = {}
  for eval_report in evals:
    student_count = 0
    for n in eval_report.page.expected_grades:
      student_count += n
    grade_recipient_count = eval_report.page.expected_grades[0]

    frac = Fraction(
      num=grade_recipient_count,
      den=student_count,
    )
    
    if eval_report.professor in m:
      m[eval_report.professor].add(frac)
    else:
      m[eval_report.professor] = frac
  
  main_list: list[Item] = []
  insuff_list: list[Item] = []
  for name, grade_fraction in m.items():
    item = Item(
      name=name,
      grade_fraction=grade_fraction,
    )
    if grade_fraction.den > 5:
      main_list.append(item)
    else:
      insuff_list.append(item)
  main_list.sort(key=lambda x: x.grade_fraction.compute(), reverse=True)
  s = ""
  for x in main_list:
    s += f"{x.name}: {x.grade_fraction.compute():.0%} ({x.grade_fraction.num}/{x.grade_fraction.den})\n"
  print(s)

def json_default(obj: Any):
  if hasattr(obj, "__dict__"):
      return obj.__dict__
  raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def getenv(key: str) -> str:
  value = os.getenv(key)
  if value is None:
    raise Error(f"expected {key} environment variable")
  return value

def init_log():
  dir_name = os.path.dirname(__file__)
  logs_path = Path(os.path.join(dir_name, logs_folder_name))
  logs_path.mkdir(parents=True, exist_ok=True)
  log_file_path = logs_path.joinpath(log_file_name)
  formatter = Formatter('%(asctime)s %(levelname)s %(message)s')
  file_handler = FileHandler(filename=log_file_path, encoding='utf-8', mode='w')
  file_handler.setFormatter(formatter)
  console_handler = StreamHandler()
  console_handler.setFormatter(formatter)
  log.setLevel(logging.DEBUG)
  log.addHandler(file_handler)
  log.addHandler(console_handler)

@dataclass
class Error(MyError):
  msg: str

  @override
  def message(self):
    return "error:" + self.msg

asyncio.run(main())