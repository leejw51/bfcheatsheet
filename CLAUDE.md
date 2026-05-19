# Project rules

## Hint button behavior (drill / type-to-learn pages)

The "hint" button on drill exercises is a toggle:

1. First click — reveal **all** still-unsolved blanks in the drill at once. For each, fill in the canonical answer (first variant of `data-answer`), mark `correct` / `solved` / `revealed="1"`, disable the input, and bump the global `solved` counter. Tag the drill with `data-hint-showing="1"` (which serializes to `dataset.hintShowing`). If every blank ends up solved, add the `solved` class and run section-completion logic.
2. Next click while `data-hint-showing="1"` — hide them again: for every blank with `data-revealed="1"`, clear the value, drop `correct` / `wrong` / `solved` / `revealed` flags, re-enable the input, and decrement the `solved` counter. Remove the drill's `solved` class and `data-hint-showing` flag. Leave user-typed correct answers untouched.
3. Streak resets to 0 whenever hint reveals answers.

This rule applies to all language variants of these pages (e.g. `basicai.html`, `korean/basicai.html`, and any future translations).
