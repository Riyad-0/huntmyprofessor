from dataclasses import dataclass
from typing import Literal

import requests
from scrape import open_login_page
from scrape import sign_in



type State = Literal[
  "start",
  "opened login page",
  "signed in"
]

type State2 = Start | str

@dataclass
class State3:
  pass

@dataclass
class Start3(State3):
  pass

@dataclass
class OpenedLoginPage3(State3):
  output: open_login_page.Output

@dataclass
class Start:
  tag: Literal["start"] = "start"

@dataclass
class OpenedLoginPage:
  tag: Literal["oep"] = "oep"

type A = int | str

def main():
  print(
    "1. Sign in",
    "2. Professor search",
    "3. Course search",
    sep="\n"
  )
  choice = input("Choice: ")

  # state: State3 = Start3()
  # s = requests.Session()

  
  # match choice:
  #   case "1":
  #     username = input("Username: ")
  #     password = input("Password: ")

# def verify_signed_in(state: State3) -> State3:
#   if isinstance(state, Start3):
#     output = open_login_page.open_login_page()
    
main()