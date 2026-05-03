from typing import Any

from fastapi import FastAPI
import httpx
from httpx_limiter import AsyncRateLimitedTransport, Rate
from httpx_limiter.aiolimiter import AiolimiterAsyncLimiter
from pydantic import BaseModel
from scrape.open_all_eval_reports import open_all_eval_reports
from scrape._eval_report import EvalReport
from scrape.data import fetch_data
from scrape.log import clear_log, log
from scrape.scrape_error import ScrapeError
from scrape.open_login_page import open_login_page
from scrape._log_in import log_in
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
async def login(login: Login):
  async with httpx.AsyncClient(follow_redirects=True) as client:
    output = await open_login_page(client)
    output = await log_in(client, output, login.username, login.password)
    output = await professor_search(client, output, search_text="washburn, alexander")
    print(output.courses)
    
    return LoginResult(
      result="success",
      courses=output.courses,
    )

@app.post("/api/courses")
async def courses2(login: Login):  
  clear_log()
  data = fetch_data()
  limiter = AiolimiterAsyncLimiter.create(Rate.create(magnitude=1, duration=0.1))
  async with httpx.AsyncClient(
    follow_redirects=True,
    transport=AsyncRateLimitedTransport.create(limiter=limiter),
  ) as client:
    try:
      output = await open_login_page(client)
      output = await log_in(client, output, login.username, login.password)
      open_course_search_page_output = await open_course_search_page(client, output)
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
          # l += 1
          # if l >= 15:
          #   break
        # log.warning(f"Found {len(search_output.course_sections)} evals for: CSCI {course_num}")
        
        # course_sections = search_output.course_sections
        # paginate_codes = search_output.paginate_codes
        # if did_fetch_max_rows or paginate_codes is None:
        #   l = 0
        #   for output in open_eval_reports(s, cookie=cookie, course_sections=course_sections):
        #     if output.cookie is not None:
        #       cookie = output.cookie
        #     eval_report = output.eval_report
        #     eval_reports.append(eval_report)
        #     data.add(eval_report)
        #     data.write()
        #     data.write_json()
        #     l += 1
        #     if l >= 30:
        #       break
        # else:
        #   did_fetch_max_rows = True
        #   output = fetch_max_rows(
        #     s,
        #     cookie=cookie,
        #     p_instance=search_output.p_instance,
        #     p_page_submission_id=search_output.p_page_submission_id,
        #     paginate_codes=paginate_codes
        #   )
        #   if output.cookie is not None:
        #     cookie = output.cookie
        #   course_sections = output.course_sections
        #   l = 0
        #   for output in open_eval_reports(s, cookie=cookie, course_sections=course_sections):
        #     if output.cookie is not None:
        #       cookie = output.cookie
        #     eval_report = output.eval_report
        #     eval_reports.append(eval_report)
        #     data.add(eval_report)
        #     data.write()
        #     data.write_json()
        #     l += 1
        #     if l >= 30:
        #       break
            
          # output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
          # eval_reports = output.eval_reports
          # for eval_report in output.eval_reports:
          #   eval_reports.append(eval_report)
          #   data.add(eval_report)
          #   data.write()
          #   data.write_json()
          # l += len(eval_reports)
        # data.add_all(eval_reports=eval_reports)
          
      # with open("out.json", "w") as f:
      #   json.dump(eval_reports, f, indent=2, default=json_default)
      # data.write()
      # data.write_json()
      return CourseSearchResult(result="success")
    except Exception as e:
      if isinstance(e, ScrapeError):
        print(e.message())
        return CourseSearchError(result="error", message=e.message())
      else:
        raise e

# @app.post("/api/courses")
# def courses(login: Login):  
#   clear_log()
#   data = fetch_data()
#   s = requests.Session()
#   try:
#     output = open_login_page(s)
#     output = log_in(s, output, login.username, login.password)
#     open_course_search_page_output = open_course_search_page(s, output)
#     output = select_dept(s, open_course_search_page_output)
#     output = select_subject(s, open_course_search_page_output)
#     course_number_options = output.course_number_options
#     l = 0
#     for course_num in course_number_options:
#       search_output = course_search(
#         s,
#         open_course_search_page_output,
#         data,
#         department="CSCI-HTR",
#         subject="CSCI",
#         course_num=course_num,
#       )
#       course_sections = search_output.course_sections
#       cookie = search_output.cookie
#       eval_reports: list[EvalReport] = []
#       for output in open_eval_reports(s, cookie=cookie, course_sections=course_sections):
#         if output.cookie is not None:
#           cookie = output.cookie
#         eval_report = output.eval_report
#         eval_reports.append(eval_report)
#         data.add(eval_report)
#         data.write()
#         data.write_json()
#         l += 1
#         if l >= 20:
#           break
#       paginate_codes = search_output.paginate_codes
#       if paginate_codes is not None:
#         output = fetch_next_rows(
#           s,
#           cookie=cookie,
#           p_instance=search_output.p_instance,
#           p_page_submission_id=search_output.p_page_submission_id,
#           paginate_codes=paginate_codes
#         )
#         if output.cookie is not None:
#           cookie = output.cookie
#         course_sections = output.course_sections
#         for output in open_eval_reports(s, cookie=cookie, course_sections=course_sections):
#           if output.cookie is not None:
#             cookie = output.cookie
#           eval_report = output.eval_report
#           eval_reports.append(eval_report)
#           data.add(eval_report)
#           data.write()
#           data.write_json()
#           l += 1
#           if l >= 20:
#             break
          
