import json
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import requests
from scrape.open_eval_reports import open_eval_reports
from scrape.log import clear_log
from scrape.scrape_error import ScrapeError
from scrape.open_login_page import open_login_page
from scrape.sign_in import sign_in
from scrape.professor_search import professor_search
from scrape.open_course_search_page import open_course_search_page
from scrape.select_dept import select_dept
from scrape.select_subject import select_subject
from scrape.course_search import course_search
from scrape.open_next_page import open_next_page

app = FastAPI()

@app.get("/")
def read_root():
  print("")


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#   return {"item_id": item_id, "q": q}

class Login(BaseModel):
  username: str
  password: str

class LoginResult(BaseModel):
  result: str
  courses: list[Any]

class CourseSearchResult(BaseModel):
  result: str

class CourseSearchError(CourseSearchResult):
  message: str

@app.post("/api/login")
def login(login: Login):
  s = requests.Session()
  output = open_login_page(s)
  output = sign_in(s, output, login.username, login.password)
  output = professor_search(s, output, search_text="washburn, alexander")
  print(output.courses)
  
  return LoginResult(
    result="success",
    courses=output.courses,
  )

@app.post("/api/courses")
def courses(login: Login):
  print("HELLO!")
  clear_log()
  s = requests.Session()
  try:
    output = open_login_page(s)
    output = sign_in(s, output, login.username, login.password)
    open_course_search_page_output = open_course_search_page(s, output)
    output = select_dept(s, open_course_search_page_output)
    output = select_subject(s, open_course_search_page_output)
    course_number_options = output.course_number_options
    for course_num in course_number_options:
      search_output = course_search(
        s,
        open_course_search_page_output,
        department="CSCI-HTR",
        subject="CSCI",
        course_num=course_num,
      )
      course_sections = search_output.course_sections
      cookie = search_output.cookie
      output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
      cookie = output.cookie
      eval_reports = output.eval_reports
      paginate_codes = search_output.paginate_codes
      if paginate_codes is not None:
        output = open_next_page(
          s,
          cookie=cookie,
          p_instance=search_output.p_instance,
          p_page_submission_id=search_output.p_page_submission_id,
          paginate_codes=paginate_codes
        )
        if output.cookie is not None:
          cookie = output.cookie
        course_sections = output.course_sections
        output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
        eval_reports = output.eval_reports
        for eval_report in output.eval_reports:
          eval_reports.append(eval_report)
        
      with open("out.json", "w") as f:
        json.dump(eval_reports, f, indent=2, default=json_default)
      return CourseSearchResult(result="success")
  except Exception as e:
    if isinstance(e, ScrapeError):
      print(e.message())
      return CourseSearchError(result="error", message=e.message())
    else:
      raise e

@app.post("/api/coursesold")
def coursesold(login: Login):
  print("HELLO!")
  clear_log()
  s = requests.Session()
  try:
    output = open_login_page(s)
    output = sign_in(s, output, login.username, login.password)
    open_course_search_page_output = open_course_search_page(s, output)
    output = select_dept(s, open_course_search_page_output)
    output = select_subject(s, open_course_search_page_output)
    course_number_options = output.course_number_options
    search_output = course_search(
      s,
      open_course_search_page_output,
      department="ENGL-HTR",
      subject="ENGL",
      course_num="12000",
      # department="CSCI-HTR",
      # subject="CSCI",
      # course_num="33500",
    )
    course_sections = search_output.course_sections
    cookie = search_output.cookie
    output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
    cookie = output.cookie
    eval_reports = output.eval_reports
    # eval_reports: list[EvalReport] = []
    # for course_section in course_sections:
    #   if course_section.url is not None:
    #     output = open_eval_report(s, cookie=cookie, url=course_section.url)
    #     cookie = output.cookie
    #     eval_reports.append(EvalReport(
    #       course=course_section.course,
    #       semester=course_section.semester,
    #       professor=course_section.professor,
    #       page=EvalReportPage(
    #         url=course_section.url,
    #         score_sections=output.score_sections,
    #         expected_grades=output.expected_grades
    #       ),
    #     ))
    #   else:
    #     eval_reports.append(EvalReport(
    #       course=course_section.course,
    #       semester=course_section.semester,
    #       professor=course_section.professor,
    #       page=None,
    #     ))
    paginate_codes = search_output.paginate_codes
    if paginate_codes is not None:
      output = open_next_page(
        s,
        cookie=cookie,
        p_instance=search_output.p_instance,
        p_page_submission_id=search_output.p_page_submission_id,
        paginate_codes=paginate_codes
      )
      if output.cookie is not None:
        cookie = output.cookie
      course_sections = output.course_sections
      # TODO
      print("LENGO:", len(course_sections))
      return CourseSearchResult(result="success")
      output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
      # TODO
      eval_reports = output.eval_reports
      # for eval_report in output.eval_reports:
      #   eval_reports.append(eval_report)
      
    with open("out.json", "w") as f:
      json.dump(eval_reports, f, indent=2, default=json_default)
    # print(eval_reports)
    return CourseSearchResult(result="success")
  except Exception as e:
    if isinstance(e, ScrapeError):
      print(e.message())
      return CourseSearchError(result="error", message=e.message())
    else:
      raise e
    
def json_default(obj: Any):
  if hasattr(obj, "__dict__"):
      return obj.__dict__
  raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")