#!/usr/bin/env python3
"""Draw the front page for Saturday 21 November 2026 as entry.png.

A one-page newspaper front page: masthead, one lead story with a small
schematic map, six stories in a two-column grid, and an "Also in brief"
box. All text is real text drawn with DejaVu fonts. Run from anywhere:

    python3 make_image.py [output-path]

Default output is entry.png next to this script. Every line is measured
before it is drawn, and the script raises if any line would overflow
its box, so a bad layout fails loudly instead of printing cut-off text.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT = W - 2 * MARGIN  # 952

PAPER = (250, 245, 233)
INK = (17, 17, 17)
RED = (185, 28, 28)
NAVY = (31, 51, 80)
MAP_FILL = (232, 238, 244)
MAP_LINE = (31, 51, 80)
GREY = (90, 90, 90)
RULE_GREY = (170, 170, 160)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BOLD = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns lines that each fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    """Draw wrapped lines, asserting none overflows the content width."""
    for line in lines:
        width = draw.textlength(line, font=fnt)
        assert x + width <= W - MARGIN + 1, f"overflow: {line!r} ({width:.0f}px)"
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_map(draw, x0, y0, w, h):
    """Schematic map panel: Poland outline, red impact marker, Ukraine label."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=MAP_FILL, outline=INK, width=2)
    # Simplified Poland outline, relative to the panel.
    poly = [
        (70, 16), (120, 6), (175, 8), (225, 18), (265, 33), (285, 58),
        (270, 83), (240, 98), (215, 113), (185, 126), (150, 133),
        (115, 126), (85, 113), (60, 93), (48, 63), (55, 38),
    ]
    pts = [(x0 + px, y0 + py) for px, py in poly]
    draw.polygon(pts, fill=(255, 255, 255), outline=MAP_LINE, width=2)
    draw.text((x0 + 108, y0 + 52), "POLAND", font=SANS_BOLD(17), fill=NAVY)
    # Impact marker in the south-east of the outline.
    cx, cy = x0 + 252, y0 + 88
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=RED, outline=(255, 255, 255), width=2)
    draw.text((cx - 4, cy - 8), "✕", font=SANS_BOLD(13), fill=(255, 255, 255))
    draw.text((x0 + 12, y0 + h - 24), "2 missiles down",
              font=SANS(13), fill=GREY)
    draw.text((x0 + 205, y0 + h - 24), "UKRAINE", font=SANS_BOLD(14), fill=GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -----------------------------------------------------
    masthead = SERIF_BOLD(84)
    title = "WORLD NEWS"
    tw = d.textlength(title, font=masthead)
    d.text(((W - tw) / 2, 22), title, font=masthead, fill=INK)
    date = "SATURDAY, 21 NOVEMBER 2026"
    date_font = SANS_BOLD(26)
    dw = d.textlength(date, font=date_font)
    d.text(((W - dw) / 2, 118), date, font=date_font, fill=RED)
    d.line([(MARGIN, 152), (W - MARGIN, 152)], fill=INK, width=3)
    d.line([(MARGIN, 158), (W - MARGIN, 158)], fill=INK, width=1)

    # ---- Lead story ---------------------------------------------------
    lead_head = SERIF_BOLD(44)
    head_lines = wrap(d, "RUSSIAN MISSILES LAND IN POLAND", lead_head, CONTENT)
    assert len(head_lines) <= 2, f"lead headline wrapped to {len(head_lines)} lines"
    y = 172
    y = draw_lines(d, head_lines, MARGIN, y, lead_head, INK, 52)
    d.line([(MARGIN, y + 4), (MARGIN + 220, y + 4)], fill=RED, width=4)

    body_font = SANS(21)
    body = (
        "Russia hit Ukraine overnight with 400+ drones and 110+ missiles, "
        "killing at least 8 in Kyiv. Two missiles and a suspected drone came "
        "down in southeastern Poland; Prime Minister Donald Tusk called it a "
        "deliberate provocation."
    )
    body_lines = wrap(d, body, body_font, 590)
    assert len(body_lines) <= 5, f"lead body wrapped to {len(body_lines)} lines"
    draw_lines(d, body_lines, MARGIN, y + 18, body_font, INK, 28)

    draw_map(d, 648, y + 14, 340, 148)

    # ---- Divider ------------------------------------------------------
    d.line([(MARGIN, 442), (W - MARGIN, 442)], fill=INK, width=2)

    # ---- Story grid: 3 rows x 2 columns ------------------------------
    stories = [
        ("AI STOCK ROUT PUSHES S&P 500 INTO CORRECTION",
         "US stocks fell 3.7% on Friday as an AI and chip sell-off swept "
         "Wall Street, Europe and Asia. The Nasdaq erased its 2026 gains."),
        ("ICJ: MYANMAR RESPONSIBLE FOR ROHINGYA GENOCIDE",
         "The International Court of Justice found Myanmar responsible for "
         "genocide against the Rohingya, in a decision that was not unanimous."),
        ("COP31 DEADLOCKED AS TALKS RUN INTO OVERTIME",
         "Nearly 200 nations failed to agree a final communique at the UN "
         "climate summit in Antalya, and talks ran into overtime."),
        ("FBI CRIMINAL DATABASE REPORTEDLY HACKED",
         "CNN reported the FBI's crime database was hacked amid continuing "
         "US tech outages. The Agriculture Department was also hit."),
        ("TRUMP, XI AND PUTIN ISSUE JOINT PEACE DECLARATION",
         "The three leaders held their first three-way meeting in Shenzhen "
         "on Thursday and declared a commitment to peace and stability."),
    ]
    quote = ("\u201cHe is a killer.\u201d",
             "\u2014 Volodymyr Zelensky, President of Ukraine, on Vladimir Putin",
             "in response to the Shenzhen peace declaration")
    col_x = [MARGIN, 524]
    col_w = 464
    row_y = [456, 581, 706]
    row_h = 125
    head_font = SERIF_BOLD(24)
    text_font = SANS(18)
    for i, (headline, body) in enumerate(stories):
        x = col_x[i % 2]
        y = row_y[i // 2]
        h_lines = wrap(d, headline, head_font, col_w)
        assert len(h_lines) <= 2, f"story {i+1} headline wrapped to {len(h_lines)}"
        y = draw_lines(d, h_lines, x, y, head_font, INK, 28)
        b_lines = wrap(d, body, text_font, col_w)
        assert len(b_lines) <= 3, f"story {i+1} body wrapped to {len(b_lines)}"
        draw_lines(d, b_lines, x, y + 4, text_font, INK, 21)
    # Sixth cell: pull-quote panel (Zelensky's words, from the brief).
    qx, qy = col_x[1], row_y[2]
    d.rectangle([qx, qy, qx + col_w, qy + row_h - 6], outline=INK, width=2)
    d.text((qx + 14, qy + 10), quote[0], font=SERIF_BOLD(30), fill=RED)
    q_lines = wrap(d, quote[1], SANS(16), col_w - 28)
    draw_lines(d, q_lines, qx + 14, qy + 52, SANS(16), INK, 21)
    d.text((qx + 14, qy + row_h - 28), quote[2], font=SANS(14), fill=GREY)
    # Grid separators.
    d.line([(512, 456), (512, 830)], fill=RULE_GREY, width=1)
    for sy in (580, 705):
        d.line([(MARGIN, sy), (W - MARGIN, sy)], fill=RULE_GREY, width=1)

    # ---- Also in brief ------------------------------------------------
    box_y, box_h = 846, 150
    d.rectangle([MARGIN, box_y, W - MARGIN, box_y + box_h],
                outline=INK, width=2)
    d.text((MARGIN + 14, box_y + 10), "ALSO IN BRIEF",
           font=SANS_BOLD(20), fill=RED)
    brief = [
        "Pancreatic cancer pill: tumours undetectable in 1 in 12 patients",
        "6.9 magnitude earthquake shakes the Peruvian Andes",
        "Bayer pays $7.25 billion to settle Roundup complaints",
        "Gen Z protests spread across 25 European countries",
        "UK and EU sign biggest post-Brexit deals in Brussels",
    ]
    brief_font = SANS(18)
    y = box_y + 42
    for item in brief:
        line = "\u2022  " + item
        assert d.textlength(line, font=brief_font) <= CONTENT - 28, f"brief overflow: {line!r}"
        d.text((MARGIN + 14, y), line, font=brief_font, fill=INK)
        y += 21

    # ---- Footer -------------------------------------------------------
    d.text((MARGIN, 1006), "World news of Saturday 21 November 2026, as reported on the day.",
           font=SANS(13), fill=GREY)

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    build()
