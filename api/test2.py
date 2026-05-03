import asyncio
import os
import random
import sys
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from httpx import AsyncClient, Cookies, Headers, Response

from scrape.data import fetch_data
from scrape._eval_report import EvalReport
from scrape.log import clear_log

def getenv(key: str) -> str:
  value = os.getenv(key)
  if value is None:
    raise Error(f"expected {key} environment variable")
  return value

def parse_username(email: str) -> str:
  split = email.split('@', 1)
  if len(split) < 2:
    raise Error('expected EMAIL environment variable to be @-separated')
  return split[0]

# from scrape.log import log as logger

request_names = ['open_course_search', 'saml', 'auth_cred', 'authn_v1', 'authn_index']

hunter_cookie_name = "ORA_WWV_APP_116"
sso_cookie_names1 = ['OAM_JSESSIONID', 'OAM_REQ_0', 'OAM_REQ_1', 'OAM_REQ_COUNT', 'BIGipServera/wVmqC4X189EXHfdIK97w']
sso_cookie_names2 = ['OAM_JSESSIONID', 'OAM_REQ_COUNT', 'BIGipServera/wVmqC4X189EXHfdIK97w', 'OAACtxCookie', 'OAM_REQ_0', 'OAM_REQ_1']
sso_cookie_names3 = ['OAM_JSESSIONID', 'OAM_REQ_COUNT', 'BIGipServera/wVmqC4X189EXHfdIK97w', 'OAACtxCookie', 'OAM_REQ_0', 'OAM_REQ_1', 'BIGipServer/1cH5tvcc6Xb1GCKLdbbKA', ]

def clean_headers(request: RawRequest) -> dict[str, str]:
  headers = request.headers.copy()
  headers.pop('Host', '')
  headers.pop('Content-Length', '')
  if 'Cookie' in headers:
    headers['Cookie'] = ''
  return headers

def strip_query_params(url: str) -> str:
  return url.split('?', maxsplit=1)[0]

def add_cookies(headers: dict[str, str], cookies: list[str]):
  s = ''
  for i, cookie in enumerate(cookies):
    if i > 0:
      s += '; '
    s += cookie
  headers['Cookie'] = s

def parse_raw_request(
  file_name: str,
) -> RawRequest:
  headers: dict[str, str] = {}
  host: str | None = None
  cookie_names: list[str] = []
  with open(file_name) as f:
    lines = [line.rstrip() for line in f.readlines()]
    method, path = parse_raw_request_first_line(lines)

    for i, line in enumerate(lines):
      if i == 0:
        continue
      split = line.split(": ", maxsplit=1)
      if len(split) < 2:
        raise ParseRequestError(f"expected colon-separated line on line {i+1}")
      key = split[0]
      value = split[1]
      if key == 'Cookie':
        cookies = value.split('; ')
        for cookie in cookies:
          name = cookie.split('=', maxsplit=1)[0]
          cookie_names.append(name)
      if key == 'Host':
        host = value
      headers[key] = value
  if host is None:
    raise ParseRequestError(f"expected 'Host'")
  url = 'https://' + host + path
  return RawRequest(
    method=method,
    url=url,
    headers=headers,
    cookie_names=cookie_names,
  )
      
@dataclass
class RawRequest:
  method: Method
  url: str
  headers: dict[str, str]
  cookie_names: list[str]

type Method = Literal['GET', 'POST']

def parse_raw_request_first_line(lines: list[str]) -> tuple[Method, str]:
  if len(lines) < 1:
    raise ParseRequestError("expected 'GET' or 'POST'")
  line = lines[0]
  split = line.split()
  if len(split) > 0:
    if split[0] == "GET":
      method = "GET"
    elif split[0] == "POST":
      method = "POST"
    else:
      raise ParseRequestError("expected 'GET' or 'POST'")
  else:
    raise ParseRequestError("expected 'GET' or 'POST'")
  if len(split) > 1:
    path = split[1]
  else:
    raise ParseRequestError("expected path")
  return method, path
  

async def send_get(
  client: AsyncClient,
  stage: str,
  url: str,
  headers: dict[str, str]
) -> Response:
  res = await client.get(
    url=url,
    headers=headers,
  )

  # content_type = res.headers.get('Content-Type', '')
  # if 'text/html' in content_type:
  #   ext = 'html'
  # elif 'application/json' in content_type:
  #   ext = 'json'
  # else:
  #   ext = 'txt'
  
  # file_name = url.lstrip('https://').replace('/', '@').replace(':', '@').replace('?', '@') + '.' + ext
  # with open(file_name, 'w') as f:
  #   f.write(res.text)
  
  # print(f"Completed: GET {url}\n  Cookies: {client.cookies}\n  response written to: {file_name}")
  await log_response(client, stage, 'GET', url, res)

  return res

