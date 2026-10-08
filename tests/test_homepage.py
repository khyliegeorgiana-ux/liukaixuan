from html.parser import HTMLParser
from pathlib import Path
import re
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


def contrast_ratio(first, second):
    def luminance(value):
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        channels = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def css_variable(css, name):
    match = re.search(rf"{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})", css)
    if not match:
        raise AssertionError(f"Missing CSS variable {name}")
    return match.group(1)


class HomepageStructureTests(unittest.TestCase):
    def test_homepage_has_required_sections(self):
        _, page, _ = parse_homepage()
        self.assertTrue({"home", "capabilities", "featured-work", "collaboration"} <= page.ids)

    def test_navigation_targets_are_stable(self):
        _, page, _ = parse_homepage()
        self.assertTrue({"index.html", "resume.html", "portfolio.html"} <= set(page.links))

    def test_navigation_has_three_pill_links(self):
        source, page, text = parse_homepage()
        self.assertNotIn("about.html", page.links)
        self.assertNotIn("关于我", text)
        self.assertEqual(source.count('class="nav-pill"'), 3)
        self.assertIn('class="nav-pill" href="index.html" aria-current="page"', source)

    def test_copy_uses_approved_positioning(self):
        _, _, text = parse_homepage()
        self.assertIn("刘凯旋", text)
        self.assertIn("AI 美工", text)
        self.assertIn("视频剪辑", text)
        self.assertNotIn("平面设计", text)

    def test_contact_cta_targets_resume_contact(self):
        _, page, _ = parse_homepage()
        self.assertIn("resume.html#contact", page.links)

    def test_hero_uses_resume_portfolio_title(self):
        source, _, text = parse_homepage()
        self.assertIn("刘凯旋的", text)
        self.assertIn("个人简历以及作品集", text)
        self.assertNotIn("你好，我是", text)
        self.assertIn('src="assets/kx-glass-monogram.png"', source)
        self.assertIn('alt="玻璃金属质感的 KX 个人标识"', source)

    def test_hero_omits_summary_modules(self):
        source, _, text = parse_homepage()
        self.assertNotIn('class="hero-stats"', source)
        for label in ("专注领域", "创作能力", "合作状态", "开放新机会"):
            self.assertNotIn(label, text)


class HomepagePresentationTests(unittest.TestCase):
    def test_assets_are_linked(self):
        source, _, _ = parse_homepage()
        self.assertIn('href="styles.css"', source)
        self.assertIn('src="script.js"', source)

    def test_styles_define_palette_and_responsive_rules(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("--color-blue", css)
        self.assertIn("--color-surface", css)
        self.assertRegex(css, r"@media\s*\([^)]*max-width:\s*760px")

    def test_page_prevents_mobile_overflow(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"overflow-x:\s*(?:hidden|clip)")

    def test_reduced_motion_is_supported(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion: reduce", css)

    def test_content_remains_visible_without_javascript(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn(".js .reveal", css)
        self.assertIn("document.documentElement.classList.add('js')", script)

    def test_mobile_navigation_remains_visible_without_javascript(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".js .nav-links {", css)
        self.assertIn(".js .menu-toggle {", css)

    def test_small_text_palette_meets_wcag_aa_contrast(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        surface = css_variable(css, "--color-surface")
        for name in ("--color-blue-strong", "--color-label"):
            self.assertGreaterEqual(contrast_ratio(css_variable(css, name), surface), 4.5)
        self.assertGreaterEqual(contrast_ratio(css_variable(css, "--color-blue-hover"), "#ffffff"), 4.5)

    def test_homepage_uses_numbered_modules_and_bento_grid(self):
        source, _, _ = parse_homepage()
        self.assertGreaterEqual(source.count('class="section-number"'), 3)
        self.assertIn('class="bento-grid', source)
        self.assertIn('class="bento-card bento-card-featured', source)

    def test_featured_work_uses_real_project_posters(self):
        source, _, text = parse_homepage()
        expected_projects = {
            "assets/portfolio/posters/headphones.jpg": "沉浸式耳机产品视觉",
            "assets/portfolio/posters/cleaning-cloth.jpg": "汽车玻璃清洁布演示",
            "assets/portfolio/posters/outfit.jpg": "都市休闲穿搭短片",
        }

        for poster, title in expected_projects.items():
            self.assertIn(f'src="{poster}"', source)
            self.assertIn(title, text)
        self.assertNotIn("即将上线", text)

    def test_featured_work_uses_two_portraits_above_one_landscape(self):
        source, _, _ = parse_homepage()
        cleaning = source.index("cleaning-cloth.jpg")
        outfit = source.index("outfit.jpg")
        headphones = source.index("headphones.jpg")
        css = (ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertLess(cleaning, outfit)
        self.assertLess(outfit, headphones)
        self.assertEqual(source.count('class="bento-card work-card work-card-portrait'), 2)
        self.assertIn('class="bento-card bento-card-featured work-card work-card-landscape', source)
        self.assertRegex(css, r"\.work-card-portrait\s+\.work-art\s*\{[^}]*aspect-ratio:\s*9\s*/\s*16")
        self.assertRegex(css, r"\.work-card-landscape\s+\.work-art\s*\{[^}]*aspect-ratio:\s*16\s*/\s*9")

    def test_hero_uses_layered_glass_visual(self):
        source, _, _ = parse_homepage()
        self.assertIn('class="glass-stage', source)
        self.assertGreaterEqual(source.count('class="glass-orbit'), 2)
        self.assertIn('class="hero-image-frame', source)
        self.assertIn('class="monogram-art', source)

    def test_palette_has_visible_blue_accents(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("--color-blue-vivid", css)
        self.assertIn("--gradient-hero", css)
        self.assertIn("var(--color-blue-vivid)", css)

    def test_mobile_menu_has_accessible_state(self):
        source, _, _ = parse_homepage()
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn('class="menu-toggle"', source)
        self.assertIn('class="nav-links"', source)
        self.assertIn("aria-expanded", script)
        self.assertIn("Escape", script)

    def test_navigation_pills_define_active_and_hover_states(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".nav-pill {", css)
        self.assertIn('.nav-pill[aria-current="page"]', css)
        self.assertIn(".nav-pill:hover", css)


if __name__ == "__main__":
    unittest.main()
