# haberturk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/haberturk-mcp

Unofficial **read-only** MCP server for **Habertürk** (www.haberturk.com) — one of Türkiye's biggest national news portals (Ciner Media; 24.4M visits in October 2026, TR #40): **latest news** from the Google News sitemap, **breaking news** (son dakika, with times), **headlines by section**, **full article text**, **keyword search**, and the **section list**.

> Part of the "Turkey MCP factory". Not affiliated with Habertürk. Data comes from Habertürk's own server-rendered pages — no login, no API key, read-only.

## For AI agents

- **Latest news**: `haberturk_latest_news` returns the freshest items from the Google News sitemap (`/sitemap_google_news.xml`, ~600 items with publication times), newest first.
- **Breaking news**: `haberturk_breaking_news` returns the newest items from `/son-dakika-haberleri/` (time HH:MM Europe/Istanbul when the page carries one, section, title, URL), newest first.
- **Headlines**: `haberturk_headlines` takes a section — `"gundem"` (default), `"ekonomi"`, `"dunya"`, `"spor"`, `"magazin"`, `"teknoloji"`, `"kultur-sanat"`, `"saglik"`, `"yasam"`, `"bilgi"`, `"htgastro"` — and returns ~50 headlines per section (title, section, URL).
- **Article**: `haberturk_get_article` takes a full haberturk.com URL and returns title, author, publish/modify dates, description, image, keywords, word count and the full body text (from the page's NewsArticle JSON-LD).
- **Search**: `haberturk_search_news` scans the news sitemap plus the breaking-news page and the gundem, ekonomi, dunya, spor and magazin listings by keyword — `"emekli"`, `"deprem"`, `"dolar"` — Turkish-aware (dotted/dotless I handled, so `"İSTANBUL"` matches `"İstanbul"`).
- **Sections**: `haberturk_list_sections` returns the sections usable with `haberturk_headlines`, with Turkish display names.
- Every response carries `fetched_at` (UTC) and `source: haberturk.com`.

## Install

```bash
uvx haberturk-mcp
```

Or add to your MCP client config (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "haberturk": {
      "command": "uvx",
      "args": ["haberturk-mcp"]
    }
  }
}
```

## Tools

| Tool | What it does |
| --- | --- |
| `haberturk_latest_news` | Latest news from the Google News sitemap (~600 items), newest first |
| `haberturk_breaking_news` | Latest breaking news (son dakika), newest first, with times |
| `haberturk_headlines` | Top headlines in one section |
| `haberturk_get_article` | Full text of one article (full URL) |
| `haberturk_search_news` | Keyword search over recent news |
| `haberturk_list_sections` | News sections usable with `haberturk_headlines` |
| `haberturk_health` | Is haberturk.com reachable right now? |

## Example

Latest news, 25 November 2026:

```json
{ "count": 2,
  "articles": [
    { "published": "2026-11-25T12:30:21+03:00", "section": "Kültür Sanat",
      "title": "İş Kültür’de Kasım ayının kitapları",
      "url": "https://www.haberturk.com/kultur-sanat/is-kulturde-kasim-ayinin-kitaplari-3929991" },
    { "published": "2026-11-25T12:22:24+03:00", "section": "Bilgi",
      "title": "Tv yayın akışı: 25 Kasım bugün TV’de neler var, hangi dizi ve film yayınlanacak",
      "url": "https://www.haberturk.com/bilgi/tv-yayin-akisi-25-kasim-bugun-tv-de-neler-var-hangi-dizi-ve-film-yayinlanacak-kanal-d-atv-show-tv-trt1-yayin-akisi-3929997" } ] }
```

An article, 25 November 2026:

```json
{ "title": "SON DAKİKA | 60 ilde 280 kişi yakalandı! Yeni nesil suç örgütlerine darbe",
  "author": "Habertürk",
  "date_published": "2026-11-25T11:33:28+03:00",
  "section": "Gündem", "word_count": 198,
  "keywords": ["suç örgütü operasyon", "yeni nesil suç örgütü"],
  "body": "İçişleri Bakanlığı ndan yapılan yazılı açıklamaya göre, İçişleri Bakanı Mustafa Çiftçi nin talimatları doğrultusunda …" }
```

## Caveats

- Search is a **scan of the news sitemap plus the breaking-news page and the main section listings**, not a full-archive search: the site's own search (`/arama/`) is disallowed in robots.txt and returns a shell page with no results, so there is no search API to call.
- Section pages have **no pagination** — each carries ~50 items, so `haberturk_headlines` sees the current page only.
- **Video** (`/video/`) pages are not text news and are excluded from listings; `haberturk_get_article` on them returns an error. Photo-news (`/foto/`) pages do carry full article text and are included.
- Article bodies come from the page's NewsArticle JSON-LD (`articleBody`, one plain-text block); if a page has no JSON-LD, the HTML paragraphs are used as a fallback. Note the site's own sanitizer strips apostrophes inside `articleBody` ("Bakanlığı ndan") — the text is otherwise complete.
- The BIST market pages (`/ekonomi/piyasa/...`) are client-side shells with no server-rendered prices and are not covered.
- `/teknoloji/` redirects to `/ekonomi/teknoloji`; `/egitim/` is 404 (not a section).
- Transport uses Chrome TLS impersonation; requests are spaced ~0.8s apart.

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # offline, recorded fixtures
.venv/bin/python -m pytest tests/test_live.py -v    # live, against www.haberturk.com
.venv/bin/python tests/smoke_live.py                # daily CI probe
```

## License

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — free for personal and non-commercial use; commercial use needs a separate license.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
