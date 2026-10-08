from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortfolioParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.current_links = []
        self.text = []
        self.videos = []
        self.sources = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.links.append(attributes["href"])
            if attributes.get("aria-current") == "page":
                self.current_links.append(attributes["href"])
        if tag == "video":
            self.videos.append(attributes)
        if tag == "source":
            self.sources.append(attributes)

    def handle_data(self, data):
        self.text.append(data)


def parse_portfolio():
    source = (ROOT / "portfolio.html").read_text(encoding="utf-8")
    parser = PortfolioParser()
    parser.feed(source)
    return source, parser, " ".join(parser.text)


class PortfolioStructureTests(unittest.TestCase):
    def test_portfolio_has_required_sections(self):
        _, page, _ = parse_portfolio()
        required = {
            "portfolio-intro",
            "portfolio-categories",
            "design-projects",
            "video-projects",
            "featured-video",
            "portrait-videos",
        }
        self.assertTrue(required <= page.ids)

    def test_portfolio_uses_approved_navigation_state(self):
        source, page, _ = parse_portfolio()
        self.assertEqual(source.count('class="nav-pill"'), 3)
        self.assertTrue({"index.html", "resume.html", "portfolio.html"} <= set(page.links))
        self.assertEqual(page.current_links, ["portfolio.html"])

    def test_portfolio_has_approved_categories(self):
        source, _, text = parse_portfolio()
        self.assertIn("电商设计图", text)
        self.assertIn("AI 视频", text)
        self.assertIn('aria-controls="design-projects"', source)
        self.assertIn('aria-controls="video-projects"', source)
        self.assertIn('aria-selected="true"', source)
        self.assertIn("作品整理中", text)

    def test_portfolio_uses_eight_progressive_video_players(self):
        source, page, _ = parse_portfolio()
        self.assertEqual(len(page.videos), 8)
        self.assertEqual(len(page.sources), 8)
        for video in page.videos:
            self.assertIn("controls", video)
            self.assertEqual(video.get("preload"), "metadata")
            self.assertIn("playsinline", video)
            self.assertNotIn("autoplay", video)
            self.assertTrue(video.get("poster", "").startswith("assets/portfolio/posters/"))
        self.assertEqual(len({video["poster"] for video in page.videos}), 8)
        self.assertEqual(source.count('class="portfolio-play"'), 8)

    def test_portfolio_uses_approved_media_order_and_titles(self):
        _, page, text = parse_portfolio()
        expected_sources = [
            "assets/portfolio/videos/headphones.mp4",
            "assets/portfolio/videos/cleaning-cloth.mp4",
            "assets/portfolio/videos/windshield-cleaner.mp4",
            "assets/portfolio/videos/ice-tray.mp4",
            "assets/portfolio/videos/storage-box.mp4",
            "assets/portfolio/videos/storage-bag.mp4",
            "assets/portfolio/videos/fluffy-spray.mp4",
            "assets/portfolio/videos/outfit.mp4",
        ]
        self.assertEqual([item.get("src") for item in page.sources], expected_sources)
        titles = [
            "沉浸式耳机产品视觉",
            "汽车玻璃清洁布演示",
            "汽车挡风玻璃清洁器演示",
            "便携制冰盒产品短片",
            "帽子收纳盒场景展示",
            "真空收纳袋场景短片",
            "蓬松喷雾使用短片",
            "都市休闲穿搭短片",
        ]
        positions = [text.index(title) for title in titles]
        self.assertEqual(positions, sorted(positions))

    def test_referenced_media_assets_exist(self):
        _, page, _ = parse_portfolio()
        paths = [item["poster"] for item in page.videos]
        paths.extend(item["src"] for item in page.sources)
        for relative in paths:
            asset = ROOT / relative
            self.assertTrue(asset.is_file(), relative)
            self.assertGreater(asset.stat().st_size, 0, relative)


