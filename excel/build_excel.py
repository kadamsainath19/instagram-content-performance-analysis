"""Builds excel/instagram_analysis.xlsx (clean data + formula-driven summary + charts).
Run from the project root:  python excel/build_excel.py"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter

df = pd.read_csv("data/instagram_clean.csv")
df["post_date"] = pd.to_datetime(df["post_date"])
N = len(df)                      # 2000 rows -> data in rows 2..N+1
LAST = N + 1

F = "Arial"
hdr_font = Font(name=F, bold=True, color="FFFFFF", size=10)
hdr_fill = PatternFill("solid", fgColor="1F3864")
body = Font(name=F, size=10)
title_font = Font(name=F, bold=True, size=14, color="1F3864")
note_font = Font(name=F, italic=True, size=9, color="595959")

wb = Workbook()

# ---------------- Sheet 1: Data ----------------
ws = wb.active
ws.title = "Data"
cols = ["post_id", "account_id", "niche", "post_date", "post_time", "post_type", "followers",
        "hashtag_count", "caption_length", "has_cta", "impressions", "reach", "likes", "comments",
        "shares", "saves", "profile_visits", "follows_gained", "hour", "weekday"]
extra = ["engagement_rate", "time_slot"]          # formula columns
ws.append(cols + extra)
for _, r in df.iterrows():
    ws.append([r["post_id"], r["account_id"], r["niche"], r["post_date"].to_pydatetime(), r["post_time"],
               r["post_type"], int(r["followers"]), int(r["hashtag_count"]), int(round(r["caption_length"])),
               int(r["has_cta"]), int(r["impressions"]), int(r["reach"]), int(r["likes"]), int(r["comments"]),
               int(r["shares"]), int(round(r["saves"])), int(r["profile_visits"]), int(r["follows_gained"]),
               int(r["hour"]), r["weekday"]])
for i in range(2, LAST + 1):
    ws[f"U{i}"] = f"=(M{i}+N{i}+O{i}+P{i})/L{i}"                       # engagement rate
    ws[f"V{i}"] = (f'=IF(S{i}<=5,"Late night (0-5)",IF(S{i}<=11,"Morning (6-11)",'
                   f'IF(S{i}<=17,"Afternoon (12-17)","Evening (18-23)")))')
    ws[f"D{i}"].number_format = "yyyy-mm-dd"
    ws[f"U{i}"].number_format = "0.0%"
for c in range(1, len(cols + extra) + 1):
    cell = ws.cell(row=1, column=c)
    cell.font, cell.fill = hdr_font, hdr_fill
    cell.alignment = Alignment(horizontal="center")
    ws.column_dimensions[get_column_letter(c)].width = 15
for row in ws.iter_rows(min_row=2, max_row=LAST):
    for cell in row:
        cell.font = body
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:V{LAST}"

# helper ranges
def rng(col):
    return f"Data!${col}$2:${col}${LAST}"
TYPE, NICHE, CTA, HOUR, DAY, REACH, ENG, SLOT, TAGS = (rng("F"), rng("C"), rng("J"), rng("S"), rng("T"),
                                                         rng("L"), rng("U"), rng("V"), rng("H"))

# ---------------- Sheet 2: Summary ----------------
sm = wb.create_sheet("Summary")
sm["A1"] = "Instagram Content Performance - Summary (all values are formulas on the Data sheet)"
sm["A1"].font = title_font
sm["A2"] = ("Engagement rate = (likes + comments + shares + saves) / reach. "
            "Data is synthetic proxy data, so results are for practice, not real-world findings.")
sm["A2"].font = note_font

def header(row, labels):
    for j, t in enumerate(labels, start=1):
        c = sm.cell(row=row, column=j, value=t)
        c.font, c.fill, c.alignment = hdr_font, hdr_fill, Alignment(horizontal="center", wrap_text=True)

def style_body(r1, r2, ncols, fmts):
    for r in range(r1, r2 + 1):
        for j in range(1, ncols + 1):
            c = sm.cell(row=r, column=j)
            c.font = body
            if j in fmts:
                c.number_format = fmts[j]

# KPI block
sm["A4"] = "KPIs"; sm["A4"].font = Font(name=F, bold=True, size=11)
kpis = [("Total posts", f"=COUNTA({rng('A')})", "#,##0"),
        ("Total reach", f"=SUM({REACH})", "#,##0"),
        ("Average reach per post", f"=AVERAGE({REACH})", "#,##0"),
        ("Average engagement rate", f"=AVERAGE({ENG})", "0.0%")]
for i, (lab, fm, nf) in enumerate(kpis, start=5):
    sm[f"A{i}"], sm[f"B{i}"] = lab, fm
    sm[f"A{i}"].font = body; sm[f"B{i}"].font = Font(name=F, bold=True, size=10)
    sm[f"B{i}"].number_format = nf

# Table 1: post type (rows 11-15)
sm["A10"] = "1. By post type"; sm["A10"].font = Font(name=F, bold=True, size=11)
header(11, ["Post type", "Posts", "Avg reach", "Avg engagement rate"])
types = ["Reel", "Carousel", "Video", "Image"]
for i, t in enumerate(types, start=12):
    sm[f"A{i}"] = t
    sm[f"B{i}"] = f"=COUNTIF({TYPE},A{i})"
    sm[f"C{i}"] = f"=AVERAGEIF({TYPE},A{i},{REACH})"
    sm[f"D{i}"] = f"=AVERAGEIF({TYPE},A{i},{ENG})"
style_body(12, 15, 4, {2: "#,##0", 3: "#,##0", 4: "0.0%"})

# Table 2: time slot (rows 19-22)
sm["A18"] = "2. By time of day"; sm["A18"].font = Font(name=F, bold=True, size=11)
header(19, ["Time slot", "Posts", "Avg reach", "Avg engagement rate"])
slots = ["Late night (0-5)", "Morning (6-11)", "Afternoon (12-17)", "Evening (18-23)"]
for i, t in enumerate(slots, start=20):
    sm[f"A{i}"] = t
    sm[f"B{i}"] = f"=COUNTIF({SLOT},A{i})"
    sm[f"C{i}"] = f"=AVERAGEIF({SLOT},A{i},{REACH})"
    sm[f"D{i}"] = f"=AVERAGEIF({SLOT},A{i},{ENG})"
style_body(20, 23, 4, {2: "#,##0", 3: "#,##0", 4: "0.0%"})

# Table 3: niche (rows 27-34)
sm["A26"] = "3. By niche"; sm["A26"].font = Font(name=F, bold=True, size=11)
header(27, ["Niche", "Posts", "Avg reach", "Avg engagement rate"])
niches = ["Comedy", "Fitness", "Travel", "Tech", "Education", "Fashion", "Beauty", "Food"]
for i, t in enumerate(niches, start=28):
    sm[f"A{i}"] = t
    sm[f"B{i}"] = f"=COUNTIF({NICHE},A{i})"
    sm[f"C{i}"] = f"=AVERAGEIF({NICHE},A{i},{REACH})"
    sm[f"D{i}"] = f"=AVERAGEIF({NICHE},A{i},{ENG})"
style_body(28, 35, 4, {2: "#,##0", 3: "#,##0", 4: "0.0%"})

# Table 4: CTA (rows 39-40)
sm["A38"] = "4. Call-to-action (CTA) effect"; sm["A38"].font = Font(name=F, bold=True, size=11)
header(39, ["Has CTA (0=no, 1=yes)", "Posts", "Avg reach", "Avg engagement rate"])
for i, t in enumerate([0, 1], start=40):
    sm[f"A{i}"] = t
    sm[f"B{i}"] = f"=COUNTIF({CTA},A{i})"
    sm[f"C{i}"] = f"=AVERAGEIF({CTA},A{i},{REACH})"
    sm[f"D{i}"] = f"=AVERAGEIF({CTA},A{i},{ENG})"
style_body(40, 41, 4, {2: "#,##0", 3: "#,##0", 4: "0.0%"})

# Table 5: hashtag groups (rows 45-48)
sm["A44"] = "5. Hashtag count groups"; sm["A44"].font = Font(name=F, bold=True, size=11)
header(45, ["Hashtags", "Min", "Max", "Posts", "Avg reach"])
groups = [("0-5", 0, 5), ("6-10", 6, 10), ("11-15", 11, 15), ("16+", 16, 30)]
for i, (lab, lo, hi) in enumerate(groups, start=46):
    sm[f"A{i}"], sm[f"B{i}"], sm[f"C{i}"] = lab, lo, hi
    sm[f"D{i}"] = f'=COUNTIFS({TAGS},">="&B{i},{TAGS},"<="&C{i})'
    sm[f"E{i}"] = f'=AVERAGEIFS({REACH},{TAGS},">="&B{i},{TAGS},"<="&C{i})'
style_body(46, 49, 5, {4: "#,##0", 5: "#,##0"})
for i in range(46, 50):                       # min/max are hardcoded inputs -> blue
    sm[f"B{i}"].font = Font(name=F, size=10, color="0000FF")
    sm[f"C{i}"].font = Font(name=F, size=10, color="0000FF")

# Table 6: weekday x hour heatmap (rows 53-60)
sm["A52"] = "6. Average reach: weekday x hour (heatmap)"; sm["A52"].font = Font(name=F, bold=True, size=11)
header(53, ["Weekday"] + list(range(24)))
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for i, d in enumerate(days, start=54):
    sm[f"A{i}"] = d
    for h in range(24):
        col = get_column_letter(2 + h)
        sm[f"{col}{i}"] = f'=IFERROR(AVERAGEIFS({REACH},{DAY},$A{i},{HOUR},{col}$53),"")'
style_body(54, 60, 25, {j: "#,##0" for j in range(2, 26)})
sm.conditional_formatting.add("B54:Y60", ColorScaleRule(start_type="min", start_color="FFF2CC",
                                                        mid_type="percentile", mid_value=50, mid_color="F4B183",
                                                        end_type="max", end_color="C00000"))

sm.column_dimensions["A"].width = 28
for j in range(2, 26):
    sm.column_dimensions[get_column_letter(j)].width = 12

# Charts (to the right of the tables)
def bar(title, cats, vals, anchor, ytitle, pct=False):
    ch = BarChart()
    ch.type, ch.style, ch.title = "col", 10, title
    ch.y_axis.title = ytitle
    ch.add_data(vals, titles_from_data=True)
    ch.set_categories(cats)
    ch.legend = None
    ch.height, ch.width = 7.5, 13
    if pct:
        ch.y_axis.number_format = "0%"
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    sm.add_chart(ch, anchor)

bar("Engagement rate by post type", Reference(sm, min_col=1, min_row=12, max_row=15),
    Reference(sm, min_col=4, min_row=11, max_row=15), "G4", "Engagement rate", pct=True)
bar("Average reach by time of day", Reference(sm, min_col=1, min_row=20, max_row=23),
    Reference(sm, min_col=3, min_row=19, max_row=23), "P4", "Average reach")
bar("Average reach by niche", Reference(sm, min_col=1, min_row=28, max_row=35),
    Reference(sm, min_col=3, min_row=27, max_row=35), "G20", "Average reach")
bar("Average reach by hashtag group", Reference(sm, min_col=1, min_row=46, max_row=49),
    Reference(sm, min_col=5, min_row=45, max_row=49), "P20", "Average reach")

# ---------------- Sheet 3: Notes ----------------
nt = wb.create_sheet("Notes")
notes = [
    "Notes",
    "Source: data/instagram_clean.csv (synthetic proxy dataset, 2,000 posts, 60 accounts, year 2025).",
    "Cleaning already done in Python: 15 duplicate rows removed, missing saves/caption_length filled with the median.",
    "To repeat the cleaning in Excel on the raw file: Data > Remove Duplicates, then filter blanks and fill them.",
    "Engagement rate (Data!U) = (likes + comments + shares + saves) / reach.",
    "Time slot (Data!V) is derived from the hour using nested IF.",
    "Blue numbers on the Summary sheet (hashtag min/max) are inputs you can change.",
    "Pivot-table practice: Insert > PivotTable on the Data sheet, rows = post_type, values = Average of engagement_rate.",
]
for i, t in enumerate(notes, start=1):
    nt[f"A{i}"] = t
    nt[f"A{i}"].font = title_font if i == 1 else body
nt.column_dimensions["A"].width = 120

wb.save("excel/instagram_analysis.xlsx")
print("saved")
