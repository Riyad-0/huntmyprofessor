# HuntMyProfessor

## Modules
- `main.py` - the CLI
- `gh-main.py` - the entry point for GitHub Actions
- `scrape/` - functionality for scraping
- `web/` - web frontend
- `.github/workflows` - workflows for scraping on GitHub Actions

## `main.py`
Run the CLI:
```
> py main.py 
HuntMyProfessor
0. Quit
1. Scrape
2. Scrape on GitHub Actions (debug)
3. Scrape on GitHub Actions (release)
4. Sync with remote
Choose: 1
```

## Environment Variables
`EMAIL`, `PASSWORD`, and `OTP_KEY` will allow automatic insertion of all login details.

Scraping with GitHub requires `GITHUB_TOKEN` and `GITHUB_REPOSITORY`

Syncing with remote requires `SUPABASE_URL` and `SUPABASE_KEY`.

An example `.env` file:
```
EMAIL=<SECRET>@login.cuny.edu
PASSWORD=<SECRET>
OTP_KEY=<SECRET>
GITHUB_REPOSITORY=Riyad-0/huntmyprofessor
GITHUB_TOKEN=github_pat_<SECRET>
SUPABASE_URL=https://<SECRET>.supabase.co
SUPABASE_KEY=sb_secret_<SECRET>
```

## `scrape/`
- `_select_dept/` - "select" the Computer Science department
- `_select_subject/` - "select" CSCI to get back a list of course numbers
- `_course_search/` - submit a course search
- `_fetch_max_rows/` - request 2000 rows instead of 20 in the search results
- `_open_eval_report/` - "click" the link to the eval report

## GitHub Actions Workflows
- `.github/workflows/debug.yml` - debug, for testing a small number of reports
- `.github/workflows/release.yml` - scrape the whole site