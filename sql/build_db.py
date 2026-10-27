"""Splits the clean CSV into two related tables (accounts, posts), saves them as CSV,
and loads them into a SQLite database so the queries in queries.sql can be run.
Run from the project root:  python sql/build_db.py"""
import sqlite3
import pandas as pd

df = pd.read_csv("data/instagram_clean.csv")

# accounts: one row per account (primary key = account_id)
accounts = df[["account_id", "niche", "followers"]].drop_duplicates()
assert accounts["account_id"].is_unique, "followers/niche must be constant per account"

# posts: one row per post (foreign key = account_id)
posts = df[["post_id", "account_id", "post_date", "hour", "weekday", "post_type",
            "hashtag_count", "caption_length", "has_cta", "impressions", "reach",
            "likes", "comments", "shares", "saves", "profile_visits", "follows_gained",
            "engagement_rate"]].copy()
for c in ["saves", "caption_length"]:
    posts[c] = posts[c].round().astype(int)

accounts.to_csv("data/accounts.csv", index=False)
posts.to_csv("data/posts.csv", index=False)

with open("sql/schema.sql") as f:
    schema = f.read()

con = sqlite3.connect("sql/instagram.db")
con.execute("PRAGMA foreign_keys = ON;")
con.executescript("DROP TABLE IF EXISTS posts; DROP TABLE IF EXISTS accounts;")
con.executescript(schema)
accounts.to_sql("accounts", con, if_exists="append", index=False)
posts.to_sql("posts", con, if_exists="append", index=False)
con.commit()
print("accounts:", con.execute("SELECT COUNT(*) FROM accounts").fetchone()[0])
print("posts:   ", con.execute("SELECT COUNT(*) FROM posts").fetchone()[0])
con.close()
