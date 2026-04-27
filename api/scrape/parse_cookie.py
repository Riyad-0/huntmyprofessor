from httpx import Cookies

from .cookie_name import cookie_name

def parse_cookie(cookies: Cookies) -> str | None:
  value = cookies.get(cookie_name)
  if value == None:
    return None
  return cookie_name + '=' + value
#   foundCookie = cookies.find(cookie => cookie.startsWith(cookieName + "="));
#   if (foundCookie === undefined) {
#     return undefined;
#   }
#   const end = foundCookie.indexOf(";");
#   if (end === -1) {
#     return foundCookie;
#   } else {
#     return foundCookie.slice(0, end);
#   }
# }
