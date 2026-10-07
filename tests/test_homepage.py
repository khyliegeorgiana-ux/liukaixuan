from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])

    def handle_data(self, data):
        self.text.append(data)


def parse_homepage():
    source = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    return source, parser, " ".join(parser.text)


class HomepageStructureTests(unittest.TestCase):
    def test_homepage_has_required_sections(self):
        _, page, _ = parse_homepage()
        self.assertTrue({"home", "capabilities", "featured-work", "collaboration"} <= page.ids)

    def test_navigation_targets_are_stable(self):
        _, page, _ = parse_homepage()
        self.assertTrue({"index.html", "about.html", "resume.html", "portfolio.html"} <= set(page.links))

    def test_copy_uses_approved_positioning(self):
        _, _, text = parse_homepage()
        self.assertIn("刘凯旋", text)
        self.assertIn("AI 美工", text)
        self.assertIn("视频剪辑", text)
        self.assertNotIn("平面设计", text)

    def test_contact_cta_targets_resume_contact(self):
        _, page, _ = parse_homepage()
        self.assertIn("resume.html#contact", page.links)


if __name__ == "__main__":
    unittest.main()
