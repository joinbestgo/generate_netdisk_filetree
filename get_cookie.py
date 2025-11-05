import browser_cookie3
from http.cookiejar import Cookie
from typing import Iterable

BROWSER_READERS = {
    "chrome": browser_cookie3.chrome,
    "chromium": browser_cookie3.chromium,
    "brave": browser_cookie3.brave,
    "edge": browser_cookie3.edge,
    "firefox": browser_cookie3.firefox,
    "safari": browser_cookie3.safari,
    # 也有 opera / vivaldi 等，可按需补充
}

def _iter_cookies(browser: str):
    browser = browser.lower()
    if browser not in BROWSER_READERS:
        raise ValueError(f"不支持的浏览器: {browser}")
    cj = BROWSER_READERS[browser]()   # CookieJar
    return cj

def get_cookies_for_domain(domain_keyword: str,
                           browser: str = "chrome") -> list[dict]:
    """
    domain_keyword: 例如 'example.com'，会匹配 cookie.domain 中包含该片段的条目
    返回: [{name,value,domain,path,secure,expires}]
    """
    jar = _iter_cookies(browser)
    out = []
    for c in jar:  # type: Cookie
        if domain_keyword in c.domain:
            out.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "expires": c.expires,
                "httponly": c._rest.get("HttpOnly") == "HttpOnly"
            })
    return out

def build_cookie_header(cookies: Iterable[dict]) -> str:
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)

if __name__ == "__main__":
    domain = "alice-int.mercedes-benz.com"
    cookies = get_cookies_for_domain(domain, browser="firefox")
    header = build_cookie_header(cookies)
    print("匹配到条数:", len(cookies))
    print("Cookie Header:")
    print(header)
