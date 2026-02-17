import * as cheerio from "cheerio";

interface Input {
  ck: string,
  cookie: string,
  searchText: string,
  pInstance: string,
  pPageSubmissionId: string,
  protected_: string
}

function fillRequestData({
  ck,
  cookie,
  searchText,
  pInstance,
  pPageSubmissionId,
  protected_
}: Input) {
  return {
    url: `https://orapp.hunter.cuny.edu/ords/wwv_flow.accept?p_context=116:3:${pInstance}`,
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
      'p_json': `{"salt":"${pPageSubmissionId}","pageItems":{"itemsToSubmit":[{"n":"P3_LAST_NAME","v":"${searchText}"},{"n":"P3_LINK","v":"","ck":"${ck}"}],"protected":"${protected_}","rowVersion":"","formRegionChecksums":[]}}`,
      'p_flow_id': '116',
      'p_flow_step_id': '3',
      'p_instance': pInstance,
      'p_page_submission_id': pPageSubmissionId,
      'p_request': 'P3_GO',
      'p_reload_on_submit': 'A',
    }
  };
}

async function sendRequest(input: Input): Promise<string> {
  const requestData = fillRequestData(input);
  const res = await fetch(requestData.url, {
    headers: requestData.headers,
    method: "POST",
    body: JSON.stringify(requestData.formData)
  });
  return await res.text();
}

async function parseResponse(responseText: string): Promise<string[]> {
  const $ = cheerio.load(responseText);
  const courses = $("[headers=COURSE]").map((_, courseElement) => $(courseElement).text()).toArray();
  return courses;
}

async function searchByProfessor(
  ck: string,
  cookie: string,
  searchText: string,
  pInstance: string,
  pPageSubmissionId: string,
  protected_: string
): Promise<string[]> {
  const responseText = await sendRequest({
    ck,
    cookie,
    searchText,
    pInstance,
    pPageSubmissionId,
    protected_
  });
  return parseResponse(responseText);
}

export default searchByProfessor;