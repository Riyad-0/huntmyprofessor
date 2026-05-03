from dataclasses import dataclass

from scrape._data import Data

schema_file_name = 'schema.json'
evals_file_name = 'evals.txt'
json_file_name = 'evals.json'

@dataclass
class LocalStore:
  data: Data
  

