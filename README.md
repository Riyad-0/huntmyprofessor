# HuntMyProfessor

HuntMyProfessor is a web scraper for Hunter College's evaluation reports website. Students can see how their peers have rated their professors and rank them by rating or A's given out. The scraped data can be viewed at the project's website: https://huntmyprofessor.vercel.app.

## Modules
- `main.py` - the scraping CLI
- `gh-main.py` - the entry point for GitHub Actions
- `scrape/` - scraping library
- `web/` - web frontend
- `.github/workflows` - workflows for scraping on GitHub Actions

## Scraping
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

`OTP_KEY` can be obtained by following the instructions in  ["Automating Multi-Factor Authentication".](#automating-multi-factor-authentication)

Scraping with GitHub requires `GITHUB_TOKEN` and `GITHUB_REPOSITORY`

Syncing with remote requires `SUPABASE_URL` and `SUPABASE_KEY`.

An example `.env` file:
```
EMAIL=<SECRET>@login.cuny.edu
PASSWORD=<SECRET>
OTP_KEY=<SECRET>
GITHUB_REPOSITORY=<username>/<repo>
GITHUB_TOKEN=github_pat_<SECRET>
SUPABASE_URL=https://<SECRET>.supabase.co
SUPABASE_KEY=sb_secret_<SECRET>
```

## Automating Multi-Factor Authentication
To get the `OTP_KEY`, follow CUNY's guide to add a CUNY Authentication Factor here: https://cunyithelp.cuny.edu/sp?id=kb_article_view&sys_kb_id=79466cba93973a900c96f4647aba10b5

It will tell you how to use [CUNY's MFA self-service.](https://ssologin.cuny.edu/oaa/rui/index.html)

Note that you cannot use your existing Authentication Factor unless you copied the Secret Key when you first set it up, which you probably did not.

When CUNY tells you to enter the Secret Key into your authenticator app, make sure you copy it and save it somewhere safe. This is the `OTP_KEY`.

Follow the remaining steps of the guide to add this Authentication Factor to your authenticator app and verify it.

Make sure you set the new Authentication Factor as Default, or else CUNY will reject its passcodes. Since you can only have one Default, this means your old Authentication Factor's passcodes will stop working. I just deleted my old one afterward.

CUNY seems to distinguish Authentication Factors based on their Friendly Name, which I learned the hard way. I suggest not reusing the same Friendly Name as your existing Authentication Factor. Deleting it first might prevent issues, but I was not willing to take the risk.

The OTP is generated using the PyOTP library like this:
``` python
import pyotp
pyotp.TOTP(otp_key).now()
```

## `scrape/`
The following modules contain the scraping code to perform tasks a user would normally do to access evaluation reports manually.
- `_select_dept/` - "select" the Computer Science department
- `_select_subject/` - "select" CSCI to get back a list of CSCI course numbers
- `_course_search/` - submit a course search
- `_fetch_max_rows/` - request 2000 rows instead of 20 in the search results
- `_open_eval_report/` - "click" the link to the eval report

## GitHub Actions Workflows
- `.github/workflows/debug.yml` - debug, for testing a small number of reports
- `.github/workflows/release.yml` - scrape the whole site