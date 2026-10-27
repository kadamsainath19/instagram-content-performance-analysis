"""Builds instagram_analysis.ipynb (with executed outputs) from the cell list below.
Run from the python/ folder:  python make_notebook.py"""
import ast, base64, contextlib, io, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

md = lambda s: ("md", s.strip("\n"))
code = lambda s: ("code", s.strip("\n"))

cells = [
md("""
# Instagram Content Performance Analysis (Python)

**Goal:** find out which post type, posting time, hashtag count and niche give the best reach and engagement.

> Data note: `instagram_raw.csv` is a **synthetic proxy dataset** (2,000 posts, 60 accounts, 2025), so the findings are for practice, not real-world conclusions.

**Engagement rate** = (likes + comments + shares + saves) / reach
"""),
code("""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
"""),
md("## 1. Load and inspect"),
code("""
df = pd.read_csv("../data/instagram_raw.csv")
print("Shape:", df.shape)
df.head()
"""),
code("""
print("Duplicate rows:", df.duplicated().sum())
print()
print("Missing values:")
print(df.isnull().sum()[df.isnull().sum() > 0])
"""),
md("## 2. Clean\nRemove duplicates and fill the missing `saves` and `caption_length` values with the median."),
code("""
df = df.drop_duplicates()
df["saves"] = df["saves"].fillna(df["saves"].median())
df["caption_length"] = df["caption_length"].fillna(df["caption_length"].median())
print("Clean shape:", df.shape)
print("Missing values left:", df.isnull().sum().sum())
"""),
md("## 3. Feature engineering"),
code("""
df["post_date"] = pd.to_datetime(df["post_date"])
df["hour"] = pd.to_datetime(df["post_time"], format="%H:%M").dt.hour
df["weekday"] = df["post_date"].dt.day_name()
df["month"] = df["post_date"].dt.month_name()
df["month_num"] = df["post_date"].dt.month
df["engagement_rate"] = (df.likes + df.comments + df.shares + df.saves) / df.reach
df["time_slot"] = pd.cut(df["hour"], bins=[-1, 5, 11, 17, 23],
                         labels=["Late night (0-5)", "Morning (6-11)", "Afternoon (12-17)", "Evening (18-23)"])
df["hashtag_group"] = pd.cut(df["hashtag_count"], bins=[-1, 5, 10, 15, 30], labels=["0-5", "6-10", "11-15", "16+"])
df[["post_type", "hour", "weekday", "reach", "engagement_rate", "time_slot"]].head()
"""),
md("## 4. Which post type performs best?"),
code("""
by_type = df.groupby("post_type")[["engagement_rate", "reach"]].mean().sort_values("reach", ascending=False)
print(by_type.round(3))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.barplot(x=by_type.index, y=by_type["engagement_rate"] * 100, ax=ax[0], color="#4C72B0")
ax[0].set_title("Engagement rate (%) by post type"); ax[0].set_xlabel(""); ax[0].set_ylabel("%")
sns.barplot(x=by_type.index, y=by_type["reach"], ax=ax[1], color="#55A868")
ax[1].set_title("Average reach by post type"); ax[1].set_xlabel(""); ax[1].set_ylabel("Reach")
plt.tight_layout(); plt.show()
"""),
md("## 5. When should we post?"),
code("""
by_slot = df.groupby("time_slot", observed=True)["reach"].mean()
print(by_slot.round(0))
print()
print("Top 5 hours by average reach:")
print(df.groupby("hour")["reach"].mean().sort_values(ascending=False).head(5).round(0))
"""),
code("""
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heat = df.pivot_table(index="weekday", columns="hour", values="reach", aggfunc="mean").reindex(order)
plt.figure(figsize=(11, 4.5))
sns.heatmap(heat, cmap="YlOrRd", cbar_kws={"label": "Average reach"})
plt.title("Average reach: weekday vs hour of posting"); plt.xlabel("Hour of day"); plt.ylabel("")
plt.tight_layout(); plt.show()
"""),
md("## 6. Do hashtags and call-to-actions (CTA) help?"),
code("""
print("Hashtag groups:")
print(df.groupby("hashtag_group", observed=True)[["reach", "engagement_rate"]].mean().round(3))
print()
print("CTA (0 = no, 1 = yes):")
print(df.groupby("has_cta")[["reach", "engagement_rate"]].mean().round(3))
"""),
md("## 7. Niche performance"),
code("""
by_niche = df.groupby("niche")[["engagement_rate", "reach"]].mean().sort_values("reach", ascending=False)
print(by_niche.round(3))

plt.figure(figsize=(8, 4))
sns.barplot(x=by_niche.index, y=by_niche["reach"], color="#C44E52")
plt.title("Average reach by niche"); plt.xlabel(""); plt.xticks(rotation=30)
plt.tight_layout(); plt.show()
"""),
md("## 8. Monthly trend"),
code("""
monthly = df.groupby("month_num")["reach"].sum()
plt.figure(figsize=(8, 4))
plt.plot(monthly.index, monthly.values, marker="o", color="#8172B2")
plt.xticks(range(1, 13)); plt.title("Total reach by month (2025)"); plt.xlabel("Month"); plt.ylabel("Total reach")
plt.tight_layout(); plt.show()
"""),
md("## 9. What is correlated with reach?"),
code("""
cols = ["followers", "hashtag_count", "caption_length", "has_cta", "reach", "engagement_rate", "profile_visits", "follows_gained"]
corr = df[cols].corr()
plt.figure(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation matrix"); plt.tight_layout(); plt.show()
"""),
md("## 10. Save the clean data"),
code("""
out = df.drop(columns=["time_slot", "hashtag_group"]).copy()
out["post_date"] = out["post_date"].dt.strftime("%Y-%m-%d")
out.to_csv("../data/instagram_clean.csv", index=False)
print("Saved ../data/instagram_clean.csv with", len(out), "rows")
"""),
md("""
## 11. Key insights (from this synthetic dataset)

1. **Reels win.** They have the highest engagement rate (about 10.2%, versus about 8.0% for images) and about 2.3x the average reach of images.
2. **Evenings are the best time.** Posts at 18:00-23:59 average the highest reach, and 18:00-19:00 are the strongest hours. Late-night posts (0-5) do worst.
3. **Hashtags help up to a point.** Reach rises from the 0-5 group to the 11-15 group, then flattens, so more than 15 hashtags adds little.
4. **CTAs make little difference** here: reach is about 3% higher, and engagement rate is slightly lower.
5. **Niche matters for reach, not engagement rate.** Comedy has by far the highest reach, while engagement rates across niches are almost the same.
6. **More followers means more reach, not better engagement.** Followers correlate with reach (about 0.57) but not with engagement rate.

**Recommendation:** post Reels in the evening with around 10-15 hashtags.
"""),
]

