"""Instagram Content Performance Analysis - Python step.
Run from the project root:  python python/analysis.py
Reads data/instagram_raw.csv, cleans it, analyses it, saves charts and clean data."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

# 1. Load
df = pd.read_csv("data/instagram_raw.csv")
print("Raw shape:", df.shape)
print("Missing values:\n", df.isnull().sum()[df.isnull().sum() > 0])
print("Duplicate rows:", df.duplicated().sum())

# 2. Clean
df = df.drop_duplicates()
df["saves"] = df["saves"].fillna(df["saves"].median())
df["caption_length"] = df["caption_length"].fillna(df["caption_length"].median())

# 3. Feature engineering
df["post_date"] = pd.to_datetime(df["post_date"])
df["hour"] = pd.to_datetime(df["post_time"], format="%H:%M").dt.hour
df["weekday"] = df["post_date"].dt.day_name()
df["month"] = df["post_date"].dt.month_name()
df["month_num"] = df["post_date"].dt.month
df["engagement_rate"] = (df.likes + df.comments + df.shares + df.saves) / df.reach
df["time_slot"] = pd.cut(df["hour"], bins=[-1, 5, 11, 17, 23],
                         labels=["Late night (0-5)", "Morning (6-11)", "Afternoon (12-17)", "Evening (18-23)"])
df["hashtag_group"] = pd.cut(df["hashtag_count"], bins=[-1, 5, 10, 15, 30],
                             labels=["0-5", "6-10", "11-15", "16+"])
print("Clean shape:", df.shape)

# 4. Analysis
print("\n--- Engagement rate and reach by post type ---")
by_type = df.groupby("post_type")[["engagement_rate", "reach"]].mean().sort_values("reach", ascending=False)
print(by_type)

print("\n--- Average reach by time slot ---")
by_slot = df.groupby("time_slot", observed=True)["reach"].mean()
print(by_slot)

print("\n--- Average reach by hour (top 5) ---")
by_hour = df.groupby("hour")["reach"].mean().sort_values(ascending=False)
print(by_hour.head(5))

print("\n--- Niche performance ---")
by_niche = df.groupby("niche")[["engagement_rate", "reach"]].mean().sort_values("engagement_rate", ascending=False)
print(by_niche)

print("\n--- CTA effect ---")
by_cta = df.groupby("has_cta")[["engagement_rate", "reach"]].mean()
print(by_cta)

print("\n--- Hashtag groups ---")
by_tag = df.groupby("hashtag_group", observed=True)[["engagement_rate", "reach"]].mean()
print(by_tag)

print("\n--- Weekday ---")
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
by_day = df.groupby("weekday")["reach"].mean().reindex(order)
print(by_day)

print("\n--- Correlations ---")
corr = df[["followers", "hashtag_count", "caption_length", "has_cta", "reach", "engagement_rate",
           "profile_visits", "follows_gained"]].corr()
print(corr.round(2))

# 5. Charts
fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(x=by_type.index, y=by_type["engagement_rate"] * 100, ax=ax, color="#4C72B0")
ax.set_title("Average engagement rate by post type"); ax.set_ylabel("Engagement rate (%)"); ax.set_xlabel("")
plt.tight_layout(); plt.savefig("images/engagement_by_post_type.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(7, 4))
sns.barplot(x=by_type.index, y=by_type["reach"], ax=ax, color="#55A868")
ax.set_title("Average reach by post type"); ax.set_ylabel("Average reach"); ax.set_xlabel("")
plt.tight_layout(); plt.savefig("images/reach_by_post_type.png", dpi=150); plt.close()

heat = df.pivot_table(index="weekday", columns="hour", values="reach", aggfunc="mean").reindex(order)
fig, ax = plt.subplots(figsize=(11, 4.5))
sns.heatmap(heat, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Average reach"})
ax.set_title("Average reach: weekday vs hour of posting"); ax.set_xlabel("Hour of day"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig("images/heatmap_weekday_hour.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=by_niche.index, y=by_niche["engagement_rate"] * 100, ax=ax, color="#C44E52")
ax.set_title("Average engagement rate by niche"); ax.set_ylabel("Engagement rate (%)"); ax.set_xlabel("")
plt.xticks(rotation=30)
plt.tight_layout(); plt.savefig("images/engagement_by_niche.png", dpi=150); plt.close()

monthly = df.groupby("month_num")["reach"].sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(monthly.index, monthly.values, marker="o", color="#8172B2")
ax.set_xticks(range(1, 13)); ax.set_title("Total reach by month (2025)"); ax.set_xlabel("Month"); ax.set_ylabel("Total reach")
plt.tight_layout(); plt.savefig("images/monthly_reach.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation matrix")
plt.tight_layout(); plt.savefig("images/correlation.png", dpi=150); plt.close()

# 6. Save clean data
df_out = df.drop(columns=["time_slot", "hashtag_group"])
df_out["post_date"] = df_out["post_date"].dt.strftime("%Y-%m-%d")
df_out.to_csv("data/instagram_clean.csv", index=False)
print("\nSaved data/instagram_clean.csv and charts in images/")
