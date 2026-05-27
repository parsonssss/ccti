---
name: ccti
description: Generate a CCTI (Claude Code Type Indicator) personality test result card for the user, based on observed behavior in the current conversation. Use this skill whenever the user asks for "CCTI", "Claude Code 人格测试", "测一下我", "看看我是哪种 Claude Code 用户", "我的 Claude Code 风格", "vibe coding 人格", or any related personality / archetype / score analysis of their AI-collaboration style. Also use it proactively when the user wants a shareable card / image summarizing their AI-pairing behavior. The output is a 1080×1420 PNG card auto-opened in the default image viewer.
---

# CCTI · Claude Code Type Indicator

A 16-type personality system that classifies how a user collaborates with Claude
Code, based purely on observable behavior in this conversation. Produces a
visually polished, shareable PNG card with the user's archetype, 8 academic
dimension scores, and 8 signature-move stats.

CCTI deliberately mirrors **MBTI** / **SBTI** branding (4-letter, `_TI` suffix).
The vibe is "accurate enough to make the user say *卧槽这就是我*", not academic
rigor.

---

## When to run

Trigger on phrases like:
- "测一下我", "我是哪种 Claude Code 用户", "我的 CCTI 是什么"
- "Claude Code 人格测试", "vibe coding 人格"
- "出张分享图 / 测试卡 / 人格卡"
- Any open-ended "评价一下我用 Claude 的方式"

Don't trigger on:
- Unrelated personality tests (MBTI, 五行 etc.) — those are different products
- Generic project work, even if the conversation has been long

---

## Workflow

Five steps. Do not skip any — the order matters.

### 1. Analyze the user's behavior

Read `references/scoring_rubric.md` for the full scoring rules. You're scoring
the **user's** messages, not Claude's.

Output of this step (kept in memory, not written to disk yet):
- **4-axis code** — one of `F`/`I`, `T`/`V`, `S`/`M`, `P`/`R` per axis → 4-letter
  archetype code (e.g. `ITSR`).
- **8 dimension scores** — 0.0 to 10.0 with one decimal, for `task_clarity`,
  `product_thinking`, `diagnostics`, `technical_decisions`,
  `iteration_cadence`, `agent_collaboration`, `context_provision`,
  `engineering_discipline`.
- **Tier** — derived from mean of 8 dimensions: ≥8.5 → `S+`, 8.0–8.5 → `S`,
  7.0–8.0 → `A`, 6.0–7.0 → `B`, <6.0 → `C`.

If the conversation is too short (<5 user messages) for a meaningful read, say
so and stop. Don't fabricate.

### 2. Pick archetype card content

Open `assets/archetypes.json`. Find the entry under
`archetypes.<your-4-letter-code>` — it has:
- `name_cn` (2-3 char Chinese name, e.g. 主谋)
- `name_en` (English, e.g. THE MASTERMIND)
- `tier` (baseline — you may **override with the tier computed in step 1** when
  it differs noticeably)
- `slogan` (top quote, e.g. 不写代码,只写决定)
- `explanation` (4-line description — may contain `<strong>` tags for green
  emphasis)
- `accent_lines` (4 short command strings shown in the SVG, e.g. `$ 下一个 →`)

### 3. Pick 8 signature-move stats

The rubric calls these **刻画级**. Use `signature_stat_templates` in
archetypes.json — each template has a value driven by one of the 4 axes. Pick
the value matching your computed axis letters.

You're allowed to:
- **Tweak any single number by ±20%** to better match what you actually saw
  this user do (e.g., prompt 长度 13 字 → 11 字 if their median is shorter).
- **Swap one or two stats** for a more user-specific one if a template's stat
  feels off. Stay in SBTI tone — short, slightly absurd, immediately
  recognizable. Avoid stats that need precise measurement to be plausible.

### 4. Render the card

Fill `assets/template.html`. Placeholders (use Python `str.replace`, not Jinja):

