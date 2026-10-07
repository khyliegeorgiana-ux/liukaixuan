from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ResumeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.current_links = []
        self.text = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if "aria-label" in attributes:
            self.labels.append(attributes["aria-label"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])
            if attributes.get("aria-current") == "page":
                self.current_links.append(attributes["href"])

    def handle_data(self, data):
        self.text.append(data)


def parse_resume():
    source = (ROOT / "resume.html").read_text(encoding="utf-8")
    parser = ResumeParser()
    parser.feed(source)
    return source, parser, " ".join(parser.text)


class ResumeStructureTests(unittest.TestCase):
    def test_resume_has_required_sections(self):
        _, page, _ = parse_resume()
        required = {"resume-intro", "strengths", "education", "credentials", "experience", "contact"}
        self.assertTrue(required <= page.ids)

    def test_resume_uses_approved_navigation_state(self):
        source, page, _ = parse_resume()
        self.assertTrue({"index.html", "resume.html", "portfolio.html"} <= set(page.links))
        self.assertEqual(page.current_links, ["resume.html"])
        self.assertEqual(source.count('class="nav-pill"'), 3)

    def test_resume_contains_approved_identity_and_summary(self):
        _, _, text = parse_resume()
        for phrase in (
            "刘凯旋",
            "AI 美工",
            "视频剪辑师",
            "专注 AI 视觉内容与短视频制作",
            "个人优势",
        ):
            self.assertIn(phrase, text)

    def test_resume_contains_education_and_experience(self):
        _, _, text = parse_resume()
        for phrase in (
            "焦作工贸职业学院",
            "计算机应用技术",
            "2022–2025",
            "深圳骏弘科技有限公司",
            "2026.02–至今",
            "深圳志会嘉科技有限公司",
            "2025.04–2026.02",
        ):
            self.assertIn(phrase, text)

    def test_resume_contains_approved_skills_and_credentials(self):
        _, _, text = parse_resume()
        for phrase in (
            "Stable Diffusion",
            "ComfyUI",
            "Photoshop",
            "剪映",
            "C1 驾驶证",
            "NIT 全国计算机应用水平证书",
            "普通话二级乙等",
            "计算机二级",
            "HCCDA-AI",
        ):
            self.assertIn(phrase, text)

    def test_resume_only_publishes_approved_contact_details(self):
        source, page, text = parse_resume()
        self.assertIn("mailto:2119861292@qq.com", page.links)
        self.assertIn("2119861292@qq.com", text)
        for prohibited in (
            "17839634123",
            "电话",
            "微信",
            "男｜22岁",
            "求职信息",
            "求职意向",
            "期望薪资",
            "期望城市",
            "平面设计",
        ):
            self.assertNotIn(prohibited, source)

    def test_portrait_is_an_accessible_placeholder(self):
        source, page, _ = parse_resume()
        self.assertIn('class="resume-portrait-placeholder"', source)
        self.assertIn("个人照片预留位置", page.labels)
        self.assertNotIn("<img", source)


class ResumePresentationTests(unittest.TestCase):
    def test_resume_defines_scoped_card_grid_and_timeline(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".resume-page", css)
        self.assertIn(".resume-grid", css)
        self.assertIn(".resume-card", css)
        self.assertIn(".resume-timeline", css)
        self.assertIn(".resume-timeline-item", css)

    def test_resume_styles_portrait_and_credential_tags(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".resume-portrait-placeholder", css)
        self.assertIn(".resume-credential-list", css)
        self.assertIn(".resume-credential-list li", css)

    def test_contact_anchor_accounts_for_sticky_navigation(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"#contact\s*\{[^}]*scroll-margin-top:")

    def test_resume_has_mobile_single_column_rules(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        mobile = re.search(r"@media\s*\(max-width:\s*760px\)\s*\{(?P<body>.*?)\n\}", css, re.S)
        self.assertIsNotNone(mobile)
        self.assertIn(".resume-grid", mobile.group("body"))
        self.assertIn("grid-template-columns: 1fr", mobile.group("body"))

    def test_resume_inherits_reduced_motion_support(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn(".js .reveal", css)


if __name__ == "__main__":
    unittest.main()
