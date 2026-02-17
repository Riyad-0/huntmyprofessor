import * as cheerio from "cheerio";
import ScrapeError from "./scrapeError";
import cookieName from "./cookieName";

const requestData = {
  url: "https://www.hunter.cuny.edu/myprof",
  headers: {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    'Host': 'orapp.hunter.cuny.edu',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
  }
};

const loginPageHTMLErrorMessage = `expected HTML elements were not found in the
login page. The login page may have changed since this web scraper was last
updated.`;

const loginPageCookieErrorMessage = `expected cookie was not set after
accessing the login page. The login page may have changed since this web scraper was last
updated.`;

class HTMLError extends ScrapeError {
  message(): string {
    return loginPageHTMLErrorMessage;
  }
}

class CookieError extends ScrapeError {
  message(): string {
    return loginPageCookieErrorMessage;
  }
}

interface RawResponseData {
  text: string,
  cookies: string[]
}

interface ResponseData {
  cookie: string,
  pInstance: string,
  pPageSubmissionId: string,
  pPageItemsProtected: string
}

async function sendRequest(): Promise<RawResponseData> {
  const res = await fetch(requestData.url, { headers: requestData.headers });
  const text = await res.text();
  const cookies = res.headers.getSetCookie()
  return { text, cookies };
}

async function parseResponse(rawResponseData: RawResponseData): Promise<ResponseData> {
  const $ = cheerio.load(rawResponseData.text);
  const pInstance = $("#pInstance").val();
  const pPageSubmissionId = $("#pPageSubmissionId").val();
  const pPageItemsProtected = $("#pPageItemsProtected").val();
  if (typeof pInstance !== "string" || typeof pPageSubmissionId !== "string" || typeof pPageItemsProtected !== "string") {
    throw new HTMLError();
  }
  const cookie = rawResponseData.cookies.find(cookie => cookie.startsWith(cookieName + "="));
  if (cookie === undefined) {
    throw new CookieError();
  }
  return {
    cookie,
    pInstance,
    pPageSubmissionId,
    pPageItemsProtected
  };
}

// async function parseCookie(cookies: string[]): Promise<string> {
//   for (const cookie of cookies) {
//     const split = cookie.split("=", 2);
//     if (split[0] === cookieName) {
//       const cookieValue = cookieName[1];
//       if (cookieValue !== undefined) {
//         return cookieValue;
//       }
//       break;
//     }
//   }
//   throw new CookieError();
// }

async function scrapeLoginPage(): Promise<ResponseData> {
  const responseText = await sendRequest();
  return parseResponse(responseText);
}

export default scrapeLoginPage;