async def send_post(
  client: AsyncClient,
  stage: str,
  url: str,
  headers: dict[str, str],
  data: dict[str, str],
) -> Response:
  res = await client.post(
    url=url,
    headers=headers,
    data=data,
  )
  await log_response(client, stage, 'POST', url, res)
  return res

async def log_response(client: AsyncClient, stage: str, method: Method, url: str, res: Response):
  content_type = res.headers.get('Content-Type', '')
  if 'text/html' in content_type:
    ext = 'html'
  elif 'application/json' in content_type:
    ext = 'json'
  else:
    ext = 'txt'
  
  # wip_file_name_stem = url.removeprefix('https://')
  # if len(wip_file_name_stem) > 100:
  #   wip_file_name_stem = strip_query_params(wip_file_name_stem)
  # wip_file_name_stem = wip_file_name_stem[:100]
  
  # file_name_stem = wip_file_name_stem.replace('/', '@').replace(':', '@').replace('?', '@')
  file_name_stem = stage
  res_file_name = file_name_stem + '.res.' + ext
  with open(res_file_name, 'w') as f:
    f.write(res.text)
  
  # headers = ''
  # for key, value in res.headers.items():
  #   headers += f'{key}: {value}\n'    
  cookies = ''
  for i, (name, value) in enumerate(client.cookies.items()):
    if i > 0:
      cookies += '\n'
    if len(value) > 30:
      value = value[:13] + ' ... ' + value[-18:]
    cookies += f'{name}={value}'
  request = (await res.request.aread()).decode(encoding='utf-8')

  details = 'Response headers:\n' + format_headers(res.headers) \
    + '\n\nResponse cookies:\n' + cookies \
    + f'\n\nRequest: {res.request.method} {url}' \
    + f'\n\nRequest headers: {format_headers(res.request.headers)}' \
    + '\n\nRequest content:\n' + request
  details_file_name = file_name_stem + ".details.txt"
  with open(details_file_name, 'w') as f:
    f.write(details)
  
  formatted_url = url
  if len(formatted_url) > 100:
    formatted_url = formatted_url[:85] + ' ... ' + formatted_url[90:]

  print(
    f"Completed: {res.request.method} {formatted_url}",
    f"  response written to: {res_file_name}",
    f"  details written to: {details_file_name}",
    sep='\n',
  )

def format_headers(headers: Headers) -> str:
  s = ''
  for i, (key, value) in enumerate(headers.items()):
    if i > 0:
      s += '\n'
    s += f'{key}: {value}'
  return s

@dataclass
class ParseRequestError(Exception):
  message: str

  def print(self):
    print("error:", self.message, "when parsing request")

@dataclass
class Error(Exception):
  message: str

  def print(self):
    print("error:", self.message)

def values_by_name(soup: BeautifulSoup, names: list[str]) -> dict[str, str]:
  data: dict[str, str] = {}
  for name in names:
    data[name] = value_by_name(soup, name)
  return data

def value_by_name(soup: BeautifulSoup, name: str) -> str:
  el = soup.find(attrs={'name': name})
  if el is None:
    raise Error(f"expected element with name '{name}'")
  value = el.get('value')
  if not isinstance(value, str):
    raise Error(f"expected element with name '{name}' to have 'value' attribute")
  return value

