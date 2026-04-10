import json
import os
from typing import Any
from pathlib import Path
import requests
from requests.sessions import RequestsCookieJar
from requests.structures import CaseInsensitiveDict
from urllib.parse import parse_qs

dir_name = os.path.dirname(__file__)
file_path = os.path.join(dir_name, "a.html")

with open(file_path) as f:
  text = f.read()

pattern = '(function(){apex.widget.selectList("#P6_SUBJECT"'
i = text.find(pattern)
print(i)
i += len(pattern)
pattern = '"ajaxIdentifier":"'
j = text.find(pattern, i)
print(j)
start = j + len(pattern)
end = text.find('"', start)
print(end)
ajax_identifier = text[start:end]
print(ajax_identifier)
print(start, end, len(ajax_identifier))
print(text[start:start+10])