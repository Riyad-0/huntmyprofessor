import cookieName from "./cookieName";

function parseCookie(cookies: string[]): string | undefined {
  const foundCookie = cookies.find(cookie => cookie.startsWith(cookieName + "="));
  if (foundCookie === undefined) {
    return undefined;
  }
  const end = foundCookie.indexOf(";");
  if (end === -1) {
    return foundCookie;
  } else {
    return foundCookie.slice(0, end);
  }
}

export default parseCookie;