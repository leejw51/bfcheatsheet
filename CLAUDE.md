# Project rules

## Hint button behavior (drill / type-to-learn pages)

The "hint" button on drill exercises is a toggle:

1. First click — reveal **all** still-unsolved blanks in the drill at once. For each, fill in the canonical answer (first variant of `data-answer`), mark `correct` / `solved` / `revealed="1"`, disable the input, and bump the global `solved` counter. Tag the drill with `data-hint-showing="1"` (which serializes to `dataset.hintShowing`). If every blank ends up solved, add the `solved` class and run section-completion logic.
2. Next click while `data-hint-showing="1"` — hide them again: for every blank with `data-revealed="1"`, clear the value, drop `correct` / `wrong` / `solved` / `revealed` flags, re-enable the input, and decrement the `solved` counter. Remove the drill's `solved` class and `data-hint-showing` flag. Leave user-typed correct answers untouched.
3. Streak resets to 0 whenever hint reveals answers.

This rule applies to all language variants of these pages (e.g. `basicai.html`, `korean/basicai.html`, and any future translations).

## Interactive HTML page pattern

Every interactive cheatsheet in this repo (`perceptron.html`, `basicai.html`, `transformers.html`, `softmax.html`, `cross-entropy.html`, `bert.html`, `tmux.html`, `git-worktree.html`, `rabbitmq.html`, etc.) is a single self-contained `.html` file — no build step, no external JS dependencies (KaTeX via CDN is fine). New pages must follow the same skeleton so styling, scoring, and keyboard nav stay consistent.

### File structure

1. `<head>` — `<meta charset>`, `<meta viewport>`, `<title>`. KaTeX CDN scripts only when math is used.
2. `<style>` — all CSS inline. Reuse the variable palette below verbatim; per-page accent colors override `--accent` / `--accent-2`.
3. `<body>` — sticky header, tab nav, `<main>` with one `<section class="tab-section">` per tab, `<canvas id="confetti-canvas">`, `<div class="toast">`, `#help-overlay`, `<footer>`, then a single `<script>` at the end.

### CSS variables (copy verbatim)

```css
:root {
  --bg: #0b1220;            --panel: #121a2b;       --panel-2: #182338;
  --border: #283449;        --text: #e6f1ff;        --muted: #8aa1bd;
  --accent: #22d3ee;        --accent-2: #38bdf8;    /* override per page */
  --code-bg: #08101e;
  --keyword: #ff7b72;       --string: #a5d6ff;      --number: #d2a8ff;
  --comment: #7d8fa6;       --fn: #d2a8ff;          --tag: #79c0ff;
  --good: #4ade80;          --bad: #f87171;         --warn: #fbbf24;
}
```

### Header / scoring (always present)

```html
<div class="sticky-top">
  <header>
    <div class="logo"><span class="spark">⚡</span> Title <span class="badge">Type to Learn</span></div>
    <div class="progress-bar-outer"><div class="progress-bar-inner" id="progressBar"></div></div>
    <div class="stat"><span class="num" id="scoreNum">0</span>/<span class="num" id="scoreTot">0</span><span class="lbl">solved</span></div>
    <div class="streak">🔥 <span class="num" id="streakNum">0</span></div>
    <button class="btn ghost tiny" onclick="showHelp()">?</button>
  </header>
  <nav class="tabs" id="tabs">
    <button class="active" data-tab="welcome">1. What is it?</button>
    <button data-tab="...">2. ...</button>
    <button data-tab="drills">N. Practice</button>
  </nav>
</div>
```

Counter math: `solved` increments on each newly-correct blank (`b.dataset.solved !== '1'` before, `'1'` after). `streak` resets to 0 on any wrong answer or any hint reveal. `progressBar` width = `solved / totalDrills * 100%`.

### Tab system

- One `<section class="tab-section" id="tab-{name}">` per tab; the active one carries `.active`.
- `<nav class="tabs">` buttons use `data-tab="{name}"` matching `id="tab-{name}"`.
- `switchTab(name)` toggles `.active` on tab buttons and sections; scrolls to top.
- Keyboard `1..N` switches tabs (skip when typing in an input). `?` opens help, `Esc` closes overlays.

### Drill anatomy

```html
<div class="drill" data-drill>
  <div class="prompt"><span class="num">1</span> Plain-English question.</div>
  <pre class="exercise">code with <input class="blank" data-answer="canonical|alt1|alt2" size="8" placeholder="?"> blanks</pre>
  <div class="controls">
    <button class="btn" onclick="checkDrill(this)">Check</button>
    <button class="btn ghost tiny" onclick="hintDrill(this)">Hint</button>
  </div>
  <div class="feedback"></div>
</div>
```

- `data-answer` is `|`-separated; the first variant is canonical (used by hint).
- Comparison is case-insensitive and strips surrounding `'` / `"`.
- Per-blank state: `dataset.solved`, `dataset.revealed`, classes `correct` / `wrong` (with `pop` and `shake` animations).
- Drill state: `.solved` class when every blank is solved; `dataset.hintShowing` while hint is on.
- Section state: when every drill in the active section is solved, fire `burstConfetti()`, `showToast(...)`, and append a `<span class="check">✓</span>` to the matching tab button.

### Required JS functions (drop-in)

`checkBlank(input)`, `checkDrill(btn)`, `hintDrill(btn)` (toggle per the rules at the top of this file), `randomGood()` / `randomBad()` (small message arrays for variety), `updateProgress()`, `checkSectionComplete()`, `showToast(msg)`, `sparkle(el)`, `burstConfetti()`, `copyCode(btn)`, `showHelp()` / `hideHelp()`. The perceptron page is the canonical reference — copy these wholesale and adjust the tab list and accent color.

### Keyboard contract

- `Tab` — natural focus traversal between blanks.
- `Enter` inside a `.blank` — runs the parent drill's primary `.btn` (Check).
- `1`..`N` outside any input — switch tabs.
- `?` — open `#help-overlay` (a fixed dimmed overlay with a `kbd` cheatsheet).
- `Esc` — close any overlay.

### Visual / motion conventions

- `.scanlines`, `.grain`, glow filters, and KaTeX are optional but encouraged.
- Confetti on section completion. `sparkle()` on each newly-solved drill. Toast notifications for milestones. Avoid blocking modals during the drill flow.
- Honor `@media (prefers-reduced-motion: reduce)` — animations should still teach the concept.

### "Type a sentence and watch X happen" sandboxes

Pages that include a live sandbox (user types into a textarea, page recomputes) should:

- Wrap the input in a `<div class="canvas-card">` with a heading and a quick legend.
- Recompute on `input` events, debounced if the work is non-trivial.
- Render output as DOM nodes (not innerHTML strings of user text — escape it) so colors, tooltips, and per-token hover all work.
- Show tensor shapes inline next to each stage as `pill`s — e.g. `[B=1, T=7] → [B=1, T=7, D=768]` — so users see the dimensions move.

### Registering a new page

After authoring `foo.html`, add a card to the `SHEETS` array in `index.html` with `id`, `href`, `title`, two-letter `glyph`, primary/secondary `color`, `desc`, `topics`, `tags` (subset of `ai` / `systems` / `cloud` / `languages`), and search `keywords`. Cards render automatically.
