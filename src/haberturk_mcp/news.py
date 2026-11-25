"""Stdlib parsing for haberturk.com server-rendered news pages.

Verified live 2026-11-25 against real pages (fixtures in tests/):
- Section pages (/gundem/ 129KB, /ekonomi/ 220KB): article cards
  are <a> anchors carrying data-newsid, data-newsname (title),
  data-newscategory and href="/<section>/<slug>-<7-digit-id>".
  ~50-60 cards per section page (slider + list), no pagination.
  /teknoloji/ 301-redirects to /ekonomi/teknoloji.
- /son-dakika-haberleri/ (91KB): breaking-news boxes
  (data-type="box-type2-breaking-news") with <a href title>
  anchors; items carry a date span
  (<span data-name="date">25 Kasım 2026, Çarşamba
  <span class="font-bold text-red-600">HH:MM</span></span>).
  52 items on the probed page. Photo-news (/foto/) items are
  real articles with full text — kept in listings.
- Google News sitemap (/sitemap_google_news.xml, 416KB): 593
  <url> entries with <loc>, <lastmod>, <news:title> (CDATA) and
  <news:publication_date> — the freshest ~2 days of news.
- Homepage (357KB): ~146 article links across all sections.
- Article pages (106-157KB): full NewsArticle JSON-LD (headline,
  description, author as Person, datePublished/dateModified,
  image, keywords, wordCount, articleSection, articleBody as one
  plain-text block). The site's own sanitizer strips apostrophes
  inside articleBody ("Bakanlığı ndan") — text is still complete.
  Photo-news (/foto/) pages also carry a full NewsArticle block.
- Video (/video/) pages carry a VideoObject, no article text —
  excluded from listings; get_article on them raises a clear error.
"""
from __future__ import annotations

import html
import json
import re

CATEGORIES = (
    "gundem", "ekonomi", "dunya", "spor", "magazin",
    "teknoloji", "kultur-sanat", "saglik", "yasam", "bilgi",
    "htgastro",
)

# URL path per section slug ("teknoloji" lives under /ekonomi/).
CATEGORY_PATHS = {
    "gundem": "gundem",
    "ekonomi": "ekonomi",
    "dunya": "dunya",
    "spor": "spor",
    "magazin": "magazin",
    "teknoloji": "ekonomi/teknoloji",
    "kultur-sanat": "kultur-sanat",
    "saglik": "saglik",
    "yasam": "yasam",
    "bilgi": "bilgi",
    "htgastro": "htgastro",
}

CATEGORY_NAMES = {
    "gundem": "Gündem",
    "ekonomi": "Ekonomi",
    "dunya": "Dünya",
    "spor": "Spor",
    "magazin": "Magazin",
    "teknoloji": "Teknoloji",
    "kultur-sanat": "Kültür Sanat",
    "saglik": "Sağlık",
    "yasam": "Yaşam",
    "bilgi": "Bilgi",
    "htgastro": "HT Gastro",
}

# Search scans these sections (the site's own /arama/ is disallowed
# in robots.txt and returns a shell page with no results, so there
# is no server-side search to call).
SEARCH_CATEGORIES = ("gundem", "ekonomi", "dunya", "spor", "magazin")

_TR_UPPER_TO_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ",
    "Ü": "ü", "Ö": "ö", "Ç": "ç",
})


def tr_lower(s: str) -> str:
    """Turkish-aware lowercase (str.lower() mangles İ -> i + dot)."""
    return s.translate(_TR_UPPER_TO_LOWER).lower()


def tr_title(s: str) -> str:
    """Turkish-aware title case for one word (str.title() mangles İ)."""
    s = tr_lower(s.strip())
    return s[:1].upper() + s[1:] if s else s


def _clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- listings

# Video pages carry a VideoObject and no article text.
_SKIP_SEGMENTS = ("/video/",)

# Article hrefs end in a 7-digit id: /<section>/<slug>-<id>
_ARTICLE_RE = re.compile(r'href="([^"]+-\d{7})"', re.S)

