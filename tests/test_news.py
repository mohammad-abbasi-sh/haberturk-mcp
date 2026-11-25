"""Offline tests for haberturk_mcp.news — recorded real haberturk.com pages.

Fixtures are real pages fetched 2026-11-25 (plain curl, browser UA):
- homepage.html: / (108 deduped article links; video links excluded).
- category-gundem.html: /gundem/ (51 articles, data-newsname cards).
- sondakika.html: /son-dakika-haberleri/ (52 breaking items, 16
  with a time span).
- sitemap-google-news.xml: /sitemap_google_news.xml (593 items,
  newest 2026-11-25T12:30:21+03:00, oldest 2026-11-23T10:18:59+03:00).
- article.html: "60 ilde 280 kişi yakalandı" 3929975 (Habertürk,
  published 2026-11-25T11:33:28+03:00, 198 words).
- article-kultur.html: "İş Kültür'de Kasım ayının kitapları"
  3929991 (Habertürk, 2264 words).
"""
import os
import unittest

from haberturk_mcp import news as N

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name: str) -> str:
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class TestListingParse(unittest.TestCase):
    def test_gundem(self):
        rows = N.parse_listing(_read("category-gundem.html"))
        self.assertEqual(len(rows), 51)
        first = rows[0]
        self.assertEqual(
            first["title"],
            "Bir ay önce evlendi... 5. kattan düşerek öldü! Flaş gelişme",
        )
        self.assertTrue(first["url"].endswith("-3929951"))
        self.assertEqual(first["section"], "Gündem")

    def test_homepage(self):
        rows = N.parse_listing(_read("homepage.html"))
        self.assertEqual(len(rows), 108)
        self.assertEqual(rows[0]["title"], "Diploması resmen iptal edildi")
        self.assertTrue(rows[0]["url"].endswith("-3929957"))

    def test_no_video(self):
        for name in ("category-gundem.html", "homepage.html",
                     "sondakika.html"):
            for r in N.parse_listing(_read(name)):
                self.assertNotIn("/video/", r["url"])

    def test_all_have_url_title(self):
        for name in ("category-gundem.html", "homepage.html"):
            for r in N.parse_listing(_read(name)):
                self.assertIn("haberturk.com", r["url"])
                self.assertTrue(r["title"])


class TestSondakikaParse(unittest.TestCase):
    def test_count_and_order(self):
        rows = N.parse_sondakika(_read("sondakika.html"))
        self.assertEqual(len(rows), 52)
        first = rows[0]
        self.assertEqual(
            first["title"], "Yılın son MGK'sı Beştepe'de toplanacak")
        self.assertEqual(first["section"], "Gündem")
        self.assertTrue(first["url"].endswith("-3929992"))

    def test_times(self):
        rows = N.parse_sondakika(_read("sondakika.html"))
        timed = [r for r in rows if "time" in r]
        self.assertEqual(len(timed), 16)
        for r in timed:
            self.assertRegex(r["time"], r"^\d{2}:\d{2}$")
        self.assertEqual(timed[0]["time"], "11:47")


class TestSitemapParse(unittest.TestCase):
    def test_count_and_order(self):
        rows = N.parse_sitemap_news(_read("sitemap-google-news.xml"))
        self.assertEqual(len(rows), 593)
        self.assertEqual(
            rows[0]["title"], "İş Kültür’de Kasım ayının kitapları")
        self.assertEqual(rows[0]["published"], "2026-11-25T12:30:21+03:00")
        self.assertEqual(rows[0]["section"], "Kültür Sanat")
        self.assertEqual(
            rows[-1]["published"], "2026-11-23T10:18:59+03:00")

    def test_sections(self):
        rows = N.parse_sitemap_news(_read("sitemap-google-news.xml"))
        sections = {r.get("section", "") for r in rows}
        for s in ("Gündem", "Ekonomi", "Dünya", "Spor", "Magazin"):
            self.assertIn(s, sections)


class TestArticleParse(unittest.TestCase):
    def setUp(self):
        self.a = N.parse_article(_read("article.html"))

    def test_core(self):
        self.assertEqual(
            self.a["title"],
            "SON DAKİKA | 60 ilde 280 kişi yakalandı! Yeni nesil suç "
            "örgütlerine darbe",
        )
        self.assertEqual(self.a["author"], "Habertürk")
        self.assertEqual(self.a["date_published"], "2026-11-25T11:33:28+03:00")
        self.assertEqual(self.a["date_modified"], "2026-11-25T11:53:41+03:00")
        self.assertEqual(self.a["section"], "Gündem")
        self.assertEqual(self.a["word_count"], 198)

    def test_body(self):
        self.assertEqual(len(self.a["body"]), 1735)
        self.assertIn("280 şüpheli yakalandı", self.a["body"])

    def test_keywords_and_image(self):
        self.assertIn("suç örgütü operasyon", self.a["keywords"])
        self.assertTrue(
            self.a["image"].startswith("https://im.haberturk.com/"))
        self.assertTrue(self.a["url"].endswith("-3929975"))

    def test_kultur_article(self):
        b = N.parse_article(_read("article-kultur.html"))
        self.assertEqual(b["title"], "İş Kültür’de Kasım ayının kitapları")
        self.assertEqual(b["author"], "Habertürk")
        self.assertEqual(b["section"], "Kültür-Sanat")
        self.assertEqual(b["word_count"], 2264)
        self.assertEqual(len(b["body"]), 17564)

    def test_no_body(self):
        with self.assertRaises(ValueError):
            N.parse_article("<html><body>no article here</body></html>")


class TestTrHelpers(unittest.TestCase):
    def test_tr_lower(self):
        self.assertEqual(N.tr_lower("İstanbul"), "istanbul")
        self.assertEqual(N.tr_lower("IĞDIR"), "ığdır")
        self.assertEqual(N.tr_lower("Şoför"), "şoför")

    def test_tr_title(self):
        self.assertEqual(N.tr_title("AKTÜALİTE"), "Aktüalite")
        self.assertEqual(N.tr_title("EKONOMİ"), "Ekonomi")
        self.assertEqual(N.tr_title("GÜNDEM"), "Gündem")


if __name__ == "__main__":
    unittest.main()
