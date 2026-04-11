from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import requests
from scrape.log import clear_log
from scrape.scrape_error import ScrapeError
from scrape.open_login_page import open_login_page
from scrape.sign_in import sign_in
from scrape.professor_search import professor_search
from scrape.open_course_search_page import open_course_search_page
from scrape.select_dept import select_dept
from scrape.select_subject import select_subject
from scrape.course_search import course_search

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
    output = course_search(s, open_course_search_page_output)
    print(output.eval_reports)
    return CourseSearchResult(result="success")
  except Exception as e:
    if isinstance(e, ScrapeError):
      print(e.message)
      return CourseSearchError(result="error", message=e.message())
    else:
      raise e