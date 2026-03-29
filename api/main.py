from fastapi import FastAPI
from pydantic import BaseModel
from scrape.open_login_page import open_login_page
from scrape.sign_in import sign_in
from scrape.professor_search import professor_search
import requests

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

@app.post("/api/login")
def login(login: Login):
  print(login.username, login.password)
  s = requests.Session()
  output = open_login_page(s)
  output = sign_in(s, output, login.username, login.password)
  output = professor_search(s, output, search_text="washburn, alexander")
  print(output.courses)
  

  return "Woah"