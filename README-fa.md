# haberturk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/haberturk-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **هابرتورک** (www.haberturk.com) — یکی از بزرگ‌ترین پورتال‌های خبری ملی ترکیه (گروه رسانه‌ای جینر؛ ۲۴٫۴ میلیون بازدید در اکتبر ۲۰۲۶، رتبهٔ ۴۰ ترکیه): **آخرین اخبار** از نقشهٔ سایت Google News، **خبر فوری** (son dakika، با ساعت)، **تیترها بر اساس بخش**، **متن کامل خبر**، **جست‌وجوی کلیدواژه** و **فهرست بخش‌ها**.

> بخشی از «کارخانهٔ MCP ترکیه». وابسته به هابرتورک نیست. داده‌ها از صفحات رندرشدهٔ سمت سرور خود هابرتورک می‌آیند — بدون ورود، بدون کلید API، فقط‌خواندنی.

## برای ایجنت‌های هوش مصنوعی

- **آخرین اخبار**: `haberturk_latest_news` تازه‌ترین موارد را از نقشهٔ سایت Google News برمی‌گرداند (`/sitemap_google_news.xml`، حدود ۶۰۰ مورد با زمان انتشار)، از جدید به قدیم.
- **خبر فوری**: `haberturk_breaking_news` جدیدترین موارد صفحهٔ `/son-dakika-haberleri/` را برمی‌گرداند (در صورت وجود، ساعت HH:MM به وقت اروپا/استانبول، بخش، تیتر، نشانی)، از جدید به قدیم.
- **تیترها**: `haberturk_headlines` یک بخش می‌گیرد — `"gundem"` (پیش‌فرض)، `"ekonomi"`، `"dunya"`، `"spor"`، `"magazin"`، `"teknoloji"`، `"kultur-sanat"`، `"saglik"`، `"yasam"`، `"bilgi"`، `"htgastro"` — و حدود ۵۰ تیتر در هر بخش برمی‌گرداند (تیتر، بخش، نشانی).
- **خبر**: `haberturk_get_article` نشانی کامل یک خبر در haberturk.com را می‌گیرد و تیتر، نویسنده، تاریخ انتشار/ویرایش، توضیح، تصویر، کلیدواژه‌ها، تعداد کلمات و متن کامل را برمی‌گرداند (از بلوک NewsArticle JSON-LD صفحه).
- **جست‌وجو**: `haberturk_search_news` نقشهٔ خبرها، صفحهٔ خبر فوری و فهرست بخش‌های گوندم، اقتصاد، دنیا، ورزش و مجله را با کلیدواژه می‌کاود — `"emekli"`، `"deprem"`، `"dolar"` — با حساسیت به ترکی (I نقطه‌دار/بی‌نقطه درست مدیریت می‌شود، پس `"İSTANBUL"` با `"İstanbul"` مطابقت می‌کند).
- **بخش‌ها**: `haberturk_list_sections` بخش‌های قابل استفاده با `haberturk_headlines` را با نام‌های نمایشی ترکی برمی‌گرداند.
- هر پاسخ `fetched_at` (UTC) و `source: haberturk.com` دارد.

## نصب

```bash
uvx haberturk-mcp
```

یا به پیکربندی کلاینت MCP خود اضافه کنید (مثلاً Claude Desktop):

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

## ابزارها

| ابزار | چه می‌کند |
| --- | --- |
| `haberturk_latest_news` | آخرین اخبار از نقشهٔ سایت Google News (حدود ۶۰۰ مورد)، از جدید به قدیم |
| `haberturk_breaking_news` | آخرین خبرهای فوری (son dakika)، از جدید به قدیم، با ساعت |
| `haberturk_headlines` | تیترهای برتر یک بخش |
| `haberturk_get_article` | متن کامل یک خبر (نشانی کامل) |
| `haberturk_search_news` | جست‌وجوی کلیدواژه در اخبار اخیر |
| `haberturk_list_sections` | بخش‌های خبری قابل استفاده با `haberturk_headlines` |
| `haberturk_health` | آیا haberturk.com در حال حاضر در دسترس است؟ |

## نمونه

آخرین اخبار، ۲۵ نوامبر ۲۰۲۶:

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

یک خبر، ۲۵ نوامبر ۲۰۲۶:

```json
{ "title": "SON DAKİKA | 60 ilde 280 kişi yakalandı! Yeni nesil suç örgütlerine darbe",
  "author": "Habertürk",
  "date_published": "2026-11-25T11:33:28+03:00",
  "section": "Gündem", "word_count": 198,
  "keywords": ["suç örgütü operasyon", "yeni nesil suç örgütü"],
  "body": "İçişleri Bakanlığı ndan yapılan yazılı açıklamaya göre, İçişleri Bakanı Mustafa Çiftçi nin talimatları doğrultusunda …" }
```

## محدودیت‌ها

- جست‌وجو **کاوش نقشهٔ خبرها، صفحهٔ خبر فوری و فهرست بخش‌های اصلی** است، نه جست‌وجوی کامل آرشیو: جست‌وجوی خود سایت (`/arama/`) در robots.txt ممنوع است و صفحه‌ای خالی و بدون نتیجه برمی‌گرداند، پس API جست‌وجویی برای فراخوانی وجود ندارد.
- صفحات بخش **صفحه‌بندی ندارند** — هر کدام حدود ۵۰ مورد دارند، پس `haberturk_headlines` فقط صفحهٔ جاری را می‌بیند.
- صفحات **ویدئو** (`/video/`) خبر متنی نیستند و از فهرست‌ها حذف می‌شوند؛ `haberturk_get_article` روی آن‌ها خطا برمی‌گرداند. صفحات خبر تصویری (`/foto/`) متن کامل دارند و شامل می‌شوند.
- متن خبرها از بلوک NewsArticle JSON-LD صفحه می‌آید (`articleBody`، یک بلوک متن ساده)؛ اگر JSON-LD نباشد، پاراگراف‌های HTML به‌عنوان جایگزین استفاده می‌شوند. توجه کنید که پاک‌کنندهٔ خود سایت آپاستروف‌ها را از داخل `articleBody` حذف می‌کند («Bakanlığı ndan») — متن در غیر این صورت کامل است.
- صفحات بازار بورس (`/ekonomi/piyasa/...`) پوسته‌های سمت کاربرند، قیمت رندرشدهٔ سمت سرور ندارند و پوشش داده نمی‌شوند.
- `/teknoloji/` به `/ekonomi/teknoloji` هدایت می‌شود؛ `/egitim/` خطای 404 می‌دهد (بخش نیست).
- انتقال از جعل هویت TLS کروم استفاده می‌کند؛ درخواست‌ها با فاصلهٔ حدود ۰٫۸ ثانیه ارسال می‌شوند.

## توسعه

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # آفلاین، فیکسچرهای ضبط‌شده
.venv/bin/python -m pytest tests/test_live.py -v    # زنده، در برابر www.haberturk.com
.venv/bin/python tests/smoke_live.py                # بررسی روزانهٔ CI
```

## مجوز

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — برای استفادهٔ شخصی و غیرتجاری رایگان است؛ استفادهٔ تجاری به مجوز جداگانه نیاز دارد.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
