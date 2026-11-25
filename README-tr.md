# haberturk-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/haberturk-mcp

**Habertürk** (www.haberturk.com) için resmi olmayan **salt okunur** MCP sunucusu — Türkiye'nin en büyük ulusal haber portallarından biri (Ciner Medya; Ekim 2026'da 24,4 milyon ziyaret, TR #40): Google News site haritasından **son haberler**, saatli **son dakika** haberleri, **kategoriye göre manşetler**, **tam metin haber**, **anahtar kelime araması** ve **kategori listesi**.

> "Turkey MCP factory" projesinin bir parçasıdır. Habertürk ile bağlantılı değildir. Veriler Habertürk'ün kendi sunucu taraflı sayfalarından gelir — giriş yok, API anahtarı yok, salt okunur.

## Yapay zekâ ajanları için

- **Son haberler**: `haberturk_latest_news`, Google News site haritasındaki (`/sitemap_google_news.xml`, yayın saatli ~600 öğe) en yeni haberleri döndürür, en yeniden eskiye.
- **Son dakika**: `haberturk_breaking_news`, `/son-dakika-haberleri/` sayfasındaki en yeni öğeleri döndürür (sayfada varsa HH:MM Avrupa/İstanbul saati, kategori, başlık, URL), en yeniden eskiye.
- **Manşetler**: `haberturk_headlines` bir kategori alır — `"gundem"` (varsayılan), `"ekonomi"`, `"dunya"`, `"spor"`, `"magazin"`, `"teknoloji"`, `"kultur-sanat"`, `"saglik"`, `"yasam"`, `"bilgi"`, `"htgastro"` — ve kategori başına ~50 manşet döndürür (başlık, kategori, URL).
- **Haber**: `haberturk_get_article`, tam bir haberturk.com URL'si alır ve başlık, yazar, yayın/güncelleme tarihleri, açıklama, görsel, anahtar kelimeler, kelime sayısı ve tam metni döndürür (sayfadaki NewsArticle JSON-LD verisinden).
- **Arama**: `haberturk_search_news`, haber site haritası ile son dakika sayfası ve gündem, ekonomi, dünya, spor, magazin listelerini anahtar kelimeyle tarar — `"emekli"`, `"deprem"`, `"dolar"` — Türkçe duyarlıdır (noktalı/noktasız I işlenir, yani `"İSTANBUL"` `"İstanbul"` ile eşleşir).
- **Kategoriler**: `haberturk_list_sections`, `haberturk_headlines` ile kullanılabilecek kategorileri Türkçe görünen adlarıyla döndürür.
- Her yanıt `fetched_at` (UTC) ve `source: haberturk.com` taşır.

## Kurulum

```bash
uvx haberturk-mcp
```

Veya MCP istemci yapılandırmanıza ekleyin (ör. Claude Desktop):

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

## Araçlar

| Araç | Ne yapar |
| --- | --- |
| `haberturk_latest_news` | Google News site haritasından son haberler (~600 öğe), en yeniden eskiye |
| `haberturk_breaking_news` | Son dakika haberleri, en yeniden eskiye, saatli |
| `haberturk_headlines` | Bir kategorideki öne çıkan manşetler |
| `haberturk_get_article` | Bir haberin tam metni (tam URL) |
| `haberturk_search_news` | Güncel haberlerde anahtar kelime araması |
| `haberturk_list_sections` | `haberturk_headlines` ile kullanılabilecek haber kategorileri |
| `haberturk_health` | haberturk.com şu anda erişilebilir mi? |

## Örnek

Son haberler, 25 Kasım 2026:

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

Bir haber, 25 Kasım 2026:

```json
{ "title": "SON DAKİKA | 60 ilde 280 kişi yakalandı! Yeni nesil suç örgütlerine darbe",
  "author": "Habertürk",
  "date_published": "2026-11-25T11:33:28+03:00",
  "section": "Gündem", "word_count": 198,
  "keywords": ["suç örgütü operasyon", "yeni nesil suç örgütü"],
  "body": "İçişleri Bakanlığı ndan yapılan yazılı açıklamaya göre, İçişleri Bakanı Mustafa Çiftçi nin talimatları doğrultusunda …" }
```

## Sınırlamalar

- Arama, **haber site haritası ile son dakika sayfası ve ana kategori listelerinin taranmasıdır**, tam arşiv araması değildir: sitenin kendi araması (`/arama/`) robots.txt'de engellidir ve sonuçsuz bir kabuk sayfa döndürür, dolayısıyla çağrılacak bir arama API'si yoktur.
- Kategori sayfalarında **sayfalama yoktur** — her biri ~50 öğe taşır, bu yüzden `haberturk_headlines` yalnızca güncel sayfayı görür.
- **Video** (`/video/`) sayfaları metin haber değildir ve listelerden çıkarılır; `haberturk_get_article` onlarda hata döndürür. Foto haber (`/foto/`) sayfaları tam metin taşır ve dahildir.
- Haber metinleri sayfadaki NewsArticle JSON-LD verisinden (`articleBody`, tek düz metin bloğu) gelir; JSON-LD yoksa HTML paragrafları yedek olarak kullanılır. Sitenin kendi temizleyicisinin `articleBody` içindeki kesme işaretlerini sildiğini unutmayın ("Bakanlığı ndan") — metin bunun dışında eksiksizdir.
- BIST piyasa sayfaları (`/ekonomi/piyasa/...`) istemci taraflı kabuklardır, sunucuda işlenmiş fiyat içermez ve kapsanmaz.
- `/teknoloji/`, `/ekonomi/teknoloji` adresine yönlenir; `/egitim/` 404'tür (kategori değildir).
- Aktarım Chrome TLS kimliğine bürünme kullanır; istekler ~0,8 sn arayla yapılır.

## Geliştirme

```bash
python -m venv .venv && .venv/bin/pip install -e . pytest
.venv/bin/python -m pytest tests/test_news.py -v    # çevrimdışı, kayıtlı örnekler
.venv/bin/python -m pytest tests/test_live.py -v    # canlı, www.haberturk.com karşısında
.venv/bin/python tests/smoke_live.py                # günlük CI yoklaması
```

## Lisans

[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) — kişisel ve ticari olmayan kullanım için ücretsizdir; ticari kullanım ayrı bir lisans gerektirir.

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