# Section cards: <a ... data-newsid="..." data-newsname="..."
# data-newscategory="..." ... href="..."> (attribute order varies).
_CARD_RE = re.compile(
    r'<a\b[^>]*data-newsid="\d+"[^>]*>',
    re.S,
)


def _section_from_url(url: str) -> str:
    m = re.match(r"https?://www\.haberturk\.com/([^/]+)/", url)
    if not m:
        return ""
    seg = m.group(1)
    if seg in CATEGORY_NAMES:
        return CATEGORY_NAMES[seg]
    return tr_title(seg.replace("-", " "))


def parse_listing(html_text: str) -> list[dict]:
    """Article links on a listing page -> [{url, title, section}]."""
    by_url: dict[str, dict] = {}
    for m in _CARD_RE.finditer(html_text):
        tag = m.group(0)
        href = re.search(r'href="([^"]+-\d{7})"', tag)
        if not href:
            continue
        path = href.group(1)
        if any(seg in path for seg in _SKIP_SEGMENTS):
            continue
        name = re.search(r'data-newsname="([^"]*)"', tag)
        title = _clean(name.group(1)) if name else ""
        if not title:
            t = re.search(r'title="([^"]*)"', tag)
            title = _clean(t.group(1)) if t else ""
        if not title:
            continue
        url = "https://www.haberturk.com" + path
        row = {"url": url, "title": title}
        section = _section_from_url(url)
        if section:
            row["section"] = section
        prev = by_url.get(url)
        if prev is None or len(row["title"]) > len(prev.get("title", "")):
            by_url[url] = row
    return list(by_url.values())


# ---------------------------------------------------------------- son dakika

# One breaking-news box: <div data-type="box-type2-breaking-news"
# ...> ... <a href="...-id" title="..."> ... <span data-name="date">
# ... <span class="font-bold text-red-600">HH:MM </span></span>
_BOX_RE = re.compile(
    r'data-type="box-type2-breaking-news"(.*?)(?=data-type="box-type2-breaking-news"|$)',
    re.S,
)
_BOX_LINK_RE = re.compile(
    r'<a\b[^>]*href="([^"]+-\d{7})"[^>]*title="([^"]*)"[^>]*>',
    re.S,
)
_BOX_TIME_RE = re.compile(
    r'<span class="font-bold text-red-600">\s*(\d{2}:\d{2})\s*</span>'
)


def parse_sondakika(html_text: str) -> list[dict]:
    """Breaking-news page -> [{time?, section, url, title}] in page
    order (newest first)."""
    rows: list[dict] = []
    seen: set[str] = set()
    for block in _BOX_RE.findall(html_text):
        link = _BOX_LINK_RE.search(block)
        if not link:
            continue
        path, title = link.group(1), _clean(link.group(2))
        if any(seg in path for seg in _SKIP_SEGMENTS):
            continue
        url = "https://www.haberturk.com" + path
        if url in seen or not title:
            continue
        seen.add(url)
        row: dict = {
            "section": _section_from_url(url),
            "url": url,
            "title": title,
        }
        t = _BOX_TIME_RE.search(block)
        if t:
            row["time"] = t.group(1)
        rows.append(row)
    return rows


# ---------------------------------------------------------------- news sitemap

_URL_RE = re.compile(r"<url>(.*?)</url>", re.S)


def parse_sitemap_news(xml_text: str) -> list[dict]:
    """Google News sitemap -> [{url, title, published, section}]
    newest first (the sitemap is already newest-first)."""
    rows: list[dict] = []
    for block in _URL_RE.findall(xml_text):
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        title = re.search(r"<news:title><!\[CDATA\[(.*?)\]\]></news:title>", block, re.S)
        if not title:
            title = re.search(r"<news:title>([^<]+)</news:title>", block)
        pub = re.search(r"<news:publication_date>([^<]+)</news:publication_date>", block)
        if not loc or not title:
            continue
        url = loc.group(1).strip()
        if any(seg in url for seg in _SKIP_SEGMENTS):
            continue
        row: dict = {
            "url": url,
            "title": _clean(title.group(1)),
            "published": pub.group(1).strip() if pub else "",
        }
        section = _section_from_url(url)
        if section:
            row["section"] = section
        rows.append(row)
    return rows


