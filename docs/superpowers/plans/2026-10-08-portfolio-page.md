# Portfolio Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a responsive portfolio page that presents one horizontal and four vertical user-provided AI videos with inline playback.

**Architecture:** Add a semantic static `portfolio.html` page that reuses the existing site shell and adds a cinema-style portfolio grid. Store normalized video files and generated poster frames under `assets/portfolio/`; extend the shared stylesheet and script with page-scoped layout, category switching, cover activation, and single-player coordination.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python standard-library tests, FFmpeg/FFprobe, Playwright/Chromium

**Spec:** `docs/superpowers/specs/2026-10-08-portfolio-page-design.md`

## Global Constraints

- Keep the site dependency-free and compatible with GitHub Pages.
- Reuse the existing light-blue, white, premium visual system and three-pill navigation.
- Use only the five user-provided videos and frames extracted from them; do not fabricate work.
- Default to “AI 视频”; keep “电商设计图” as an honest empty-state category.
- Do not autoplay or preload full video files; use `preload="metadata"` and native controls.
- Preserve usable native video controls without JavaScript and honor reduced-motion preferences.
- Display the videos in this exact order: 耳机, 清洁布, 制冰盒, 收纳盒, 衣服.

## Review Focus

- A browser with JavaScript disabled must still expose native controls for all five videos; Task 1 asserts controls in markup and Task 3 verifies Chromium behavior.
- A failed or delayed poster image must not collapse the layout; Task 2 pins aspect-ratio containers and fallback backgrounds.
- Starting a second video must pause the first without rewinding it; Task 2 exercises the `play` listener behavior in Chromium.
- Switching to the empty design category while a video plays must pause playback and expose an honest status message; Task 2 tests both state changes.
- Mobile Safari/Chromium widths must not overflow despite native controls and long Chinese titles; Task 3 checks 390 px scroll width and card bounds.

---

### Task 1: Real Media Assets and Semantic Portfolio Markup

**Files:**
- Create: `portfolio.html`
- Create: `tests/test_portfolio.py`
- Create: `assets/portfolio/videos/headphones.mp4`
- Create: `assets/portfolio/videos/cleaning-cloth.mp4`
- Create: `assets/portfolio/videos/ice-tray.mp4`
- Create: `assets/portfolio/videos/storage-box.mp4`
- Create: `assets/portfolio/videos/outfit.mp4`
- Create: `assets/portfolio/posters/headphones.jpg`
- Create: `assets/portfolio/posters/cleaning-cloth.jpg`
- Create: `assets/portfolio/posters/ice-tray.jpg`
- Create: `assets/portfolio/posters/storage-box.jpg`
- Create: `assets/portfolio/posters/outfit.jpg`

**Interfaces:**
- Consumes: the five uploaded MP4 files under `/workspace/attachments/`, the shared site shell, and approved titles from the spec.
- Produces: stable category panels `design-projects` and `video-projects`; five `.portfolio-video` elements and `.portfolio-play` controls consumed by Task 2.

- [ ] **Step 1: Write failing structure and media tests**

Create `tests/test_portfolio.py` with parser-based tests asserting the six stable IDs `portfolio-intro`, `portfolio-categories`, `design-projects`, `video-projects`, `featured-video`, and `portrait-videos`; exactly three navigation pills with `portfolio.html` current; exactly five video elements with `controls`, `preload="metadata"`, no `autoplay`, unique poster paths, exact English MP4 paths, exact approved titles/order, and both category labels. Assert every referenced video and poster exists and is non-empty.

- [ ] **Step 2: Run tests and verify expected failure**

Run: `python3 -m unittest tests/test_portfolio.py -v`

Expected: FAIL because `portfolio.html` and normalized media assets do not exist.

- [ ] **Step 3: Normalize media paths and generate real posters**

Copy the uploaded videos without re-encoding into the exact English paths above. Use FFmpeg to extract representative JPEG frames: headphones near 2 seconds, cleaning cloth near 7 seconds, ice tray near 7 seconds, storage box near 7 seconds, and outfit near 2 seconds. Scale posters to a maximum width of 1280 px at web-appropriate JPEG quality while preserving aspect ratio.

- [ ] **Step 4: Implement semantic portfolio markup**

Create `portfolio.html` with the shared skip link, header, navigation, and footer. Add two real button tabs with `aria-controls`, `aria-selected`, and stable panel IDs. Render the featured headphones project first, then the four portrait projects in the approved order. Each card includes a native video with controls, poster, `playsinline`, accessible label, ratio, duration, title, and a progressively enhanced cover/play button.

- [ ] **Step 5: Verify source assets with FFprobe**

