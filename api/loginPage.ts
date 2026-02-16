import * as cheerio from "cheerio";
import ScrapeError from "./scrapeError";

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

const loginPageErrorMessage = `unable to find expected HTML elements in the login
page. The login page may have changed since this web scraper was last
updated.`;

class LoginPageError extends ScrapeError {
  message(): string {
    return loginPageErrorMessage;
  }
}

interface ResponseData {
  pInstance: string,
  pPageSubmissionId: string,
  pPageItemsProtected: string
}

async function sendRequest(): Promise<string> {
  const res = await fetch(requestData.url, { headers: requestData.headers });
  return await res.text();
}

async function parseResponse(responseText: string): Promise<ResponseData> {
  const $ = cheerio.load(responseText);
  const pInstance = $("#pInstance").val();
  const pPageSubmissionId = $("#pPageSubmissionId").val();
  const pPageItemsProtected = $("#pPageItemsProtected").val();
  if (typeof pInstance !== "string" || typeof pPageSubmissionId !== "string" || typeof pPageItemsProtected !== "string") {
    throw new LoginPageError();
  }
  return {
    pInstance,
    pPageSubmissionId,
    pPageItemsProtected
  };
}

async function scrapeLoginPage(): Promise<ResponseData> {
  const responseText = await sendRequest();
  return parseResponse(responseText);
}

export default scrapeLoginPage;