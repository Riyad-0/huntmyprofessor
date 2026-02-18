import * as cheerio from "cheerio";
import ScrapeError from "./scrapeError";
import parseCookie from "./parseCookie";
import log from "./log";

interface Input {
  cookie: string,
  username: string,
  password: string,
  pInstance: string,
  pPageSubmissionId: string,
  protected_: string
}

interface ResponseData {
  ck: string,
  cookie: string
  pPageSubmissionId: string,
  pPageItemsProtected: string,
}

interface RawResponseData {
  text: string,
  cookies: string[]
}

const searchPageHTMLErrorMessage = `expected HTML elements were not found in the
search page. The search page may have changed since this web scraper was last
updated.`;

const logInCookieErrorMessage = `expected cookie was not set after logging in.
This web scraper may need to be updated.`;

class HTMLError extends ScrapeError {
  missing: string[];
  responseText: string;

  constructor(
    missing: string[],
    responseText: string
  ) {
    super();
    this.missing = missing;
    this.responseText = responseText;
  }

  message(): string {
    const missingMessage = `missing elements: ${this.missing}`;
    const responseTextMessage = `response text:\n${this.responseText}`;
    return searchPageHTMLErrorMessage + "\n" +
      missingMessage + "\n" +
      responseTextMessage;
  }
}

class CookieError extends ScrapeError {
  message(): string {
    return logInCookieErrorMessage;
  }
}

function fillRequestData({
  cookie,
  username,
  password,
  pInstance,
  pPageSubmissionId,
  protected_
}: Input) {
  return {
    url: `https://orapp.hunter.cuny.edu/ords/wwv_flow.accept?p_context=116:101:${pInstance}`,
    headers: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': cookie,
      'Host': 'orapp.hunter.cuny.edu',
      'Origin': 'https://orapp.hunter.cuny.edu',
      'Referer': 'https://orapp.hunter.cuny.edu/',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-User': '?1',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
      'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
    },
    formData: {
      'p_json': `{"salt":"${pPageSubmissionId}","pageItems":{"itemsToSubmit":[{"n":"P101_USERNAME","v":"${username}"},{"n":"P101_PASSWORD","v":"${password}"}],"protected":"${protected_}","rowVersion":"","formRegionChecksums":[]}}`,
      'p_flow_id': '116',
      'p_flow_step_id': '101',
      'p_instance': pInstance,
      'p_page_submission_id': pPageSubmissionId,
      'p_request': 'P101_LOGIN',
      'p_reload_on_submit': 'A',
    }
  };
}

async function sendRequest(input: Input): Promise<RawResponseData> {
  const requestData = fillRequestData(input);
  log(JSON.stringify(requestData, null, 2));
  throw new CookieError();
  const res = await fetch(requestData.url, {
    headers: requestData.headers,
    method: "POST",
    body: JSON.stringify(requestData.formData)
  });
  const text = await res.text();
  const cookies = res.headers.getSetCookie()
  return { text, cookies };
}

async function parseResponse(rawResponseData: RawResponseData): Promise<ResponseData> {
  const $ = cheerio.load(rawResponseData.text);
  const ck = $("[data-for=P3_LINK]").val();
  const pPageSubmissionId = $("#pPageSubmissionId").val();
  const pPageItemsProtected = $("#pPageItemsProtected").val();
  if (typeof ck !== "string" || typeof pPageSubmissionId !== "string" || typeof pPageItemsProtected !== "string") {
    const missing = [];
    if (typeof ck !== "string") {
      missing.push("ck");
    }
    if (typeof pPageSubmissionId !== "string") {
      missing.push("pPageSubmissionId");
    }
    if (typeof pPageItemsProtected !== "string") {
      missing.push("pPageItemsProtected");
    }
    throw new HTMLError(missing, rawResponseData.text);
  }
  const cookie = parseCookie(rawResponseData.cookies);
  if (cookie === undefined) {
    throw new CookieError();
  }
  return {
    ck,
    cookie,
    pPageSubmissionId,
    pPageItemsProtected
  };
}

async function signIn(
  cookie: string,
  username: string,
  password: string,
  pInstance: string,
  pPageSubmissionId: string,
  protected_: string
): Promise<ResponseData> {
  const responseText = await sendRequest({
    cookie,
    username,
    password,
    pInstance,
    pPageSubmissionId,
    protected_
  });
  return parseResponse(responseText);
}

export default signIn;