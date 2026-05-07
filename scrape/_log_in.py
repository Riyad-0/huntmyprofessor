from dataclasses import dataclass
from typing import override

import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrape import _parse_course_search_page
from scrape._cookie_name import cookie_name
from scrape._error import MyError
from scrape._parse_course_search_page import parse_course_search_page

@dataclass
class Output:
  course_search_page: _parse_course_search_page.CourseSearchPage
  cookie_value: str

@dataclass
class CookieError(MyError):
  @override
  def message(self):
    return 'expected login cookie'

async def log_in(email: str | None, password: str | None, otp_key: str | None, cookie_value: str | None) -> Output:
  hide_input = True
  options = Options()

  # Disable ask-for-location prompt
  prefs = {'profile.default_content_setting_values.geolocation': 2}
  options.add_experimental_option('prefs', prefs) # type: ignore

  driver = webdriver.Chrome(options=options)
  # if cookie_value is not None:
  #   driver.get('https://orapp.hunter.cuny.edu/ords/f?p=116:10')
  #   driver.delete_cookie(cookie_name) # pyright: ignore[reportUnknownMemberType]
  #   driver.add_cookie({ # pyright: ignore[reportUnknownMemberType]
  #     'name': cookie_name,
  #     'value': cookie_value,
  #     'domain': 'orapp.hunter.cuny.edu',
  #     'path': '/ords/',
  #     'secure': True,
  #     'httpOnly': True,
  #     'priority': 'Medium',
  #   })
  #   driver.get('https://orapp.hunter.cuny.edu/ords/f?p=116:10')
  #   input()
  wait = WebDriverWait(driver, 90)

  driver.get('https://orapp.hunter.cuny.edu/ords/f?p=116:6')
  
  login_page_condition = EC.presence_of_element_located((By.ID, 'CUNYLoginUsernameDisplay'))
  course_search_page_condition = EC.presence_of_element_located((By.ID, 'pPageItemsProtected'))
  
  found = wait.until(EC.any_of(login_page_condition, course_search_page_condition))

  if found.get_attribute('id') == 'pPageItemsProtected': # pyright: ignore[reportUnknownMemberType]
    return await finish_log_in(driver)
  
  email_text_box = wait.until(EC.presence_of_element_located((By.ID, 'CUNYLoginUsernameDisplay')))
  password_text_box = wait.until(EC.presence_of_element_located((By.ID, 'CUNYLoginPassword')))
  submit_button = wait.until(EC.presence_of_element_located((By.ID, 'submit')))

  if hide_input:
    script = \
      "arguments[0].style.backgroundColor = 'black';" + \
      "arguments[0].style.color = 'black';" + \
      "arguments[1].style.backgroundColor = 'black';" + \
      "arguments[1].style.color = 'black';"

    driver.execute_script(script, email_text_box, password_text_box) # pyright: ignore[reportUnknownMemberType]
  
  if email is not None:
    email_text_box.send_keys(email)
  if password is not None:
    password_text_box.send_keys(password)
  if email is not None and password is not None:
    submit_button.click()

  otp_text_box = wait.until(EC.presence_of_element_located((By.ID, 'otpValue|input')))

  if hide_input:
    script = \
        "arguments[0].type = 'password';"
    driver.execute_script(script, otp_text_box) # pyright: ignore[reportUnknownMemberType]
  
  if otp_key is not None:
    submit_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'oj-button-button')))
    otp = pyotp.TOTP(otp_key).now()
    otp_text_box.send_keys(otp)
    submit_button.click()

  wait.until(EC.presence_of_element_located((By.ID, 'pPageItemsProtected')))

  return await finish_log_in(driver)

  # cookie_details = driver.get_cookie(cookie_name) # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
  # if cookie_details is None:
  #   raise CookieError()
  # cookie_value = cookie_details['value'] # pyright: ignore[reportUnknownVariableType]
  # cookie = cookie_name + '=' + cookie_value # type: ignore

  # res_text = driver.page_source
  # driver.close()
  # # with open("big-test.html", 'w') as f:
  # #   f.write(res_text)

  # output = parse_course_search_page(res_text, cookie) # type: ignore
  # return Output(
  #   course_search_page=output,
  #   cookie_value=cookie_value, # type: ignore
  # )

async def finish_log_in(driver: webdriver.Chrome) -> Output:
  cookie_details = driver.get_cookie(cookie_name) # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
  if cookie_details is None:
    raise CookieError()
  cookie_value = cookie_details['value'] # pyright: ignore[reportUnknownVariableType]
  cookie = cookie_name + '=' + cookie_value # pyright: ignore[reportUnknownVariableType]

  res_text = driver.page_source

  # driver.get('https://ssologin.cuny.edu/')
  # print(driver.get_cookies())

  driver.close()

  output = parse_course_search_page(res_text, cookie) # type: ignore
  return Output(
    course_search_page=output,
    cookie_value=cookie_value, # type: ignore
  )