# --- execute code cells and capture outputs ---
ns = {}
nb_cells = []
count = 0
def to_lines(s):
    lines = s.split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]

for kind, src in cells:
    if kind == "md":
        nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": to_lines(src)})
        continue
    count += 1
    outputs = []
    buf = io.StringIO()
    tree = ast.parse(src)
    last_val = None
    with contextlib.redirect_stdout(buf):
        body = tree.body
        if body and isinstance(body[-1], ast.Expr):
            exec(compile(ast.Module(body[:-1], []), "cell", "exec"), ns)
            last_val = eval(compile(ast.Expression(body[-1].value), "cell", "eval"), ns)
        else:
            exec(compile(tree, "cell", "exec"), ns)
    text = buf.getvalue()
    if text:
        outputs.append({"output_type": "stream", "name": "stdout", "text": to_lines(text.rstrip("\n"))})
    for num in plt.get_fignums():
        b = io.BytesIO()
        plt.figure(num).savefig(b, format="png", dpi=100, bbox_inches="tight")
        outputs.append({"output_type": "display_data", "metadata": {},
                        "data": {"image/png": base64.b64encode(b.getvalue()).decode(),
                                 "text/plain": ["<Figure>"]}})
    plt.close("all")
    if last_val is not None:
        outputs.append({"output_type": "execute_result", "execution_count": count, "metadata": {},
                        "data": {"text/plain": to_lines(repr(last_val))}})
    nb_cells.append({"cell_type": "code", "execution_count": count, "metadata": {},
                     "outputs": outputs, "source": to_lines(src)})

nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
with open("instagram_analysis.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
print("notebook written,", count, "code cells")
