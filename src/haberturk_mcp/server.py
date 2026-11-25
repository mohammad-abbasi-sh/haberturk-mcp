"""MCP server: unofficial read-only access to haberturk.com news."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import news as _N

mcp = FastMCP("haberturk-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for haberturk.com, one of Türkiye's
biggest national news portals (Ciner Media; 24.4M visits in October
2026, TR #40) — latest news from the Google News sitemap, breaking
news (son dakika, with times), headlines by section, full article
text, keyword search, and the section list. Data comes from the
site's server-rendered pages — no login, no API key. The Google News
sitemap (/sitemap_google_news.xml) carries the freshest ~600 items
with titles and publication times. Section pages (/<category>/:
gundem, ekonomi, dunya, spor, magazin, teknoloji, kultur-sanat,
saglik, yasam, bilgi, htgastro) list ~50 headlines each with no
pagination. The breaking-news page (/son-dakika-haberleri/) lists
the newest items with times. Article pages carry a full NewsArticle
JSON-LD block (title, author, publish/modify dates, description,
image, keywords, word count, full body text). Keyword search scans
the news sitemap plus the breaking-news page and the main section
listings (the site's own /arama/ search is disallowed in robots.txt
and returns a shell page with no results, so there is no
server-side search to call). Video (/video/) pages are not text news
and are excluded from listings; photo-news (/foto/) pages do carry
full article text and are included. Read-only; transport uses Chrome
TLS impersonation; requests are spaced ~0.8s apart.
Built by Mohammad Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir — Turkey MCP factory.\
"""


_SOURCE = "haberturk.com"
_DISCLAIMER = "Unofficial read-only data from haberturk.com; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


def _validate_limit(limit: int, lo: int = 1, hi: int = 30) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


@mcp.tool()
def haberturk_latest_news(limit: int = 10) -> str:
    """Latest Habertürk news from the Google News sitemap, newest
    first. limit 1..30. Returns items (publication time, section,
    title, article URL) — the freshest ~600 items on the site."""
    try:
        _validate_limit(limit)
        xml_text = _http.fetch_sitemap_news_xml()
        rows = _N.parse_sitemap_news(xml_text)
    except (ValueError, _http.HaberturkError) as e:
        return _err(e)
    return _ok({"count": min(limit, len(rows)), "articles": rows[:limit]})


@mcp.tool()
def haberturk_breaking_news(limit: int = 10) -> str:
    """Latest Habertürk breaking news (son dakika), newest first.
    limit 1..30. Returns items (time HH:MM Europe/Istanbul when the
    page carries one, section, title, article URL) from the
    /son-dakika-haberleri/ page."""
    try:
        _validate_limit(limit)
        html_text = _http.fetch_sondakika_html()
        rows = _N.parse_sondakika(html_text)
    except (ValueError, _http.HaberturkError) as e:
        return _err(e)
    return _ok({"count": min(limit, len(rows)), "articles": rows[:limit]})


@mcp.tool()
def haberturk_headlines(category: str = "gundem", limit: int = 10) -> str:
    """Top headlines in one Habertürk section. category: "gundem"
    (default), "ekonomi", "dunya", "spor", "magazin", "teknoloji",
    "kultur-sanat", "saglik", "yasam", "bilgi", "htgastro".
    limit 1..30. Returns headlines (title, section, article URL)."""
    try:
        category = (category or "gundem").strip().lower()
        if category not in _N.CATEGORIES:
            raise ValueError(
                f"category must be one of {', '.join(_N.CATEGORIES)}"
            )
        _validate_limit(limit)
        html_text = _http.fetch_category_html(category)
        rows = _N.parse_listing(html_text)
    except (ValueError, _http.HaberturkError) as e:
        return _err(e)
    return _ok({
            "category": category,
            "count": min(limit, len(rows)),
            "headlines": rows[:limit],
        })


@mcp.tool()
def haberturk_get_article(article_url: str) -> str:
    """Full text of one Habertürk article. article_url: the article's
    haberturk.com URL (as returned by the latest/breaking/headlines/
    search tools, e.g. "https://www.haberturk.com/gundem/son-dakika-
    60-ilde-280-kisi-yakalandi-yeni-nesil-suc-orgutlerine-darbe-
    3929975"). Returns title, author, publish/modify dates,
    description, image, keywords, word count and the full body text.
    Video pages have no article text and return an error."""
    try:
        if not article_url or not article_url.strip():
            raise ValueError("article_url must not be empty")
        html_text = _http.fetch_article_html(article_url.strip())
        data = _N.parse_article(html_text)
    except (ValueError, _http.HaberturkError) as e:
        return _err(e)
    return _ok(data)


@mcp.tool()
def haberturk_search_news(query: str, limit: int = 10) -> str:
    """Keyword search over recent Habertürk news: scans the Google
    News sitemap (~600 freshest items) plus the breaking-news page
    and the gundem, ekonomi, dunya, spor and magazin listings,
    matching the keyword in titles. query: e.g. "emekli", "deprem",
    "dolar". limit 1..30. Note: the site's own /arama/ search is
    disallowed in robots.txt and returns no results, so this
    searches the current listings instead of a search backend.
    Turkish-aware (dotted/dotless I handled, so "İSTANBUL"
    matches "İstanbul")."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        _validate_limit(limit)
        q = _N.tr_lower(query.strip())
        rows: list[dict] = []
        seen: set[str] = set()

        def _scan(candidates: list[dict]) -> None:
            for r in candidates:
                if r["url"] in seen:
                    continue
                seen.add(r["url"])
                hay = _N.tr_lower(r.get("title", ""))
                if q in hay:
                    rows.append(r)

        _scan(_N.parse_sitemap_news(_http.fetch_sitemap_news_xml()))
        _scan(_N.parse_sondakika(_http.fetch_sondakika_html()))
        for category in _N.SEARCH_CATEGORIES:
            if len(rows) >= limit:
                break
            _scan(_N.parse_listing(_http.fetch_category_html(category)))
    except (ValueError, _http.HaberturkError) as e:
        return _err(e)
    return _ok({"query": query.strip(),
         "count": min(limit, len(rows)), "articles": rows[:limit]})


@mcp.tool()
def haberturk_list_sections() -> str:
    """Habertürk news sections usable with haberturk_headlines, with
    their Turkish display names. No arguments."""
    return _ok({
        "sections": [
            {"slug": slug, "name": _N.CATEGORY_NAMES[slug]}
            for slug in _N.CATEGORIES
        ],
    })


@mcp.tool()
def haberturk_health() -> str:
    """Check whether haberturk.com is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
