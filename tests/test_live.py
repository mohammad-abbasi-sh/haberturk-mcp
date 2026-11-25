"""Live tests for haberturk_mcp — real requests to haberturk.com.

Requires network + Chrome TLS impersonation (curl-cffi). The server
is polite by design (~0.8s between requests), so this file takes
~30s. Run: python -m pytest tests/test_live.py -v

Headlines change during the day; tests assert structure and sane
ranges, not exact titles.
"""
import unittest

from haberturk_mcp import http as H
from haberturk_mcp import news as N


class TestLiveSitemap(unittest.TestCase):
    def test_latest(self):
        xml_text = H.fetch_sitemap_news_xml()
        rows = N.parse_sitemap_news(xml_text)
        self.assertGreater(len(rows), 100)
        self.assertIn("haberturk.com", rows[0]["url"])
        self.assertTrue(rows[0]["title"])
        self.assertTrue(rows[0]["published"])


class TestLiveHeadlines(unittest.TestCase):
    def test_gundem(self):
        html_text = H.fetch_category_html("gundem")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 20)
        self.assertIn("haberturk.com", rows[0]["url"])

    def test_ekonomi(self):
        html_text = H.fetch_category_html("ekonomi")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 20)

    def test_dunya(self):
        html_text = H.fetch_category_html("dunya")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 10)

    def test_spor(self):
        html_text = H.fetch_category_html("spor")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 10)

    def test_teknoloji(self):
        # /teknoloji/ 301-redirects to /ekonomi/teknoloji
        html_text = H.fetch_category_html("teknoloji")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 5)

    def test_unknown_category_404(self):
        with self.assertRaises(H.HaberturkError):
            H.fetch_category_html("xyzabcqwerty")


class TestLiveLatest(unittest.TestCase):
    def test_sondakika(self):
        html_text = H.fetch_sondakika_html()
        rows = N.parse_sondakika(html_text)
        self.assertGreater(len(rows), 10)
        self.assertTrue(rows[0]["title"])
        timed = [r for r in rows if "time" in r]
        self.assertGreater(len(timed), 0)
        self.assertRegex(timed[0]["time"], r"^\d{2}:\d{2}$")


class TestLiveArticle(unittest.TestCase):
    def test_son_dakika_story(self):
        html_text = H.fetch_article_html(
            "https://www.haberturk.com/gundem/son-dakika-60-ilde-280-kisi-"
            "yakalandi-yeni-nesil-suc-orgutlerine-darbe-3929975"
        )
        a = N.parse_article(html_text)
        self.assertEqual(
            a["title"],
            "SON DAKİKA | 60 ilde 280 kişi yakalandı! Yeni nesil suç "
            "örgütlerine darbe",
        )
        self.assertEqual(a["author"], "Habertürk")
        self.assertGreater(a["word_count"], 100)

    def test_unknown_article_404(self):
        with self.assertRaises(H.HaberturkError):
            H.fetch_article_html(
                "https://www.haberturk.com/gundem/boyle-bir-haber-yok-0000000"
            )


class TestLiveHealth(unittest.TestCase):
    def test_health_ok(self):
        result = H.health_check()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["http_status"], 200)


if __name__ == "__main__":
    unittest.main()