#         # output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
#         # eval_reports = output.eval_reports
#         # for eval_report in output.eval_reports:
#         #   eval_reports.append(eval_report)
#         #   data.add(eval_report)
#         #   data.write()
#         #   data.write_json()
#         # l += len(eval_reports)
#       # data.add_all(eval_reports=eval_reports)
        
#     # with open("out.json", "w") as f:
#     #   json.dump(eval_reports, f, indent=2, default=json_default)
#     # data.write()
#     # data.write_json()
#     return CourseSearchResult(result="success")
#   except Exception as e:
#     if isinstance(e, ScrapeError):
#       print(e.message())
#       return CourseSearchError(result="error", message=e.message())
#     else:
#       raise e

# # @app.post("/api/coursesold")
# # def coursesold(login: Login):
# #   print("HELLO!")
# #   clear_log()
# #   s = requests.Session()
# #   try:
# #     output = open_login_page(s)
# #     output = sign_in(s, output, login.username, login.password)
# #     open_course_search_page_output = open_course_search_page(s, output)
# #     output = select_dept(s, open_course_search_page_output)
# #     output = select_subject(s, open_course_search_page_output)
# #     course_number_options = output.course_number_options
# #     search_output = course_search(
# #       s,
# #       open_course_search_page_output,
# #       department="ENGL-HTR",
# #       subject="ENGL",
# #       course_num="12000",
# #       # department="CSCI-HTR",
# #       # subject="CSCI",
# #       # course_num="33500",
# #     )
# #     course_sections = search_output.course_sections
# #     cookie = search_output.cookie
# #     output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
# #     cookie = output.cookie
# #     eval_reports = output.eval_reports
# #     # eval_reports: list[EvalReport] = []
# #     # for course_section in course_sections:
# #     #   if course_section.url is not None:
# #     #     output = open_eval_report(s, cookie=cookie, url=course_section.url)
# #     #     cookie = output.cookie
# #     #     eval_reports.append(EvalReport(
# #     #       course=course_section.course,
# #     #       semester=course_section.semester,
# #     #       professor=course_section.professor,
# #     #       page=EvalReportPage(
# #     #         url=course_section.url,
# #     #         score_sections=output.score_sections,
# #     #         expected_grades=output.expected_grades
# #     #       ),
# #     #     ))
# #     #   else:
# #     #     eval_reports.append(EvalReport(
# #     #       course=course_section.course,
# #     #       semester=course_section.semester,
# #     #       professor=course_section.professor,
# #     #       page=None,
# #     #     ))
# #     paginate_codes = search_output.paginate_codes
# #     if paginate_codes is not None:
# #       output = open_next_page(
# #         s,
# #         cookie=cookie,
# #         p_instance=search_output.p_instance,
# #         p_page_submission_id=search_output.p_page_submission_id,
# #         paginate_codes=paginate_codes
# #       )
# #       if output.cookie is not None:
# #         cookie = output.cookie
# #       course_sections = output.course_sections
# #       # TODO
# #       print("LENGO:", len(course_sections))
# #       return CourseSearchResult(result="success")
# #       output = open_eval_reports(s, cookie=cookie, course_sections=course_sections)
# #       # TODO
# #       eval_reports = output.eval_reports
# #       # for eval_report in output.eval_reports:
# #       #   eval_reports.append(eval_report)
      
# #     with open("out.json", "w") as f:
# #       json.dump(eval_reports, f, indent=2, default=json_default)
# #     # print(eval_reports)
# #     return CourseSearchResult(result="success")
# #   except Exception as e:
# #     if isinstance(e, ScrapeError):
# #       print(e.message())
# #       return CourseSearchError(result="error", message=e.message())
# #     else:
# #       raise e
    
# def json_default(obj: Any):
#   if hasattr(obj, "__dict__"):
#       return obj.__dict__
#   raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")