# ---------------------------------------------------------------- article

def parse_article(html_text: str) -> dict:
    """Article page -> title, author, dates, description, image,
    keywords, body (full text), word_count, section, url."""
    for m in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>',
        html_text, re.S,
    ):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "NewsArticle":
            return _article_from_jsonld(data)
    # Fallback: plain paragraphs inside the article content div.
    return _article_from_html(html_text)


def _article_from_jsonld(data: dict) -> dict:
    out: dict = {}
    title = _clean(data.get("headline"))
    # JSON-LD headlines carry a site suffix ("... - Habertürk Son
    # Dakika Haber", "... - Haberler - Habertürk") — strip it.
    title = re.sub(r"\s+-\s+(Haberler\s+-\s+)?Habertürk.*$", "", title)
    out["title"] = title
    out["description"] = _clean(data.get("description"))
    author = data.get("author")
    if isinstance(author, dict):
        out["author"] = _clean(author.get("name"))
    elif isinstance(author, str):
        out["author"] = _clean(author)
    out["date_published"] = data.get("datePublished") or data.get("dateCreated") or ""
    out["date_modified"] = data.get("dateModified") or ""
    image = data.get("image")
    if isinstance(image, dict):
        out["image"] = image.get("url") or ""
    elif isinstance(image, str):
        out["image"] = image
    elif isinstance(image, list) and image:
        first = image[0]
        out["image"] = first.get("url", "") if isinstance(first, dict) else str(first)
    keywords = data.get("keywords")
    if isinstance(keywords, list):
        out["keywords"] = [str(k) for k in keywords if k]
    elif isinstance(keywords, str):
        out["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]
    if data.get("wordCount"):
        try:
            out["word_count"] = int(data["wordCount"])
        except (TypeError, ValueError):
            pass
    out["section"] = _clean(data.get("articleSection"))
    page = data.get("mainEntityOfPage")
    if isinstance(page, dict) and page.get("@id"):
        out["url"] = page["@id"]
    body = data.get("articleBody")
    if not body or not str(body).strip():
        raise ValueError("article has no body text (articleBody empty)")
    out["body"] = re.sub(r"\s+", " ", str(body)).strip()
    return {k: v for k, v in out.items() if v not in (None, "", [])}


def _article_from_html(html_text: str) -> dict:
    out: dict = {}

    def _meta(name: str) -> str | None:
        mm = re.search(
            rf'<meta[^>]+(?:property|name)="{re.escape(name)}"[^>]+content="([^"]*)"',
            html_text,
        )
        return html.unescape(mm.group(1)) if mm else None

    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S)
    if m:
        out["title"] = _clean(m.group(1))
    if not out.get("title"):
        m = re.search(r"<title>(.*?)</title>", html_text, re.S)
        if m:
            out["title"] = _clean(m.group(1)).split(" - Habertürk")[0]

    out["description"] = _meta("description") or _meta("og:description") or ""
    out["date_published"] = _meta("datePublished") or ""
    out["date_modified"] = _meta("dateModified") or ""
    out["image"] = _meta("og:image") or ""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', html_text)
    if m:
        out["url"] = m.group(1)

    paras = []
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", html_text, re.S):
        text = _clean(pm.group(1))
        if not text or len(text) < 40:
            continue
        if re.match(r"\d{2}\.\d{2}\.\d{4}", text):
            continue  # date line, not body text
        if text.endswith(("(DHA)", "(AA)", "(İHA)")):
            continue  # agency byline, not body text
        paras.append(text)
    if not paras:
        raise ValueError("no article body found on this page")
    out["body"] = "\n\n".join(paras)
    out["paragraph_count"] = len(paras)
    return {k: v for k, v in out.items() if v not in (None, "")}