| Placeholder | Source |
|---|---|
| `{{SLOGAN}}` | archetype `slogan` |
| `{{NAME_CN_HEAD}}` | first character of `name_cn` (e.g. 主 in 主谋) |
| `{{NAME_CN_TAIL}}` | the rest, accented green (e.g. 谋) |
| `{{NAME_CN_FULL}}` | full `name_cn` |
| `{{NAME_EN}}` | archetype `name_en` |
| `{{TAGLINE}}` | archetype `tagline` (one-line behavioral picture, e.g. "「下一个」是你的语气词") |
| `{{CODE}}` | the 4-letter archetype code itself (e.g. `ITSR`, `FTSR`) — shown as a small outline badge next to the tier |
| `{{TIER}}` | computed tier (`S+` / `S` / `A` / `B` / `C`) |
| `{{EXPLANATION}}` | archetype `explanation` (already contains `<strong>` if any) |
| `{{D1_SCORE}}` ... `{{D8_SCORE}}` | dimension scores (e.g. `9.2`), in order: task_clarity, product_thinking, diagnostics, technical_decisions, iteration_cadence, agent_collaboration, context_provision, engineering_discipline |
| `{{D1_PCT}}` ... `{{D8_PCT}}` | same scores × 10 (the bar widths in percent — e.g. `92` for 9.2) |
| `{{S1_VALUE}}` ... `{{S8_VALUE}}` | signature stat values |
| `{{S1_LABEL}}` ... `{{S8_LABEL}}` | signature stat labels (`\n` as literal `\n` → renders as line break via `<br>` doesn't apply here, use `<br>` substitution — see below) |
| `{{SVG_SCENE}}` | archetype `svg_scene` — full SVG fragment for the right-side illustration (motif unique to each type: magnifying glass for Inspector, fire+PUSH for Yolo, hammer+anvil for Smith, etc.) |
| `{{YEAR}}` | current year, four digits |

**Note on `\n` in stat labels:** if a label has `\n`, replace it with `<br>`
before substitution, because the template's `.stat-label` renders HTML.

**Note on green-accent split:** for `name_cn`, the template renders the first
character white and the rest in green. If `name_cn` is only 1 char (rare),
put it in `{{NAME_CN_HEAD}}` and leave `{{NAME_CN_TAIL}}` empty.

**Where to write:** save the filled HTML to `~/.claude/skills/ccti/output/`
(create it if missing) with a name like `ccti-<archetype>-<timestamp>.html`.
**Don't** modify `assets/template.html` itself.

### 5. Render + open

Run the bundled scripts. They handle macOS / Windows / Linux automatically by
detecting Chrome / Chromium / Edge / Brave install paths.

```bash
python3 ~/.claude/skills/ccti/scripts/render.py \
  <filled-html-path> \
  <output-png-path>

python3 ~/.claude/skills/ccti/scripts/open_image.py \
  <output-png-path>
```

If `render.py` exits non-zero, surface the message — likely no Chromium-family
browser is installed. Don't pretend it worked.

After both scripts succeed, send a short message to the user:
1. Confirm the archetype name + tier
2. Mention where the PNG was saved
3. Optionally: 1-line interpretation of the most distinctive trait you scored

Keep this confirmation under 4 lines. The card itself is the deliverable.

---

## Output directory convention

```
~/.claude/skills/ccti/output/
  ccti-ITSR-2026-05-27-1734.html
  ccti-ITSR-2026-05-27-1734.png
```

Both HTML and PNG live there. HTML is kept so users can re-render manually
(e.g., resize, tweak copy) without re-running the skill.

---

## Honest limits

- This is calibrated for **Chinese-speaking users on Claude Code**. The
  archetype names and copy are in Chinese.
- The "16-type" framing is decorative — not a validated psychometric instrument.
  Tell the user this if they ask.
- The 8 dimension scores reflect Claude's observation of the current
  conversation only. They are *not* a measure of the user's overall engineering
  skill.

---

## Files in this skill

- `SKILL.md` — this file
- `assets/archetypes.json` — 16 archetype definitions + stat templates +
  dimension keys
- `assets/template.html` — visual template with placeholders
- `references/scoring_rubric.md` — full scoring rules per axis and per dimension
- `scripts/render.py` — cross-platform HTML→PNG renderer (Chrome/Chromium/Edge/Brave)
- `scripts/open_image.py` — cross-platform image opener