async def main():
  load_dotenv()
  email = getenv('EMAIL')
  password = getenv('PASSWORD')
  username = parse_username(email)
  async with AsyncClient(follow_redirects=True) as client:
    stage = '1_open_course_search'
    r = parse_raw_request(stage + '.txt')
    headers = clean_headers(r)
    res = await send_get(client, stage, url=r.url, headers=headers)

    soup = BeautifulSoup(res.text, 'html.parser')
    data: dict[str, str] = {
      'SAMLRequest': value_by_name(soup, 'SAMLRequest'),
      'RelayState': value_by_name(soup, 'RelayState'),
    }

    # cookie = parse_cookie(client.cookies)
    stage = '2_saml'
    r = parse_raw_request(stage + '.txt')
    headers = clean_headers(r)
    res = await send_post(client, stage, url=r.url, headers=headers, data=data)

    data = {
      'usernameDisplay': email,
      'username': username,
      'password': password,
      'submit': '',
    }

    stage = '3_auth_cred'
    r = parse_raw_request(stage + '.txt')
    headers = clean_headers(r)
    cookies = parse_cookies(client.cookies, names=r.cookie_names)
    # cookies = [parse_cookie(client.cookies, cookie_name, default=None) for cookie_name in sso_cookie_names]
    add_cookies(headers, list(cookies.values()))
    res = await send_post(client, stage, url=r.url, headers=headers, data=data)

    soup = BeautifulSoup(res.text, 'html.parser')
    data = values_by_name(soup, ['reqTok', 'request_id', 'CREDENTIAL_CONTEXT_DATA'])

    stage = '4_authn_v1'
    r = parse_raw_request(stage + '.txt')
    headers = clean_headers(r)
    cookies = parse_cookies(client.cookies, names=r.cookie_names, default=cookies)
    add_cookies(headers, list(cookies.values()))
    res = await send_post(client, stage, url=r.url, headers=headers, data=data)

    parsed_headers = parse_headers(res.headers, ['Location'])
    tstok = parse_tstok(parsed_headers)
  
    stage = '5_authnui'
    r = parse_raw_request(stage + '.txt')
    url = parsed_headers['Location'].replace(':443', '', count=1)
    headers = clean_headers(r)
    cookies = parse_cookies(client.cookies, names=r.cookie_names, default=cookies)
    add_cookies(headers, list(cookies.values()))
    await send_get(client, stage, url=url, headers=headers)

    stage = '6_fp'
    r = parse_raw_request(stage + '.txt')
    headers = clean_headers(r)
    cookies = parse_cookies(client.cookies, names=r.cookie_names, default=cookies)
    add_cookies(headers, list(cookies.values()))
    await send_get(client, stage, url=r.url, headers=headers)

    # stage = '7_process'
    # r = parse_raw_request(stage + '.txt')
    # headers = clean_headers(r)
    # cookies = parse_cookies(client.cookies, names=r.cookie_names, default=cookies)
    # add_cookies(headers, list(cookies.values()))
    # random_id = str(random.randint(100, 999))
    # data = {
    #   'reqTok': data['reqTok'],
    #   'jclient': 'vfc',
    #   'jfp': 'acn=Mozilla&l=en-US&ce=true&an=Netscape&av=5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36&p=Win32&ua=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36&o=true&je=false&w=1280&h=720&cd=32&aw=1280&ah=672&tzo=-4&mt=application/pdf,text/pdf&pl=PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF&prod=Gecko&prods=20030107&pd=32',
    #   'randomId': random_id,
    #   'tstok': tstok,
    # }
    # res = await send_post(client, stage, url=r.url, headers=headers, data=data)


  # print(r)

def parse_tstok(parsed_headers: dict[str, str]) -> str:
  split = parsed_headers['Location'].split('?tstok=', maxsplit=1)
  if len(split) < 2:
    raise Error("expected 'tstok' query parameter in 'Location' response header")
  rest = split[1]
  return rest.split('&', maxsplit=1)[0]

# SAMLData = TypedDict('SAMLData', {
#   'SAMLRequest': str,
#   'RelayState': str,
# }, closed=True)

def parse_cookie(cookies: Cookies, name: str, default: str | None) -> str:
  value = cookies.get(name)
  if value is None:
    if default is None:
      raise Error(f"expected cookie '{name}' to be set")
    else:
      return default
  return name + '=' + value

def parse_cookies_old(cookies: Cookies, names: list[str] | None = None, default: dict[str, str] = {}) -> dict[str, str]:
  out: dict[str, str] = {}
  for name, cookie in default:
    if names is None or name in names:
      out[name] = cookie
  for name, value in cookies.items():
    if names is None or name in names:
      out[name] = name + '=' + value
  return out

def parse_cookies(cookies: Cookies, names: list[str], default: dict[str, str] = {}) -> dict[str, str]:
  out: dict[str, str] = {}
  for name in names:
    cookie = parse_cookie(cookies, name, default.get(name))
    out[name] = cookie
  return out

def parse_headers(headers: Headers, names: list[str]) -> dict[str, str]:
  out: dict[str, str] = {}
  for name in names:
    value = headers.get(name)
    if value is None:
      raise Error(f"expected header '{name}'")
    out[name] = value
  return out

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from scrape import open_course_search_page
from scrape.select_dept import select_dept
from scrape.select_subject import select_subject
from scrape.scrape_error import ScrapeError
from scrape.course_search import course_search
from scrape.open_all_eval_reports import open_all_eval_reports
from scrape.log import log
from httpx_limiter import AsyncRateLimitedTransport, Rate # type: ignore
from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter # type: ignore


