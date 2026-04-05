from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import requests
from scrape.open_login_page import open_login_page
from scrape.sign_in import sign_in
from scrape.professor_search import professor_search

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