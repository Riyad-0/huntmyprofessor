import * as cheerio from "cheerio"

export default function test() {
  const $ = cheerio.load(`<input data-for=P3_LINK value=cool />`);
  const ck = $("[data-for=P3_LINK]").val();
  return ck;
}