Run FFprobe over all five normalized MP4 files and assert: headphones is 1920×1080; cleaning cloth 480×854; ice tray 720×1280; storage box 480×854; outfit 480×854. Confirm all files have a video stream and durations within one second of the approved values.

- [ ] **Step 6: Run structure and full regression tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all homepage, resume, and portfolio structure tests PASS.

- [ ] **Step 7: Commit assets and semantic page**

Run: `git add portfolio.html assets/portfolio tests/test_portfolio.py && git commit -m "feat: add portfolio media and content"`

### Task 2: Cinema Layout, Categories, and Inline Playback

**Files:**
- Modify: `styles.css`
- Modify: `script.js`
- Modify: `tests/test_portfolio.py`

**Interfaces:**
- Consumes: Task 1 category panel IDs, `.portfolio-video`, `.portfolio-play`, and card structure.
- Produces: `activatePortfolioCategory(categoryName)` behavior through tab event listeners, inline cover activation, and one-active-video coordination.

- [ ] **Step 1: Add failing presentation and interaction tests**

Extend `tests/test_portfolio.py` to assert page-scoped cinema grid selectors, 16:9 and 9:16 aspect-ratio rules, four-column/two-column/one-column breakpoints, poster fallback background, tab selected/hidden state hooks, and reduced-motion support. Add script assertions for tab event listeners, `video.pause()`, `play` event coordination, and active-cover class handling.

- [ ] **Step 2: Run new tests and verify expected failure**

Run: `python3 -m unittest tests/test_portfolio.py -v`

Expected: presentation and interaction assertions FAIL because portfolio CSS and JavaScript are absent.

- [ ] **Step 3: Implement the B cinema showcase layout**

Append `.portfolio-page`-scoped styles to `styles.css`: decorative intro, icon tabs, a wide featured card, a four-column portrait grid, correct aspect-ratio media frames, real-poster presentation, play overlays, project metadata, honest empty state, hover/focus states, and layout fallbacks. At 960 px use two portrait columns; at 760 px use one column and mobile-safe padding.

- [ ] **Step 4: Implement progressive category and playback behavior**

Extend `script.js` defensively so non-portfolio pages are unchanged. Category buttons update `aria-selected`, `hidden`, and active classes; switching categories pauses every portfolio video. Clicking a cover reveals and plays its video. On any video `play` event, pause every other portfolio video and update the active card without resetting current time.

- [ ] **Step 5: Run all automated tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 6: Commit layout and behavior**

Run: `git add styles.css script.js tests/test_portfolio.py && git commit -m "feat: add portfolio playback experience"`

### Task 3: Browser, Performance, and Publication Verification

**Files:**
- No product files expected unless a failing browser check requires a tested correction

**Interfaces:**
- Consumes: completed portfolio page and media from Tasks 1 and 2.
- Produces: browser evidence, synchronized publishing branches, and the public portfolio URL.

- [ ] **Step 1: Run the final automated suite and whitespace check**

Run: `python3 -m unittest discover -s tests -v && git diff --check && git status --short`

Expected: all tests PASS, no whitespace errors, and no unintended files.

- [ ] **Step 2: Run desktop and mobile Chromium checks**

Serve the repository locally and load `/portfolio.html` at 1440×1000, 820×1000, and 390×844. Assert no horizontal overflow; five video cards have visible bounds; the featured card is 16:9 and portrait cards are approximately 9:16; AI 视频 is initially selected; 电商设计图 reveals the empty state; returning to AI 视频 restores the grid; and all source/poster requests return HTTP 200.

- [ ] **Step 3: Verify playback and progressive enhancement**

In Chromium, click two different covers and assert the second video plays while the first is paused and retains its current time. Switch category and assert all videos pause. Reload with JavaScript disabled and assert all five video elements and native controls remain visible and usable. Emulate reduced motion and confirm cards remain visible.

- [ ] **Step 4: Visually inspect full-page screenshots**

Capture desktop and mobile screenshots after all reveal items are visible. Check content density, title wrapping, native control fit, poster cropping, category states, card order, footer alignment, and consistency with the homepage/resume visual system.

- [ ] **Step 5: Push to both publishing branches**

Run: `git push origin HEAD:main && git push origin HEAD:gh-pages`

Expected: both remote branches advance to the same final commit.

- [ ] **Step 6: Verify remote source and public route**

Confirm `main` and `gh-pages` resolve to the final commit and raw GitHub serves `portfolio.html`, all five MP4 paths, and all five poster paths. Check `https://khyliegeorgiana-ux.github.io/liukaixuan/portfolio.html`; if the environment blocks `github.io`, report raw-branch and workflow evidence separately from public-route confirmation.
