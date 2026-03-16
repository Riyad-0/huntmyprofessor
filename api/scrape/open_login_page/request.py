import json
import os;

headers_file_path = os.path.join(os.path.dirname(__file__), "requestHeaders.json")

def parse_headers():
  with open(headers_file_path, "r") as file:
    headers = json.load(file)
    return headers

url = "https://www.hunter.cuny.edu/myprof"
headers = parse_headers()