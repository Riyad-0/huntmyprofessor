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
import supabase

from scrape import Data, MyError, continue_scrape, fetch_data, log, log_in, read_saved_cookie_value

data_folder_name = 'data'
logs_folder_name = 'logs'
log_file_name = 'hunt.log'
debug_workflow_file_name = 'debug.yml'
release_workflow_file_name = 'release.yml'

async def main():
  try:
    await inner()
  except Exception as e:
    if isinstance(e, MyError):
      log.error(e.message())
    else:
      raise e

async def inner():
  load_dotenv()
  init_log()
  dir_name = os.path.dirname(__file__)
  data_path = os.path.join(dir_name, data_folder_name)
  data = fetch_data(data_path)
  print(
    'HuntMyProfessor',
    '0. Quit',
    '1. Scrape',
    '2. Scrape with GitHub (debug)',
    '3. Scrape with GitHub (release)',
    '4. Sync with remote',
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
      await scrape(data, mode='github-debug')
    elif choice == '3':
      await scrape(data, mode='github-release')
    elif choice == '4':
      await sync(data)
    else:
      print('error: invalid selection')
  
async def scrape(data: Data, mode: Literal['local', 'github-debug', 'github-release']):
  limit = None
  if mode == 'local':
    wip_limit = input('Limit the number of reports to scrape, or leave blank for no limit\nLimit: ')
    if wip_limit.strip() != '':
      limit = int(wip_limit)
    
  email = os.getenv('EMAIL')
  password = os.getenv('PASSWORD')
  otp_key = os.getenv('OTP_KEY')

  saved_cookie_value = read_saved_cookie_value(str(data.path))
  # if saved_cookie_value is not None:
  #   result = await scrape_with_cookie(cookie_value=saved_cookie_value, data=data)
  #   if result == 'success':
  #     return
    
  # otp = input('otp: ')
  output = await log_in(email=email, password=password, otp_key=otp_key, cookie_value=saved_cookie_value)
  # save_cookie_value(cookie_folder=str(data.path), cookie_value=output.cookie_value)
  if mode == 'local':
    await continue_scrape(
      course_search_page=output.course_search_page,
      cookie_value=output.cookie_value,
      data=data,
      limit=limit,
    )
  elif mode == 'github-debug' or mode == 'github-release':
    match mode:
      case 'github-debug': workflow_file_name = debug_workflow_file_name
      case 'github-release': workflow_file_name = release_workflow_file_name
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
      print(f'Running workflow: {workflow_file_name}')
      res = await client.post(
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
      if res.status_code == 200:
        body = res.json()
        run_id = body['workflow_run_id']
        print(f"Running workflow at: https://github.com/{repo}/actions/runs/{run_id}")
      else:
        print(f"error: workflow {workflow_file_name} failed")

async def sync(data: Data):
  supabase_url = os.getenv("SUPABASE_URL")
  if supabase_url is None:
    print("expected SUPABASE_URL environment variable")
    return

  supabase_key = os.getenv("SUPABASE_KEY")
  if supabase_key is None:
    print("expected SUPABASE_KEY environment variable")
    return
  db = await supabase.acreate_client(
    supabase_url=supabase_url,
    supabase_key=supabase_key,
  )
  courses = [{'name': course} for course in data.schema_db.courses]
  db_courses = (await db.table('course').upsert(courses, on_conflict='name', ignore_duplicates=True).execute()).data
  sections = [{'name': section} for section in data.schema_db.sections]
  db_sections = (await db.table('section').upsert(sections, on_conflict='name', ignore_duplicates=True).execute()).data
  semesters: list[dict[str, int]] = []
  for semester in data.schema_db.semesters:
    year, season = semester_to_year_season(semester)
    semesters.append({
      'year': year,
      'season': season,
    })
  db_semesters = (await db.table('semester').upsert(semesters, on_conflict='year,season', ignore_duplicates=True).execute()).data
  professors = [{'name': professor} for professor in data.schema_db.professors]
  db_professors = (await db.table('professor').upsert(professors, on_conflict='name', ignore_duplicates=True).execute()).data
  evals = data.deserialize()
  wip_db_evals = []
  for eval in evals:
    year, season = semester_to_year_season(eval.semester)
    for course in db_courses:
      if course['name'] == eval.course:
        course_id = course['id']
        break
    for section in db_sections:
      if section['name'] == eval.section:
        section_id = section['id']
        break
    for semester in db_semesters:
      if semester['year'] == year and semester['season'] == season:
        semester_id = semester['id']
        break
    for professor in db_professors:
      if professor['name'] == eval.professor:
        professor_id = professor['id']
        break
    q = eval.page.score_sections[0].questions[-1]
    response_count = 0
    weighted_total = 0
    for i, count in enumerate(q.scores):
      response_count += count
      weighted_total += (i+1) * count
    rating = weighted_total / response_count
    a_count = eval.page.expected_grades[0]
    wip_db_evals.append({
      'course_id': course_id,
      'section_id': section_id,
      'semester_id': semester_id,
      'professor_id': professor_id,
      'response_count': response_count,
      'rating': rating,
      'a_count': a_count,
    })
  await db.table('eval').upsert(wip_db_evals, ignore_duplicates=True).execute()
  log.info(f'Synced {len(wip_db_evals)} evals')

def semester_to_year_season(semester: str) -> tuple[int, int]:
  split = semester.split()
  year = int(split[1].strip())
  season = split[0].strip().lower()
  season = ['winter', 'spring', 'summer', 'fall'].index(season)
  return year, season

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