class PortfolioPresentationTests(unittest.TestCase):
    def test_portfolio_defines_cinema_layout_and_aspect_ratios(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".portfolio-page", css)
        self.assertIn(".portfolio-featured", css)
        self.assertIn(".portfolio-portrait-grid", css)
        landscape = re.search(r"\.portfolio-media-landscape\s*\{(?P<body>[^}]*)\}", css, re.S)
        portrait = re.search(r"\.portfolio-media-portrait\s*\{(?P<body>[^}]*)\}", css, re.S)
        self.assertIsNotNone(landscape)
        self.assertIsNotNone(portrait)
        self.assertIn("aspect-ratio: 16 / 9", landscape.group("body"))
        self.assertIn("aspect-ratio: 9 / 16", portrait.group("body"))

    def test_portfolio_media_has_poster_fallback(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        media = re.search(r"\.portfolio-media\s*\{(?P<body>[^}]*)\}", css, re.S)
        self.assertIsNotNone(media)
        self.assertIn("background:", media.group("body"))
        self.assertIn("overflow: hidden", media.group("body"))

    def test_portfolio_has_tablet_and_mobile_card_rules(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        tablet_start = css.index("@media (max-width: 960px)")
        mobile_start = css.index("@media (max-width: 760px)")
        tablet = css[tablet_start:mobile_start]
        mobile = css[mobile_start:css.index("@media (max-width: 480px)")]
        self.assertIn(".portfolio-portrait-card", tablet)
        self.assertRegex(tablet, r"flex-basis:\s*calc\(\(100%\s*-\s*18px\)\s*/\s*2\)")
        self.assertIn(".portfolio-portrait-card", mobile)
        self.assertRegex(mobile, r"flex-basis:\s*100%")

    def test_seven_portrait_cards_wrap_and_center_the_last_row(self):
        source, _, _ = parse_portfolio()
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        portrait_grid = re.search(r"\.portfolio-portrait-grid\s*\{(?P<body>[^}]*)\}", css, re.S)

        self.assertEqual(source.count('class="portfolio-card portfolio-portrait-card reveal"'), 7)
        self.assertIsNotNone(portrait_grid)
        self.assertIn("display: flex", portrait_grid.group("body"))
        self.assertIn("flex-wrap: wrap", portrait_grid.group("body"))
        self.assertIn("justify-content: center", portrait_grid.group("body"))

    def test_portfolio_styles_progressive_play_and_tab_states(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".js .portfolio-play", css)
        self.assertIn(".portfolio-card.is-playing", css)
        self.assertIn('.portfolio-tab[aria-selected="true"]', css)
        self.assertIn("prefers-reduced-motion: reduce", css)

    def test_hidden_video_panel_overrides_grid_display(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        hidden = re.search(r"\.portfolio-video-panel\[hidden\]\s*\{(?P<body>[^}]*)\}", css, re.S)
        self.assertIsNotNone(hidden)
        self.assertIn("display: none", hidden.group("body"))

    def test_play_button_has_unclipped_inner_focus_indicator(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        focus = re.search(r"\.js \.portfolio-play:focus-visible::before\s*\{(?P<body>[^}]*)\}", css, re.S)
        self.assertIsNotNone(focus)
        self.assertIn("box-shadow:", focus.group("body"))


class PortfolioInteractionTests(unittest.TestCase):
    def test_script_coordinates_categories_and_video_playback(self):
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("portfolioTabs", script)
        self.assertIn("portfolioVideos", script)
        self.assertIn("activatePortfolioCategory", script)
        self.assertIn("video.pause()", script)
        self.assertIn("addEventListener('play'", script)
        self.assertIn("classList.add('is-playing')", script)

    def test_script_activates_cover_buttons(self):
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertIn("portfolioPlayButtons", script)
        self.assertIn("button.closest('.portfolio-card')", script)
        self.assertIn("video.play()", script)


if __name__ == "__main__":
    unittest.main()
