#!/usr/bin/env python3
"""Premium PDF generator for Status Mechanics — Lazy Scholar PH"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors
import os

# ── Color palette ──────────────────────────────────────────────────────────────
INK        = HexColor('#0E0E0E')
INK_SOFT   = HexColor('#3A3A3A')
INK_MUTED  = HexColor('#6B6B6B')
PAPER      = HexColor('#FAFAF8')
CREAM      = HexColor('#F5F4EF')
GOLD       = HexColor('#C9A84C')
GOLD_LT    = HexColor('#E8D08C')
GOLD_DK    = HexColor('#8B6914')
ACCENT     = HexColor('#1A1A2E')
RULE_COLOR = HexColor('#D4C9A8')
LOW_RED    = HexColor('#8B2020')
HIGH_GREEN = HexColor('#1A5C1A')
BG_YELLOW  = HexColor('#FFF9EC')


# ── Custom Flowables ───────────────────────────────────────────────────────────
class ColorBox(Flowable):
    """Solid colour rectangle used for section headers / callouts."""
    def __init__(self, width, height, color, radius=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.color)
        if self.radius:
            self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)
        else:
            self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


class GoldRule(Flowable):
    def __init__(self, width, thickness=2):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.height = thickness

    def draw(self):
        self.canv.setFillColor(GOLD)
        self.canv.rect(0, 0, self.width, self.thickness, fill=1, stroke=0)


class SideBar(Flowable):
    """Left-border accent bar for pull quotes / callout-light."""
    def __init__(self, width, height, bar_color=GOLD, bar_w=3, bg_color=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.bar_color = bar_color
        self.bar_w = bar_w
        self.bg_color = bg_color

    def draw(self):
        if self.bg_color:
            self.canv.setFillColor(self.bg_color)
            self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        self.canv.setFillColor(self.bar_color)
        self.canv.rect(0, 0, self.bar_w, self.height, fill=1, stroke=0)


class NumberCircle(Flowable):
    def __init__(self, num, size=20):
        Flowable.__init__(self)
        self.num = str(num)
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        r = self.size / 2
        self.canv.setFillColor(GOLD)
        self.canv.circle(r, r, r, fill=1, stroke=0)
        self.canv.setFillColor(ACCENT)
        self.canv.setFont('Helvetica-Bold', 9)
        self.canv.drawCentredString(r, r - 3, self.num)


# ── Styles ─────────────────────────────────────────────────────────────────────
def make_styles(W):
    S = {}

    S['brand'] = ParagraphStyle('brand',
        fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
        spaceAfter=32, tracking=3, alignment=TA_LEFT,
        leading=12)

    S['cover_title'] = ParagraphStyle('cover_title',
        fontName='Times-Bold', fontSize=52, textColor=white,
        leading=56, spaceAfter=20, alignment=TA_LEFT)

    S['cover_sub'] = ParagraphStyle('cover_sub',
        fontName='Times-Italic', fontSize=18, textColor=HexColor('#B8B8CC'),
        leading=26, spaceAfter=48, alignment=TA_LEFT)

    S['epigraph'] = ParagraphStyle('epigraph',
        fontName='Times-Italic', fontSize=14, textColor=INK_SOFT,
        leading=22, spaceBefore=0, spaceAfter=0,
        leftIndent=12, rightIndent=12, alignment=TA_LEFT)

    S['toc_label'] = ParagraphStyle('toc_label',
        fontName='Helvetica-Bold', fontSize=9, textColor=GOLD,
        spaceAfter=16, tracking=3, leading=14)

    S['toc_item'] = ParagraphStyle('toc_item',
        fontName='Helvetica', fontSize=11, textColor=INK_SOFT,
        leading=16, spaceAfter=4, leftIndent=28)

    S['section_num'] = ParagraphStyle('section_num',
        fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
        tracking=3, leading=12, spaceAfter=6)

    S['section_title'] = ParagraphStyle('section_title',
        fontName='Times-Bold', fontSize=24, textColor=white,
        leading=30, spaceAfter=6)

    S['section_sub'] = ParagraphStyle('section_sub',
        fontName='Times-Italic', fontSize=12, textColor=HexColor('#8888AA'),
        leading=18, spaceAfter=0)

    S['h3'] = ParagraphStyle('h3',
        fontName='Times-Bold', fontSize=18, textColor=INK,
        spaceBefore=28, spaceAfter=10, leading=24)

    S['h4'] = ParagraphStyle('h4',
        fontName='Helvetica-Bold', fontSize=9, textColor=GOLD_DK,
        spaceBefore=20, spaceAfter=8, tracking=2, leading=14)

    S['body'] = ParagraphStyle('body',
        fontName='Helvetica', fontSize=11, textColor=INK_SOFT,
        leading=18, spaceBefore=0, spaceAfter=10,
        alignment=TA_JUSTIFY)

    S['body_sm'] = ParagraphStyle('body_sm',
        fontName='Helvetica', fontSize=10, textColor=INK_SOFT,
        leading=16, spaceBefore=0, spaceAfter=6,
        alignment=TA_JUSTIFY)

    S['pull_quote'] = ParagraphStyle('pull_quote',
        fontName='Times-Italic', fontSize=15, textColor=ACCENT,
        leading=24, spaceBefore=4, spaceAfter=4,
        alignment=TA_CENTER, leftIndent=8, rightIndent=8)

    S['callout_label'] = ParagraphStyle('callout_label',
        fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
        tracking=3, leading=12, spaceAfter=6)

    S['callout_body'] = ParagraphStyle('callout_body',
        fontName='Helvetica', fontSize=10, textColor=HexColor('#DDDDE8'),
        leading=16, spaceBefore=0, spaceAfter=0, alignment=TA_LEFT)

    S['callout_light_body'] = ParagraphStyle('callout_light_body',
        fontName='Helvetica', fontSize=10, textColor=INK_SOFT,
        leading=16, spaceBefore=0, spaceAfter=0, alignment=TA_LEFT)

    S['bullet'] = ParagraphStyle('bullet',
        fontName='Helvetica', fontSize=10.5, textColor=INK_SOFT,
        leading=17, spaceBefore=2, spaceAfter=2,
        leftIndent=20, firstLineIndent=-16)

    S['checklist'] = ParagraphStyle('checklist',
        fontName='Helvetica', fontSize=10, textColor=INK_SOFT,
        leading=16, spaceBefore=3, spaceAfter=3,
        leftIndent=22, firstLineIndent=-18)

    S['numbered'] = ParagraphStyle('numbered',
        fontName='Helvetica', fontSize=10.5, textColor=INK_SOFT,
        leading=17, spaceBefore=4, spaceAfter=4,
        leftIndent=28, firstLineIndent=-22)

    S['default_num'] = ParagraphStyle('default_num',
        fontName='Helvetica-Bold', fontSize=8, textColor=GOLD_DK,
        tracking=2, leading=12, spaceAfter=4)

    S['default_title'] = ParagraphStyle('default_title',
        fontName='Times-Bold', fontSize=14, textColor=INK,
        leading=20, spaceAfter=6)

    S['principle_num'] = ParagraphStyle('principle_num',
        fontName='Times-Bold', fontSize=36, textColor=RULE_COLOR,
        leading=40, alignment=TA_CENTER)

    S['principle_label'] = ParagraphStyle('principle_label',
        fontName='Helvetica-Bold', fontSize=9, textColor=GOLD_DK,
        tracking=2, leading=14, spaceAfter=4)

    S['week_tag'] = ParagraphStyle('week_tag',
        fontName='Helvetica-Bold', fontSize=8, textColor=ACCENT,
        tracking=2, leading=12)

    S['score_range'] = ParagraphStyle('score_range',
        fontName='Helvetica-Bold', fontSize=10, textColor=INK)

    S['score_label'] = ParagraphStyle('score_label',
        fontName='Helvetica', fontSize=10, textColor=INK_SOFT)

    S['audit_domain_h'] = ParagraphStyle('audit_domain_h',
        fontName='Helvetica-Bold', fontSize=10, textColor=white,
        tracking=2, leading=14)

    S['closing_h'] = ParagraphStyle('closing_h',
        fontName='Times-Bold', fontSize=26, textColor=white,
        leading=34, spaceAfter=20)

    S['closing_body'] = ParagraphStyle('closing_body',
        fontName='Helvetica', fontSize=11, textColor=HexColor('#C8C8D8'),
        leading=19, spaceAfter=10, alignment=TA_JUSTIFY)

    S['action_step'] = ParagraphStyle('action_step',
        fontName='Helvetica', fontSize=11, textColor=HexColor('#DDDDE8'),
        leading=18, spaceAfter=6)

    S['closing_brand'] = ParagraphStyle('closing_brand',
        fontName='Helvetica-Bold', fontSize=10, textColor=GOLD,
        tracking=2, leading=14)

    S['closing_copy'] = ParagraphStyle('closing_copy',
        fontName='Helvetica', fontSize=8, textColor=HexColor('#555566'),
        leading=12)

    S['table_header'] = ParagraphStyle('table_header',
        fontName='Helvetica-Bold', fontSize=8, textColor=white,
        tracking=1, leading=13, alignment=TA_LEFT)

    S['table_cell'] = ParagraphStyle('table_cell',
        fontName='Helvetica', fontSize=9.5, textColor=INK_SOFT,
        leading=14, alignment=TA_LEFT)

    S['table_cell_low'] = ParagraphStyle('table_cell_low',
        fontName='Helvetica', fontSize=9.5, textColor=LOW_RED,
        leading=14, alignment=TA_LEFT)

    S['table_cell_high'] = ParagraphStyle('table_cell_high',
        fontName='Helvetica', fontSize=9.5, textColor=HIGH_GREEN,
        leading=14, alignment=TA_LEFT)

    S['table_cell_bold'] = ParagraphStyle('table_cell_bold',
        fontName='Helvetica-Bold', fontSize=9.5, textColor=INK,
        leading=14, alignment=TA_LEFT)

    return S


# ── Helper builders ────────────────────────────────────────────────────────────
def spacer(h=12):
    return Spacer(1, h)


def hrule(W, color=RULE_COLOR, thickness=0.5):
    return HRFlowable(width=W, thickness=thickness, color=color,
                      spaceAfter=0, spaceBefore=0)


def section_block(S, W, num_text, title_text, sub_text=None):
    """Dark banner section divider."""
    inner_w = W - 56
    items = [
        Spacer(1, 20),
        Paragraph(num_text.upper(), S['section_num']),
        Paragraph(title_text, S['section_title']),
    ]
    if sub_text:
        items.append(Paragraph(sub_text, S['section_sub']))
    items.append(Spacer(1, 20))

    tbl = Table([[items]], colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('LEFTPADDING',  (0, 0), (-1, -1), 24),
        ('RIGHTPADDING', (0, 0), (-1, -1), 24),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return [PageBreak(), tbl, spacer(28)]


def pull_quote_block(S, W, text):
    inner_w = W - 0
    p = Paragraph(text, S['pull_quote'])
    tbl = Table([[p]], colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('TOPPADDING',   (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 18),
        ('LEFTPADDING',  (0, 0), (-1, -1), 24),
        ('RIGHTPADDING', (0, 0), (-1, -1), 24),
        ('LINEABOVE',  (0, 0), (-1, 0), 2, GOLD),
        ('LINEBELOW',  (0, -1), (-1, -1), 2, GOLD),
    ]))
    return [spacer(12), tbl, spacer(12)]


def callout_dark(S, W, label, text):
    inner_w = W - 0
    cells = []
    if label:
        cells.append(Paragraph(label.upper(), S['callout_label']))
    cells.append(Paragraph(text, S['callout_body']))
    tbl = Table([[[c for c in cells]]], colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('TOPPADDING',   (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 16),
        ('LEFTPADDING',  (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('ROUNDEDCORNERS', [2]),
    ]))
    return [spacer(10), tbl, spacer(10)]


def callout_light(S, W, text, bold_prefix=None):
    inner_w = W - 0
    if bold_prefix:
        body_text = f'<b>{bold_prefix}</b> {text}'
    else:
        body_text = text
    p = Paragraph(body_text, S['callout_light_body'])
    tbl = Table([[p]], colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_YELLOW),
        ('TOPPADDING',   (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 14),
        ('LEFTPADDING',  (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('LINEBEFORE', (0, 0), (0, -1), 3, GOLD),
    ]))
    return [spacer(8), tbl, spacer(8)]


def bullet_item(S, text):
    return Paragraph(f'— {text}', S['bullet'])


def check_item(S, text):
    return Paragraph(f'☐ {text}', S['checklist'])


def numbered_item(S, n, text):
    return Paragraph(f'<b>{n}.</b> {text}', S['numbered'])


def default_block(S, W, num, title, body_text):
    inner_w = W
    cells = [
        Paragraph(f'DEFAULT {num:02d}', S['default_num']),
        Paragraph(title, S['default_title']),
        Paragraph(body_text, S['body_sm']),
    ]
    tbl = Table([[cells]], colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('TOPPADDING',   (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 14),
        ('LEFTPADDING',  (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('LINEBEFORE', (0, 0), (0, -1), 3, GOLD),
    ]))
    return [tbl, spacer(8)]


def compare_table(S, W, headers, rows, col_styles=None):
    n = len(headers)
    col_w = W / n
    col_widths = [col_w] * n

    header_row = [Paragraph(h, S['table_header']) for h in headers]
    data = [header_row]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            style_key = 'table_cell'
            if col_styles and i < len(col_styles) and col_styles[i]:
                style_key = col_styles[i]
            if i == 0:
                style_key = 'table_cell_bold'
            cells.append(Paragraph(cell, S[style_key]))
        data.append(cells)

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    ts = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('BACKGROUND', (0, 0), (0, 0), GOLD_DK),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, RULE_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PAPER, CREAM]),
    ])
    tbl.setStyle(ts)
    return [spacer(10), tbl, spacer(10)]


def audit_domain(S, W, num, title, items):
    header_cells = [
        [Paragraph(str(num), ParagraphStyle('an',
            fontName='Helvetica-Bold', fontSize=11,
            textColor=ACCENT, leading=14)),
         Paragraph(title.upper(), S['audit_domain_h'])],
    ]
    hdr = Table(header_cells, colWidths=[28, W - 28 - 48])
    hdr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('BACKGROUND', (0, 0), (0, 0), GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('LEFTPADDING',  (0, 0), (0, 0), 8),
        ('LEFTPADDING',  (1, 0), (1, 0), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))

    checklist_cells = [[check_item(S, itm)] for itm in items]
    checklist_cells.append([Paragraph(f'Domain {num} Score: ___ / 50',
        ParagraphStyle('dscore', fontName='Helvetica-Bold', fontSize=10,
                       textColor=GOLD_DK, leading=14))])

    body_tbl = Table(checklist_cells, colWidths=[W - 48])
    body_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PAPER),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, RULE_COLOR),
        ('LINEABOVE', (0, -1), (-1, -1), 0.8, RULE_COLOR),
        ('BACKGROUND', (0, -1), (-1, -1), CREAM),
    ]))

    wrapper = Table([[hdr], [body_tbl]], colWidths=[W - 48])
    wrapper.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, RULE_COLOR),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return [wrapper, spacer(16)]


def week_block(S, W, week_num, title, description, impl_items, installs):
    inner_w = W - 48

    tag = Paragraph(f'WEEK {week_num}', ParagraphStyle('wt',
        fontName='Helvetica-Bold', fontSize=8, textColor=ACCENT,
        tracking=2, leading=12, backColor=GOLD,
        borderPad=(3, 8, 3, 8)))

    cells = [
        [Paragraph(f'WEEK {week_num}', S['week_tag'])],
        [Paragraph(title, S['h3'])],
        [Paragraph(description, S['body_sm'])],
        [Paragraph('DAILY IMPLEMENTATION', S['h4'])],
    ]
    for item in impl_items:
        cells.append([bullet_item(S, item)])
    cells.append([Spacer(1, 8)])
    cells.append([Paragraph(f'<i><b>Installs:</b> {installs}</i>',
        ParagraphStyle('inst', fontName='Helvetica-Oblique', fontSize=10,
                       textColor=GOLD_DK, leading=15))])

    # flatten cells for Table
    flat = [[row[0]] for row in cells]
    tbl = Table(flat, colWidths=[inner_w])
    tbl.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, RULE_COLOR),
        ('BACKGROUND', (0, 0), (-1, -1), PAPER),
        ('BACKGROUND', (0, 0), (0, 0), GOLD),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('LEFTPADDING',  (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('TOPPADDING',   (0, 0), (0, 0), 5),
        ('BOTTOMPADDING',(0, 0), (0, 0), 5),
    ]))
    return [tbl, spacer(16)]


def principle_block(S, W, num, label, text):
    inner_w = W
    tbl = Table([[
        Paragraph(str(num), S['principle_num']),
        [Paragraph(label, S['principle_label']),
         Paragraph(text, S['body_sm'])],
    ]], colWidths=[48, inner_w - 48])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, RULE_COLOR),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 14),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
    ]))
    return [tbl, spacer(4)]


def score_table(S, W):
    rows = [
        ('●', '41 – 50', 'Strong — this domain is a status asset', '#2E7D32'),
        ('●', '31 – 40', 'Solid — minor calibration needed', '#7CB342'),
        ('●', '21 – 30', 'Developing — consistent improvement opportunity', '#F9A825'),
        ('●', '11 – 20', 'Priority — this domain is likely costing you status', '#E65100'),
        ('●', '1 – 10',  'Critical — immediate behavioral intervention needed', '#B71C1C'),
    ]

    header = Table([[Paragraph('SCORE INTERPRETATION GUIDE', S['callout_label'])]],
                   colWidths=[W - 48])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GOLD),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))

    data_rows = []
    for dot, rng, label, color in rows:
        data_rows.append([
            Paragraph(f'<font color="{color}">●</font>', ParagraphStyle('dot',
                fontName='Helvetica', fontSize=14, leading=16, textColor=HexColor(color))),
            Paragraph(rng, S['score_range']),
            Paragraph(label, S['score_label']),
        ])

    body = Table(data_rows, colWidths=[20, 60, W - 48 - 80])
    body.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PAPER),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [PAPER, CREAM]),
        ('TOPPADDING',   (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 9),
        # dot column: minimal padding so the 20pt width stays positive
        ('LEFTPADDING',  (0, 0), (0, -1), 3),
        ('RIGHTPADDING', (0, 0), (0, -1), 3),
        # other columns: standard padding
        ('LEFTPADDING',  (1, 0), (-1, -1), 10),
        ('RIGHTPADDING', (1, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    wrapper = Table([[header], [body]], colWidths=[W - 48])
    wrapper.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, RULE_COLOR),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return [spacer(12), wrapper, spacer(12)]


# ── Page callbacks ─────────────────────────────────────────────────────────────
def cover_page_template(canvas, doc):
    W, H = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # decorative circles
    canvas.setFillColor(HexColor('#C9A84C18'))
    canvas.circle(W + 60, H + 60, 280, fill=1, stroke=0)
    canvas.setFillColor(HexColor('#C9A84C0D'))
    canvas.circle(-60, -60, 220, fill=1, stroke=0)
    canvas.restoreState()


def body_page_template(canvas, doc):
    W, H = doc.pagesize
    canvas.saveState()
    # Footer
    canvas.setFillColor(RULE_COLOR)
    canvas.rect(doc.leftMargin, 0.45 * inch, W - doc.leftMargin - doc.rightMargin, 0.5, fill=1, stroke=0)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(INK_MUTED)
    canvas.drawString(doc.leftMargin, 0.3 * inch, 'Status Mechanics  ·  Lazy Scholar PH')
    canvas.drawRightString(W - doc.rightMargin, 0.3 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


# ── Main builder ───────────────────────────────────────────────────────────────
def build_pdf(output_path):
    PAGE_W, PAGE_H = letter
    L_MARGIN = R_MARGIN = 0.85 * inch
    T_MARGIN = 0.8 * inch
    B_MARGIN = 0.7 * inch
    FRAME_PAD = 6  # ReportLab default frame inner padding
    CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN - 2 * FRAME_PAD
    CONTENT_H = PAGE_H - T_MARGIN - B_MARGIN - 2 * FRAME_PAD

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=L_MARGIN, rightMargin=R_MARGIN,
        topMargin=T_MARGIN, bottomMargin=B_MARGIN,
        title='Status Mechanics — Lazy Scholar PH',
        author='Lazy Scholar PH',
        subject='The Hidden Scoring System Running Every Social Interaction',
    )

    S = make_styles(CONTENT_W)
    W = CONTENT_W
    story = []

    # ── COVER ──────────────────────────────────────────────────────────────────
    # first_page canvas callback paints the full dark background;
    # the table here carries its own ACCENT fill so every cell is dark too.
    CW = CONTENT_W  # usable column width inside the frame
    cover_cells = [
        [Paragraph('LAZY SCHOLAR PH  ·  PREMIUM DIGITAL RESOURCE', S['brand'])],
        [Spacer(1, 8)],
        [GoldRule(48)],
        [Spacer(1, 20)],
        [Paragraph('Status\nMechanics', S['cover_title'])],
        [Paragraph('The Hidden Scoring System Running Every Social Interaction', S['cover_sub'])],
        [Spacer(1, 20)],
        [Paragraph('COMPLETE GUIDE  ·  Includes 6-Domain Audit &amp; 30-Day Protocol',
            ParagraphStyle('badge_line', fontName='Helvetica-Bold', fontSize=9,
                           textColor=GOLD, tracking=1, leading=14))],
        [Spacer(1, 40)],
    ]
    cover_tbl = Table(cover_cells, colWidths=[CW])
    cover_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (0, 0), 52),   # extra top padding on first row
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(cover_tbl)
    story.append(PageBreak())

    # ── EPIGRAPH ───────────────────────────────────────────────────────────────
    story.append(spacer(20))
    epigraph_content = Paragraph(
        '“Status is not assigned. It is calculated — in real time, '
        'by every person in the room, without their conscious awareness or yours.”',
        S['epigraph'])
    ep_tbl = Table([[epigraph_content]], colWidths=[W - 0])
    ep_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('TOPPADDING',   (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 16),
        ('LEFTPADDING',  (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('LINEBEFORE', (0, 0), (0, -1), 3, GOLD),
    ]))
    story.append(ep_tbl)
    story.append(spacer(32))

    # ── TABLE OF CONTENTS ──────────────────────────────────────────────────────
    story.append(Paragraph('TABLE OF CONTENTS', S['toc_label']))
    toc_items = [
        ('01', 'Introduction: The Game You’re Already Playing'),
        ('02', 'The Two-Hierarchy Model: Dominance vs. Prestige'),
        ('03', 'The Status Signal Stack: What Is Actually Being Read'),
        ('04', 'Behavioral Scoring Patterns: Real-Time Calculations'),
        ('05', 'The 12 High-Status Behavioral Defaults'),
        ('06', 'Status Threats and Recovery'),
        ('07', 'Environmental Status Calibration'),
        ('08', 'The Status Audit: Six-Domain Self-Assessment'),
        ('09', 'The 30-Day Prestige Protocol'),
        ('10', 'Summary: The Complete Status Map'),
    ]
    for num, title in toc_items:
        row = Table([[
            Paragraph(f'<font color="#C9A84C"><b>{num}</b></font>', S['toc_item']),
            Paragraph(title, S['toc_item']),
        ]], colWidths=[32, W - 32])
        row.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 0.4, RULE_COLOR),
            ('TOPPADDING',   (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 7),
            ('LEFTPADDING',  (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(row)
    story.append(spacer(40))
    story.append(hrule(W))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Introduction',
        'The Game You’re Already Playing',
        'Why status operates beneath the level of conscious awareness — and why that matters')

    story.append(Paragraph(
        'You have been scored in every conversation you have had today.', S['h3']))
    story.append(Paragraph(
        'Not by a conscious evaluator with a clipboard — but by the pattern-recognition '
        'circuitry that every human brain runs automatically, beneath the level of language, '
        'before a single word has been exchanged. Status is assessed in the first 300 '
        'milliseconds of an interaction. It is updated continuously as the interaction unfolds. '
        'And it determines, more than any other single factor, whether you will be listened to, '
        'trusted, advanced, or overlooked.', S['body']))
    story.append(Paragraph(
        'The frustrating reality is that most people experience the <i>consequences</i> of status '
        'dynamics without ever understanding the mechanism. They sense that something invisible is '
        'being tracked. They notice that certain people command rooms effortlessly while others '
        'struggle despite technical competence. They feel the shift when an interaction goes '
        'poorly — but cannot name what caused it.', S['body']))
    story.append(Paragraph('This document names it.', S['body']))

    story += pull_quote_block(S, W,
        '“The scoring system is already running.\nThis document gives you the rulebook.”')

    story.append(Paragraph(
        'What follows is a complete architectural map of how status is assessed, maintained, '
        'compounded, and destroyed in modern professional and social environments. This is not '
        'motivational content. It is a technical manual — built on behavioral science, '
        'evolutionary psychology, and pattern recognition — designed to give you conscious '
        'access to a system that has always been running in the background. The goal is not to '
        'make you manipulative. It is to make you literate.', S['body']))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1: TWO-HIERARCHY MODEL
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section One',
        'The Two-Hierarchy Model:\nDominance vs. Prestige',
        'Why most people are playing the wrong game')

    story.append(Paragraph(
        'Every human group organizes itself along two fundamentally different status hierarchies. '
        'Most people operate as if there is only one. This mistake costs them everything.', S['body']))

    story.append(Paragraph('Hierarchy Type 1: Dominance', S['h3']))
    story.append(Paragraph(
        'Dominance hierarchies are ancient. They predate complex language. They operate on a '
        'single currency: <b>the credible threat of cost imposition</b>. A dominance-based '
        'high-status individual maintains their position by controlling resources, punishing '
        'non-compliance, and generating compliance through fear or social pressure.', S['body']))

    story.append(Paragraph('How Dominance Status Is Maintained', S['h4']))
    for item in [
        'Controlling who speaks and when',
        'Withholding approval or recognition as a power tool',
        'Exploiting social friction to establish hierarchy',
        'Punishing challenges publicly and disproportionately',
        'Monopolizing attention without reciprocation',
    ]:
        story.append(bullet_item(S, item))
    story.append(spacer(8))

    story += callout_light(S, W,
        'Dominance generates <i>compliance</i> — not respect. The moment coercive leverage '
        'is reduced, dominance status collapses instantly. It creates adversaries and produces '
        'brittle social architectures.',
        bold_prefix='The structural problem:')

    story.append(Paragraph('Hierarchy Type 2: Prestige', S['h3']))
    story.append(Paragraph(
        'Prestige hierarchies are uniquely human. A prestige-based individual maintains their '
        'position by demonstrating competence, generating value, and providing reliable signals '
        'of trustworthiness. Others defer to them voluntarily — not because they fear '
        'consequences but because they genuinely benefit from the association.', S['body']))

    story.append(Paragraph('How Prestige Status Is Maintained', S['h4']))
    for item in [
        'Consistent delivery on stated positions',
        'Genuine investment in others’ outcomes',
        'Demonstrated competence without insecurity-driven display',
        'Comfort with complexity and uncertainty',
        'Selective use of social capital',
    ]:
        story.append(bullet_item(S, item))
    story.append(spacer(8))

    story += callout_dark(S, W, 'Critical Insight',
        'Most people who are trying to “be more confident” or “project more authority” '
        'are unconsciously deploying dominance signals — generating short-term compliance '
        'while eroding long-term respect.')

    story.append(Paragraph('Behavioral Fingerprints: Dominance vs. Prestige', S['h4']))
    story += compare_table(S, W,
        ['Situation', 'Dominance Response', 'Prestige Response'],
        [
            ['Being challenged',   'Escalates, punishes',     'Engages with curiosity'],
            ['In disagreement',    'Talks over, dismisses',   'Asks clarifying questions'],
            ['When uncertain',     'Performs certainty',      'Acknowledges, investigates'],
            ['With attention',     'Monopolizes',             'Distributes strategically'],
            ['Under pressure',     'Reactive, defensive',     'Measured, deliberate'],
            ['With success',       'Claims credit',           'Attributes to team'],
            ['With failure',       'Deflects blame',          'Owns cleanly'],
        ],
        col_styles=[None, 'table_cell_low', 'table_cell_high'])

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2: STATUS SIGNAL STACK
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Two',
        'The Status Signal Stack',
        'What is actually being read in every interaction')

    story.append(Paragraph(
        'Status is not assessed on a single dimension. It is calculated across a layered stack '
        'of signals, processed simultaneously by the evaluator’s nervous system. '
        'Understanding this stack is the difference between guessing and knowing.', S['body']))

    story.append(Paragraph('Layer 1: Somatic Signals  —  Pre-Verbal, Highest Weight', S['h3']))
    story.append(Paragraph(
        'These signals are processed before language and are the hardest to fake.', S['body']))
    for item in [
        '<b>Movement economy:</b> High-status individuals move with deliberate efficiency. '
        'Low-status individuals display nervous excess movement — fidgeting, over-gesturing, self-touching.',
        '<b>Spatial occupation:</b> Status correlates with comfortable occupation of available '
        'space. Physical contraction signals submission in every mammalian species, including humans.',
        '<b>Vocal pace:</b> Dominant voices are slower. Rushed speech reads as anxiety — '
        'anxiety reads as low status.',
        '<b>Eye contact calibration:</b> Relaxed, held contact during key statements. Breaking '
        'eye contact downward signals submission; sideways signals confidence.',
        '<b>Reaction latency:</b> Immediate capitulation = low status. Deliberate pause before '
        'response = high status.',
    ]:
        story.append(bullet_item(S, item))
    story.append(spacer(8))

    story.append(Paragraph('Layer 2: Attentional Signals', S['h3']))
    story.append(Paragraph(
        'Your attention is a currency. How you spend it broadcasts your status calculation '
        'of every person in the room.', S['body']))
    story += compare_table(S, W,
        ['Pattern Type', 'Behavior', 'Signal'],
        [
            ['High-Status', 'Directs attention by genuine engagement', 'Selective = valuable'],
            ['High-Status', 'Doesn’t laugh before the punchline', 'Authentic response'],
            ['Low-Status',  'Over-nodding, reflexive agreement', 'Approval-seeking'],
            ['Low-Status',  'Seeks eye contact from high-status others', 'Upward-looking orientation'],
        ])

    story.append(Paragraph('Layer 3: Linguistic Signals', S['h3']))
    story.append(Paragraph('High-Status Linguistic Patterns', S['h4']))
    for item in [
        '<b>Declarative over interrogative:</b> “We should do X” vs. “I was thinking maybe we could do X?”',
        '<b>No pre-emptive apology:</b> “This might be wrong, but...” signals insecurity before the idea is evaluated',
        '<b>Economy of words:</b> Low-status speakers over-explain. High-status speakers state and allow silence to work.',
        '<b>First-person ownership:</b> “I decided” vs. “The decision was made”',
    ]:
        story.append(bullet_item(S, item))
    story.append(spacer(6))

    story.append(Paragraph('Common High-Cost Linguistic Errors', S['h4']))
    for n, item in enumerate([
        'Upspeak — rising inflection on declarative statements converts them into approval requests',
        'Filler over-use — signals real-time insecurity (“um, like, you know...”)',
        'Excessive hedging — “kind of”, “sort of”, “maybe” erodes perceived conviction',
        'Permission-seeking preambles — “I just wanted to say...” / “This is probably dumb but...”',
    ], 1):
        story.append(numbered_item(S, n, item))
    story.append(spacer(8))

    story.append(Paragraph('Layer 4: Social Friction Response  —  Highest Diagnostic Value', S['h3']))
    story += pull_quote_block(S, W,
        '“The status is revealed in the response,\nnot the provocation.”')
    story += compare_table(S, W,
        ['Friction Event', 'Low-Status Response', 'High-Status Response'],
        [
            ['Interrupted mid-sentence', 'Stops, defers',              'Continues without acknowledging'],
            ['Opinion challenged',       'Backs down rapidly',          '“Walk me through your thinking”'],
            ['Work criticized',          'Defensive explanation',        '“Where specifically?”'],
            ['Dismissive treatment',     'Tries harder to impress',     'Neutral, unreactive'],
            ['Joke at your expense',     'Laugh too hard or discomfort', 'Brief smile, redirect'],
            ['Ignored in group',         'Louder, more insistent',      'Patient, strategic'],
        ],
        col_styles=[None, 'table_cell_low', 'table_cell_high'])

    story.append(Paragraph('Layer 5: Consistency Signals', S['h3']))
    story.append(Paragraph(
        'Status is not a single event. It is a running average. The brain tracks consistency '
        'between what someone says and what they do with remarkable precision. Consistency '
        'destroys more status than almost any single event:', S['body']))
    for item in [
        'Changing stated opinions immediately when challenged',
        'Saying one thing in public and behaving differently in private',
        'Reliability failures: being late, not following through',
        'Mood-dependent performance — signals internal instability',
    ]:
        story.append(bullet_item(S, item))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3: BEHAVIORAL SCORING PATTERNS
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Three',
        'Behavioral Scoring Patterns',
        'Real-time calculations others run on you — and where the points go')

    story.append(Paragraph(
        'The brain’s status assessment is a composite score across six behavioral domains, '
        'updated continuously throughout every interaction.', S['body']))

    story.append(Paragraph('Domain 1: Entry Presence', S['h3']))
    story.append(Paragraph(
        'How you enter a physical space sets the opening bid for all subsequent status '
        'calculations. This is a priming effect — the brain anchors to the first signal '
        'and adjusts from there.', S['body']))

    story.append(Paragraph('Status-Positive Entry Pattern', S['h4']))
    for item in [
        'Pause briefly at the threshold — signals comfort, not urgency to be seen',
        'Move deliberately, at 80% of your natural pace',
        'Orient to the room rather than immediately searching for approval',
        'Acknowledge on your own schedule, not reflexively',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Status-Negative Entry Patterns', S['h4']))
    for item in [
        'Rushing — signals you are over-scheduled or undervalued',
        'Immediate approval-seeking — scanning for who noticed you arrived',
        'Apology-entry — opens with a deficit frame',
        'Loud overcompensation — performing energy signals the opposite of confidence',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Domain 2: Conversational Architecture', S['h3']))
    for item in [
        'Asking high-quality questions signals confidence in curiosity over need to perform',
        'Comfortable with pauses — not filling every silence',
        'Not over-explaining after making a point (state, then stop)',
        'Challenging premises rather than only adding information',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Domain 3: Disagreement Handling', S['h3']))
    story.append(Paragraph(
        'Most people either avoid disagreement entirely (low status) or escalate aggressively '
        '(dominance). The prestige-based model is neither.', S['body']))
    story.append(Paragraph('The High-Status Disagreement Protocol', S['h4']))
    for n, item in enumerate([
        'Receive the disagreement without visible reactivity',
        'Confirm understanding: “So your position is X — is that right?”',
        'State your position declaratively without over-justifying',
        'If the challenge has merit, update publicly and own the update',
        'If the challenge lacks merit, hold your position calmly',
    ], 1):
        story.append(numbered_item(S, n, item))

    story += callout_dark(S, W, 'The Critical Principle',
        'Willingness to update is high status. Reflexive updating is low status. '
        'The difference is whether the update is driven by logic or by social pressure.')

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4: THE 12 DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Four',
        'The 12 High-Status Behavioral Defaults',
        'Patterns that compound respect over time')

    story.append(Paragraph(
        'These are not techniques to deploy situationally. They are behavioral defaults — '
        'the automatic patterns of genuinely high-status individuals. The goal is to internalize '
        'them until they require no conscious effort.', S['body']))
    story.append(spacer(8))

    defaults = [
        ('Complete Before Responding',
         'Listen until the other person is fully finished — including the pause after the '
         'last word. This signals that you have enough internal security that you don’t '
         'need to be the first to fill silence.'),
        ('Hold Positions Under Pressure Unless Logic Changes',
         'Update when the reasoning changes, not when the social pressure increases. If someone '
         'simply repeats a challenge louder, that is not new information.'),
        ('Move at Your Own Pace',
         'Pace signals internal state. Deliberate movement signals comfort with one’s '
         'position. This applies to walking, speaking, responding to messages, and making decisions.'),
        ('Distribute Attention Selectively',
         'Distributing attention reflexively signals that you have no selection criteria — '
         'which signals that your attention is not particularly valuable.'),
        ('Own Ignorance Cleanly',
         '“I don’t know” is one of the highest-status phrases available. It signals '
         'security — you do not need to appear omniscient to feel secure in your position.'),
        ('Speak Last in Group Settings',
         'The person who speaks last reads the room, integrates perspectives, and delivers a '
         'synthesized view — a pattern that signals both intelligence and status comfort.'),
        ('Give Credit Before Claiming It',
         'Publicly attributing success to others does not diminish your status — it '
         'amplifies it. It signals security, leadership, and trustworthiness simultaneously.'),
        ('Challenge Premises, Not Just Conclusions',
         'Low-status individuals engage with conclusions. High-status individuals examine '
         'premises. “What are we assuming here?” signals qualitatively different engagement.'),
        ('Disengage from Status Competitions',
         'When someone is visibly competing for status, the high-status response is not to '
         'compete. Refuse to play — not with contempt, but with genuine disengagement.'),
        ('Repair Cleanly Without Performance',
         'When wrong, repair directly and briefly. “I was wrong about that” without '
         'performance or excessive explanation. Clean repair signals internal security.'),
        ('Control Your First Response',
         'The most important moment in any high-stakes interaction is the 1–2 seconds after '
         'something challenging happens. Practice deliberate latency before any significant response.'),
        ('Set the Frame',
         'Whoever defines the terms, the metrics, and the context of an interaction leads it. '
         '“The question I’m trying to answer is...” Frame-setting is leadership, not aggression.'),
    ]

    for i, (title, body) in enumerate(defaults, 1):
        story += default_block(S, W, i, title, body)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5: STATUS THREATS AND RECOVERY
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Five',
        'Status Threats and Recovery',
        'How respect is lost, damaged, and rebuilt')

    story.append(Paragraph('How Status Is Most Commonly Lost', S['h3']))

    loss_patterns = [
        ('Loss Pattern 1: Reactive Capitulation',
         'Repeatedly changing positions when challenged signals that social pressure works on you. '
         'Once established, your stated positions are treated as opening bids rather than genuine views.',
         'Begin holding positions under pressure. The first few instances will feel uncomfortable. '
         'The discomfort is the recalibration happening.'),
        ('Loss Pattern 2: Approval Accumulation',
         'Attempting to build status by accumulating approval from high-status individuals is '
         'immediately readable as low-status positioning. It makes you less interesting rather than more.',
         'Replace approval-seeking with contribution behaviors. Ask a sharp question. Disagree '
         'genuinely with a minor point. Bring information they don’t have.'),
        ('Loss Pattern 3: Over-Explanation',
         'Explaining your decisions more than the situation requires signals that you expect your '
         'position to be challenged — which signals that you believe it should be.',
         'Practice the “state and stop” discipline. Make your point. Stop. Let the silence work.'),
        ('Loss Pattern 4: Emotional Volatility',
         'Disproportionate emotional reactions signal that your internal calibration is unstable '
         'and externally dependent. These events update everyone’s model of you significantly.',
         'The pause protocol. Every time you feel a reactive impulse, insert a deliberate pause '
         'before any response.'),
        ('Loss Pattern 5: Value/Behavior Inconsistency',
         'Once observers register that your behavior does not match your stated values, every '
         'subsequent statement is evaluated through that filter.',
         'Address inconsistencies through observable behavior change — not statements about '
         'your values, but behavioral demonstration.'),
    ]

    for pattern_name, problem, recovery in loss_patterns:
        story.append(Paragraph(pattern_name, S['h4']))
        story.append(Paragraph(problem, S['body']))
        story += callout_light(S, W, recovery, bold_prefix='Recovery:')
        story.append(spacer(4))

    story.append(Paragraph('The Status Recovery Protocol', S['h3']))
    for n, item in enumerate([
        'Acknowledge the actual damage to yourself first, with specificity',
        'Identify the specific behavior — not vague self-criticism, but the exact pattern',
        'Make one clean repair — direct acknowledgment closes the loop without performance',
        'Behavioral change, not announcement — let the behavioral signal carry the message',
        'Consistency window — status repairs on a 30–60 day behavioral consistency horizon',
    ], 1):
        story.append(numbered_item(S, n, item))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6: ENVIRONMENTAL CALIBRATION
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Six',
        'Environmental Status Calibration',
        'How context changes the scoring rules')

    story.append(Paragraph(
        'Status is not computed against an absolute standard. It is computed against the '
        'contextual baseline of the environment. Understanding how context shifts the scoring '
        'rules allows you to calibrate rather than apply a single behavioral template.', S['body']))

    story.append(Paragraph('High-Stakes Professional Environments', S['h3']))
    for item in [
        'Precision and economy of language carry maximum weight',
        'Meeting commitments at 100% reliability is the core prestige signal',
        'Being right more often than wrong is the compounding asset',
        'Asking high-quality questions over making statements when uncertain',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Social and Peer Environments', S['h3']))
    for item in [
        'Warmth and generosity carry more weight than in professional contexts',
        'The ability to make others feel seen is a high-prestige behavior',
        'Humor used as connection rather than dominance is a status amplifier',
        'Contribution to group energy without monopolizing it',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Hierarchically Asymmetric Environments', S['h3']))
    story.append(Paragraph('Operating Upward (with high-status others)', S['h4']))
    for item in [
        'Do not perform humility — it signals their status should diminish you',
        'Engage as a peer in substance while acknowledging structural difference in process',
        'Bring genuine value — the highest status move in asymmetric interactions',
    ]:
        story.append(bullet_item(S, item))

    story.append(Paragraph('Operating Downward (with lower-status others)', S['h4']))
    for item in [
        'Generosity of attention is one of the highest prestige signals available',
        'Genuine interest in their perspective builds loyalty that compounds',
        'Building genuine investment (prestige) rather than using structural power (dominance)',
    ]:
        story.append(bullet_item(S, item))

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7: THE STATUS AUDIT
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Seven',
        'The Status Audit',
        'A six-domain self-assessment and calibration protocol')

    story.append(Paragraph(
        'Use this audit to generate an honest baseline. Rate each item 1–10. '
        'Your two lowest-scoring domains are your highest-leverage improvement opportunities.', S['body']))
    story.append(spacer(8))

    audit_domains = [
        ('Somatic Presence Audit', [
            'I move at a deliberate, unhurried pace in social and professional settings',
            'I maintain comfortable eye contact during key statements without staring',
            'I occupy space comfortably without physical contraction',
            'My voice pace slows (rather than accelerates) in high-pressure moments',
            'I minimize excess movement — fidgeting, self-touching, over-gesturing',
        ]),
        ('Attentional Discipline Audit', [
            'I distribute attention based on genuine engagement, not reflexive response',
            'I do not laugh at things I don’t find funny to signal approval',
            'I complete listening before formulating my response',
            'I am comfortable not seeking acknowledgment from high-status individuals',
            'I direct attention to ideas and outcomes rather than managing perceptions',
        ]),
        ('Linguistic Precision Audit', [
            'I use declarative rather than interrogative framing when stating opinions',
            'I avoid pre-emptive apology before making points',
            'I make statements without excessive hedging qualifiers',
            'I stop after making a point rather than over-explaining',
            'My speech pace in high-pressure situations is deliberate rather than rushed',
        ]),
        ('Social Friction Response Audit', [
            'When challenged, I pause before responding rather than reacting immediately',
            'I hold positions under social pressure unless the logic genuinely changes',
            'I do not escalate when challenged — I engage or decline to engage',
            'I am not visibly destabilized by dismissive treatment',
            'I respond to criticism with curiosity rather than defensiveness',
        ]),
        ('Consistency Audit', [
            'My public positions match my private behavior',
            'I follow through on stated commitments at a high rate',
            'My performance quality is consistent across good and bad days',
            'I update positions based on logic rather than social pressure',
            'I am the same person in asymmetric interactions — up and down the hierarchy',
        ]),
        ('Repair and Recovery Audit', [
            'I acknowledge mistakes and errors cleanly and briefly',
            'I do not perform apology or seek excessive reassurance after errors',
            'I repair interpersonal damage directly rather than avoiding it',
            'I identify specific behavioral patterns rather than vague self-criticism',
            'I give credit and attribute success to others readily and specifically',
        ]),
    ]

    for i, (domain_title, items) in enumerate(audit_domains, 1):
        story += audit_domain(S, W, i, domain_title, items)

    story.append(Paragraph('Interpreting Your Scores', S['h4']))
    story += score_table(S, W)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 8: 30-DAY PROTOCOL
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Section Eight',
        'The 30-Day Prestige Protocol',
        'A structured behavioral calibration plan')

    story.append(Paragraph(
        'This protocol installs the four highest-leverage status behaviors through deliberate '
        'practice. Each week adds a new behavior while maintaining prior weeks.', S['body']))
    story.append(spacer(8))

    weeks = [
        (1, 'The Pause Protocol',
         'Insert a 1–3 second deliberate pause before responding to any significant social '
         'input — questions, challenges, requests, criticism.',
         [
             'Before responding to the first question in any meeting: pause, breathe, respond',
             'When challenged: stop, let 2 seconds pass, then engage',
             'When asked for a decision you haven’t made: “Let me think about that”',
         ],
         'Reaction latency as a default — the gap between stimulus and response that signals internal security.'),
        (2, 'The State-and-Stop Discipline',
         'After making any point, statement, or opinion — stop. Do not fill the subsequent '
         'silence with elaboration or justification unless directly asked.',
         [
             'After making a recommendation: state it once, then stop',
             'After being challenged: hold the pause, then respond once — not three times',
             'After a disagreement: state your position, then stop',
         ],
         'Economy of language — statements that don’t trail off into self-undermining elaboration.'),
        (3, 'Attentional Discipline',
         'For one full day each week, track every instance of reflexive approval behavior and '
         'consciously interrupt the pattern.',
         [
             'In conversations: give attention when genuinely engaged, not as performance',
             'In group settings: contribute when you have something to add, not to signal participation',
             'With compliments: be specific and genuine, not reflexive',
         ],
         'Attentional selectivity — the signal that your engagement and approval mean something.'),
        (4, 'The Frame-Setting Practice',
         'In three interactions per week, set the frame explicitly before engaging.',
         [
             'In meetings: offer a framing statement before the group settles into someone else’s',
             'In disagreements: reframe the terms — “I think the real question is...”',
             'In negotiations: establish your evaluation criteria before the other party establishes theirs',
         ],
         'Habitual frame-setting — the automatic leadership behavior that defines interactions rather than responding to them.'),
    ]

    for week_num, title, desc, impl, installs in weeks:
        story += week_block(S, W, week_num, title, desc, impl, installs)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 9: SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    story += section_block(S, W, 'Summary',
        'The Complete Status Map',
        'Five principles that govern everything')

    principles = [
        ('Status Is Behavioral, Not Positional',
         'Title, money, and credentials create the appearance of status but not the reality. '
         'Behavioral signals are assessed continuously and override credential signals in most '
         'real-time interactions.'),
        ('Prestige Compounds. Dominance Decays.',
         'Every prestige-based behavior — genuine contribution, consistency, clean repair, '
         'generous acknowledgment — adds to a growing account. Every dominance-based '
         'behavior creates temporary compliance at the cost of long-term respect erosion.'),
        ('Reactivity Is the Universal Low-Status Signal',
         'The single most readable status signal is how strongly external events move you. '
         'The more your internal state is shaped by external inputs, the lower the status signal '
         'you broadcast. Internal stability is the foundation of all other status signals.'),
        ('Consistency Is the Delivery Mechanism',
         'Intelligence, competence, and good intentions produce no status benefit without '
         'behavioral consistency. The brain tracks pattern, not performance. One exceptional '
         'interaction is a data point. Twelve consistent interactions are a reputation.'),
        ('The Frame Holder Leads',
         'Whoever defines the terms of an interaction leads it. Frame-setting is the most '
         'leverage-efficient status behavior available — it shapes every subsequent '
         'exchange without requiring direct competition.'),
    ]

    for i, (label, text) in enumerate(principles, 1):
        story += principle_block(S, W, i, label, text)

    story.append(spacer(12))
    story.append(Paragraph('The Core Status Checklist', S['h3']))
    story.append(Paragraph(
        'Use this before entering any high-stakes social or professional environment.', S['body']))

    checklists = [
        ('Pre-Entry Calibration', [
            'Pace slowed to 80% of natural',
            'Physical expansion — not contraction',
            'Internal orientation to room, not to being seen',
            'First statement prepared as declarative, not interrogative',
        ]),
        ('In-Interaction Monitoring', [
            'Listening fully before formulating response',
            'Pausing before responding to friction',
            'Stating without over-explaining',
            'Attention directed by genuine engagement',
        ]),
        ('Post-Interaction Review', [
            'Identified any reactive capitulations',
            'Noted over-explanation patterns',
            'Assessed consistency with prior positions',
            'Identified opportunities to set frame earlier',
        ]),
    ]

    for section_name, items in checklists:
        story.append(Paragraph(section_name, S['h4']))
        for item in items:
            story.append(check_item(S, item))
        story.append(spacer(6))

    # ══════════════════════════════════════════════════════════════════════════
    # CLOSING PAGE
    # ══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    closing_content = [
        [Paragraph(
            'The scoring system doesn’t care whether you know the rules. But you do now.',
            S['closing_h'])],
        [Paragraph(
            'Every person you respect — those who seem to command rooms without effort, '
            'who hold their positions with ease, who build trust that survives context changes '
            '— operates from the principles in this document. The patterns are learnable. '
            'The calibration is available to anyone willing to be honest about where they currently are.',
            S['closing_body'])],
        [Spacer(1, 28)],
        [Paragraph('START HERE', ParagraphStyle('sh',
            fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
            tracking=3, leading=12, spaceAfter=12))],
    ]

    for step in [
        'Identify your two lowest audit scores — those are your highest-leverage opportunities',
        'Practice the pause protocol for the next 30 days without exception',
        'Set the frame deliberately in your next three interactions',
    ]:
        closing_content.append([Paragraph(f'● {step}', S['action_step'])])

    CL_W = CONTENT_W - 72  # inner usable width inside closing_tbl (36pt padding each side)
    closing_content += [
        [Spacer(1, 40)],
        [hrule(CL_W, color=HexColor('#33334A'))],
        [Spacer(1, 16)],
        [Table([[
            Paragraph('LAZY SCHOLAR PH', S['closing_brand']),
            Paragraph('© 2026 · Premium Digital Content · For personal use only',
                      S['closing_copy']),
        ]], colWidths=[CL_W * 0.5, CL_W * 0.5])],
    ]

    # Closing: use CONTENT_W column, with built-in left padding of 36
    # The later_pages callback will draw the page number; we overlay with the dark table.
    closing_tbl = Table(closing_content, colWidths=[CONTENT_W])
    closing_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 36),
        ('RIGHTPADDING', (0, 0), (-1, -1), 36),
        ('TOPPADDING',   (0, 0), (0, 0), 52),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(closing_tbl)

    # ── Build ──────────────────────────────────────────────────────────────────
    def first_page(canvas, doc):
        canvas.saveState()
        # First page cover: full dark background
        canvas.setFillColor(ACCENT)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Decorative gradient circles
        canvas.setFillColor(HexColor('#C9A84C15'))
        canvas.circle(PAGE_W + 80, PAGE_H + 80, 320, fill=1, stroke=0)
        canvas.setFillColor(HexColor('#C9A84C0A'))
        canvas.circle(-80, -80, 250, fill=1, stroke=0)
        canvas.restoreState()

    def later_pages(canvas, doc):
        canvas.saveState()
        W_p, H_p = doc.pagesize
        # light rule footer
        canvas.setFillColor(RULE_COLOR)
        canvas.rect(doc.leftMargin, 0.5 * inch,
                    W_p - doc.leftMargin - doc.rightMargin, 0.5, fill=1, stroke=0)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(INK_MUTED)
        canvas.drawString(doc.leftMargin, 0.32 * inch,
                          'Status Mechanics  ·  Lazy Scholar PH')
        canvas.drawRightString(W_p - doc.rightMargin, 0.32 * inch,
                               str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
    print(f'PDF written: {output_path}')


if __name__ == '__main__':
    out = '/home/user/Lazy-ScholarPH/ai-pipeline/pdfs/2026-05-28-premium.pdf'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build_pdf(out)
