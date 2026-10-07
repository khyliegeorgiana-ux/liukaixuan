# Resume Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a responsive, public resume page for 刘凯旋 that presents AI visual and video editing experience in a polished card layout.

**Architecture:** Create one semantic static page that reuses the site's existing navigation, footer, design tokens, and JavaScript behaviors. Add page-scoped resume components to the shared stylesheet and standard-library HTML/CSS regression tests to protect content, privacy, responsiveness, and navigation.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python standard-library tests, Playwright/Chromium smoke checks

**Spec:** `docs/superpowers/specs/2026-10-07-resume-page-design.md`

## Global Constraints

- Keep the site dependency-free and compatible with GitHub Pages.
- Use the existing white and low-saturation light-blue visual system.
- Position 刘凯旋 only as “AI 美工 / 视频剪辑师”; never use “平面设计”.
- Publish only `2119861292@qq.com`; omit phone, WeChat, gender, and age.
- Omit the complete 求职信息 section, including 求职意向、期望薪资、期望城市.
- Use an explicit replaceable portrait placeholder until the user supplies the original photo.
- Preserve readable content without JavaScript and honor reduced-motion preferences.

## Review Focus

- A direct visit to `resume.html#contact` must land on the email card; Task 1 asserts the stable ID and mail link.
- Privacy-sensitive source text must be absent from rendered markup; Task 1 checks every prohibited label and known phone number.
- The resume navigation must select 简历 without selecting 首页; Task 1 checks the exact `aria-current` placement.
- Long company names, dates, and certificate labels must wrap without horizontal overflow at 390 px; Task 2 checks computed page width in Chromium.
- Reveal effects must not hide resume content when JavaScript is unavailable or reduced motion is enabled; Task 2 checks shared hooks and browser-visible content.

---

### Task 1: Semantic Resume Content and Privacy

**Files:**
- Create: `resume.html`
- Create: `tests/test_resume.py`

**Interfaces:**
- Consumes: shared navigation/footer class names and `script.js` hooks from `index.html`.
- Produces: stable section IDs `resume-intro`, `strengths`, `education`, `credentials`, `experience`, and `contact`; component hooks prefixed `resume-` for Task 2.

- [ ] **Step 1: Write failing resume structure tests**

Create `tests/test_resume.py` with parser-based tests that assert the six section IDs; all approved headings, companies, dates, skills, certificates, and `mailto:2119861292@qq.com`; three navigation links; and `aria-current="page"` only on the 简历 link. Add negative assertions for `17839634123`, 电话, 微信, 男, 22岁, 求职信息, 求职意向, 期望薪资, 期望城市, and 平面设计. Assert a portrait placeholder with an accessible label and no fake personal photo URL.

- [ ] **Step 2: Run the resume tests and verify failure**

Run: `python3 -m unittest tests/test_resume.py -v`

Expected: FAIL because `resume.html` does not exist.

- [ ] **Step 3: Implement semantic resume markup**

Create `resume.html` using the approved copy from the spec. Reuse the header, three-pill navigation, skip link, footer, stylesheet, and script. Structure the identity, strengths, education, credentials, experience timeline, and email contact as semantic sections/articles; mark purely decorative elements `aria-hidden="true"`.

- [ ] **Step 4: Run structure and regression tests**

Run: `python3 -m unittest tests/test_resume.py tests/test_homepage.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit the semantic page**

Run: `git add resume.html tests/test_resume.py && git commit -m "feat: add semantic resume page"`

### Task 2: Resume Card System and Responsive Behavior

**Files:**
- Modify: `styles.css`
- Modify: `tests/test_resume.py`

**Interfaces:**
- Consumes: `resume-*` hooks and stable IDs from Task 1.
- Produces: desktop card grid, mobile single-column layout, portrait placeholder, timeline, credential tags, contact card, hover/focus states, and print-safe readable styling.

- [ ] **Step 1: Add failing presentation tests**

Extend `tests/test_resume.py` to assert a `.resume-page` scope, grid and timeline selectors, styled portrait placeholder, credential tag rules, `#contact` scroll offset, a mobile rule at `max-width: 760px`, and reduced-motion coverage inherited from the shared stylesheet.

- [ ] **Step 2: Run the presentation tests and verify failure**

Run: `python3 -m unittest tests/test_resume.py -v`

Expected: the new CSS assertions FAIL because resume styles are absent.

- [ ] **Step 3: Implement the resume visual system**

Append page-scoped rules to `styles.css`. Use a wide identity card, varied pale-blue surfaces, restrained grid/dot decorations, section numbering, a two-column education/credentials row, a vertical experience timeline, compact tags, and subtle hover lift. At 760 px and below, convert every resume grid to one column, allow metadata to wrap, reduce card padding, and keep tap targets at least 44 px high.

- [ ] **Step 4: Run all automated tests**

Run: `python3 -m unittest discover -s tests -v`

Expected: all homepage and resume tests PASS.

- [ ] **Step 5: Run desktop and mobile browser smoke checks**

Serve the repository with `python3 -m http.server 4173 --directory /workspace/liukaixuan`. In Chromium, load `/resume.html` at 1440×1000 and 390×844; assert `document.documentElement.scrollWidth === document.documentElement.clientWidth`, 简历 has the active pill background, the email link resolves to the approved `mailto:` address, `#contact` exists, and each required card has a visible bounding box. Capture screenshots for visual inspection, then stop only the server started for this check.

- [ ] **Step 6: Commit the finished resume styling**

Run: `git add styles.css tests/test_resume.py && git commit -m "feat: style responsive resume cards"`

### Task 3: Publication Verification

**Files:**
- No product files expected

**Interfaces:**
- Consumes: verified commits from Tasks 1 and 2.
- Produces: synchronized `main` and `gh-pages` remote branches and a checked public resume URL.

- [ ] **Step 1: Verify the final working tree and test suite**

Run: `git status --short && python3 -m unittest discover -s tests -v && git diff --check`

Expected: clean working tree, all tests PASS, and no whitespace errors.

- [ ] **Step 2: Push the reviewed commit to both publishing branches**

Run: `git push origin HEAD:main && git push origin HEAD:gh-pages`

Expected: both remote branches advance to the same final commit.

- [ ] **Step 3: Verify remote content and deployment status**

Run read-only Git checks to confirm `main` and `gh-pages` point to the final commit and that the raw `resume.html` contains the approved title and email. Inspect the GitHub Pages workflow result when available; distinguish a successful push from completed Pages publication.

- [ ] **Step 4: Verify the public route**

Check `https://khyliegeorgiana-ux.github.io/liukaixuan/resume.html` after deployment. Confirm the latest resume content is served; if the environment proxy blocks `github.io`, report the raw-branch and workflow evidence and give the exact public URL for user verification.