async def main2():
  load_dotenv()
  email = getenv('EMAIL')
  password = getenv('PASSWORD')

  if len(sys.argv) < 2:
    raise Error('expected otp as command-line argument')
  otp = sys.argv[1]

  options = Options()

  # Disable ask-for-location prompt
  prefs = {'profile.default_content_setting_values.geolocation': 2}
  options.add_experimental_option('prefs', prefs) # type: ignore

  driver = webdriver.Chrome(options=options)
  wait = WebDriverWait(driver, 10)

  driver.get('https://orapp.hunter.cuny.edu/ords/f?p=116:6')
  
  email_text_box = wait.until(EC.presence_of_element_located((By.ID, 'CUNYLoginUsernameDisplay')))
  password_text_box = wait.until(EC.presence_of_element_located((By.ID, 'CUNYLoginPassword')))
  submit_button = wait.until(EC.presence_of_element_located((By.ID, 'submit')))
  
  email_text_box.send_keys(email)
  password_text_box.send_keys(password)
  submit_button.click()

  otp_text_box = wait.until(EC.presence_of_element_located((By.ID, 'otpValue|input')))
  submit_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'oj-button-button')))

  otp_text_box.send_keys(otp)
  submit_button.click()

  wait.until(EC.presence_of_element_located((By.ID, 'pPageItemsProtected')))

  cookie_details = driver.get_cookie(hunter_cookie_name) # type: ignore
  cookie_value = cookie_details['value'] # type: ignore
  cookie = hunter_cookie_name + '=' + cookie_value # type: ignore

  res_text = driver.page_source
  driver.close()
  with open("big-test.html", 'w') as f:
    f.write(res_text)
  
  output = open_course_search_page.parse_response2(res_text, cookie) # type: ignore
  await continue_scrape(output, cookie_value) # type: ignore

  # async with AsyncClient(cookies={hunter_cookie_name: cookie_value}, follow_redirects=True) as client:
  #   output = await select_dept.select_dept(client, output)
  #   print(output.subject_options)

async def continue_scrape(open_course_search_page_output: open_course_search_page.Output, cookie_value: str):
  cookies={hunter_cookie_name: cookie_value}
  clear_log()
  data = fetch_data()
  limiter = AiolimiterAsyncLimiter.create(Rate.create(magnitude=1, duration=0.1))
  async with AsyncClient(
    cookies=cookies,
    follow_redirects=True,
    transport=AsyncRateLimitedTransport.create(limiter=limiter),
  ) as client:
    try:
      output = await select_dept(client, open_course_search_page_output)
      output = await select_subject(client, open_course_search_page_output)
      course_number_options = ["12000"]
      did_fetch_max_rows = False
      for course_num in course_number_options:
        search_output = await course_search(
          client,
          open_course_search_page_output,
          data,
          department="CSCI-HTR",
          subject="CSCI",
          course_num=course_num,
          did_fetch_max_rows=did_fetch_max_rows,
        )
        # cookie = search_output.cookie
        # match search_output.parse_result:
        #   case Parsed(course_sections):
        #     evals_iter = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
        #   case NeedsPaginate(paginate_codes):
        #     did_fetch_max_rows = True
        #     output = fetch_max_rows(
        #       s,
        #       cookie=cookie,
        #       p_instance=search_output.p_instance,
        #       p_page_submission_id=search_output.p_page_submission_id,
        #       paginate_codes=paginate_codes
        #     )
        #     if output.cookie is not None:
        #       cookie = output.cookie
        #     course_sections = output.course_sections
        #     evals_iter = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
        eval_reports_output = await open_all_eval_reports(
          client,
          data=data,
          course_search_output=search_output,
          did_fetch_max_rows=did_fetch_max_rows,
          limit=20,
        )
        did_fetch_max_rows = eval_reports_output.did_fetch_max_rows
        eval_reports: list[EvalReport] = []
        # l = 0
        for aoutput in eval_reports_output.outputs:
          # if output.cookie is not None:
            # cookie = output.cookie
          output = await aoutput
          eval_report = output.eval_report
          eval_reports.append(eval_report)
          data.add(eval_report)
          data.write()
          data.write_json()
          log.info(f"Collected eval: {eval_report.formatted()}")
    except Exception as e:
      if isinstance(e, ScrapeError):
        print(e.message())
      else:
        raise e
  # input()

asyncio.run(main2())
