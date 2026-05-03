from pathlib import Path
import time

def get_cookie_file_path(cookie_folder: str) -> Path:
  cookie_folder_path = Path(cookie_folder)
  cookie_folder_path.mkdir(parents=True, exist_ok=True)
  return cookie_folder_path.joinpath('cookie.txt')

def read_saved_cookie_value(cookie_folder: str) -> str | None:
  cookie_file_path = get_cookie_file_path(cookie_folder)
  try:
    with open(cookie_file_path) as f:
      lines = [line.rstrip() for line in f.readlines()]
  except FileNotFoundError:
    return None
  if len(lines) < 2:
    return None
  cookie_value = lines[0]
  try:
    cookie_time = float(lines[1])
  except ValueError:
    return None
  if time.time() - cookie_time < 30 * 60:
    return cookie_value
  else:
    return None
  
def save_cookie_value(cookie_folder: str, cookie_value: str):
  cookie_file_path = get_cookie_file_path(cookie_folder)
  with open(cookie_file_path, 'w') as f:
    f.write(cookie_value + f'\n{time.time()}')
    