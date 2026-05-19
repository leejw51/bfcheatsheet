#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def convert(src: Path, out: Path) -> None:
    html_files = sorted(p for p in src.rglob("*.html") if out not in p.parents)
    if not html_files:
        print(f"no .html files found under {src}")
        return

    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        for html in html_files:
            rel = html.relative_to(src) if src in html.parents or src == html.parent else html.name
            pdf_path = (out / Path(rel)).with_suffix(".pdf")
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            print(f">> {html} -> {pdf_path}")
            page.goto(html.resolve().as_uri(), wait_until="networkidle")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
            )
        browser.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="convert html files to pdf recursively")
    ap.add_argument("src", type=Path, help="source directory to scan")
    ap.add_argument("-o", "--out", type=Path, default=Path("pdf"), help="output directory")
    args = ap.parse_args()

    if not args.src.exists():
        print(f"error: source {args.src} does not exist", file=sys.stderr)
        return 1

    convert(args.src.resolve(), args.out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
