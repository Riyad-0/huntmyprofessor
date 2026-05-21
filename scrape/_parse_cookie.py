from httpx import Cookies

from scrape._cookie_name import cookie_name

def parse_cookie(cookies: Cookies) -> str | None:
  value = cookies.get(cookie_name)
  if value == None:
    return None
  return cookie_name + '=' + value
