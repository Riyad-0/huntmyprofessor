import asyncio
import json
from logging import FileHandler, Formatter, StreamHandler
import logging
import os
from pathlib import Path

from scrape import CourseSearchPage, SelectElementOption, continue_scrape, fetch_data, log

data_folder_name = 'data'
logs_folder_name = 'logs'
log_file_name = 'hunt.log'

async def main():
  cookie_value = os.getenv("COOKIE_VALUE")
  if cookie_value is None:
    print("expected COOKIE_VALUE environment variable")
    return
  course_search_page = os.getenv("COURSE_SEARCH_PAGE")
  if course_search_page is None:
    print("expected COURSE_SEARCH_PAGE environment variable")
    return
  course_search_page = json.loads(course_search_page)
  course_search_page = CourseSearchPage(
    cookie=course_search_page['cookie'],
    p_instance=course_search_page['p_instance'],
    p_page_items_protected=course_search_page['p_page_items_protected'],
    p_page_submission_id=course_search_page['p_page_submission_id'],
    dept_ajax_identifier=course_search_page['dept_ajax_identifier'],
    subject_ajax_identifier=course_search_page['subject_ajax_identifier'],
    dept_options=[
      SelectElementOption(
        name=option['name'],
        value=option['value'],
      )
      for option in course_search_page['dept_options']
    ],
  )

  init_log()
  dir_name = os.path.dirname(__file__)
  data_path = os.path.join(dir_name, data_folder_name)
  data = fetch_data(data_path)

  await continue_scrape(
    course_search_page=course_search_page,
    cookie_value=cookie_value,
    data=data,
    # limit=50,
  )

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
  log.setLevel(logging.INFO)
  log.addHandler(file_handler)
  log.addHandler(console_handler)

if __name__ == '__main__':
  asyncio.run(main())