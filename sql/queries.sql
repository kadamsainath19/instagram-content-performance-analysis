-- Instagram Content Performance Analysis: analysis queries
-- Tested on SQLite. In MySQL/PostgreSQL they work as-is.

-- 1. Overview KPIs
SELECT COUNT(*)                 AS total_posts,
       SUM(reach)               AS total_reach,
       ROUND(AVG(reach), 0)     AS avg_reach,
       ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct
FROM posts;

-- 2. Engagement and reach by post type
SELECT post_type,
       COUNT(*)                             AS posts,
       ROUND(AVG(engagement_rate) * 100, 2) AS avg_engagement_pct,
       ROUND(AVG(reach), 0)                 AS avg_reach
FROM posts
GROUP BY post_type
ORDER BY avg_engagement_pct DESC;

-- 3. Best hour to post (by average reach)
SELECT hour, COUNT(*) AS posts, ROUND(AVG(reach), 0) AS avg_reach
FROM posts
GROUP BY hour
ORDER BY avg_reach DESC;

-- 4. Time-of-day buckets
SELECT CASE WHEN hour BETWEEN 0  AND 5  THEN '1. Late night (0-5)'
            WHEN hour BETWEEN 6  AND 11 THEN '2. Morning (6-11)'
            WHEN hour BETWEEN 12 AND 17 THEN '3. Afternoon (12-17)'
            ELSE                             '4. Evening (18-23)' END AS time_slot,
       ROUND(AVG(reach), 0) AS avg_reach
FROM posts
GROUP BY time_slot
ORDER BY time_slot;

-- 5. Niche performance (uses JOIN through the foreign key)
SELECT a.niche,
       COUNT(*)                               AS posts,
       ROUND(AVG(p.reach), 0)                 AS avg_reach,
       ROUND(AVG(p.engagement_rate) * 100, 2) AS avg_engagement_pct
FROM posts p
JOIN accounts a ON p.account_id = a.account_id
GROUP BY a.niche
ORDER BY avg_reach DESC;

-- 6. Does a call-to-action (CTA) help?
SELECT has_cta,
       COUNT(*)                               AS posts,
       ROUND(AVG(reach), 0)                   AS avg_reach,
       ROUND(AVG(engagement_rate) * 100, 2)   AS avg_engagement_pct
FROM posts
GROUP BY has_cta;

-- 7. Hashtag count groups
SELECT CASE WHEN hashtag_count <= 5  THEN '0-5'
            WHEN hashtag_count <= 10 THEN '6-10'
            WHEN hashtag_count <= 15 THEN '11-15'
            ELSE '16+' END AS hashtag_group,
       COUNT(*)             AS posts,
       ROUND(AVG(reach), 0) AS avg_reach
FROM posts
GROUP BY hashtag_group
ORDER BY MIN(hashtag_count);

-- 8. Top 5 posts per niche by reach (window function)
SELECT * FROM (
    SELECT a.niche, p.post_id, p.post_type, p.reach,
           RANK() OVER (PARTITION BY a.niche ORDER BY p.reach DESC) AS rnk
    FROM posts p
    JOIN accounts a ON p.account_id = a.account_id
) t
WHERE rnk <= 5
ORDER BY niche, rnk;

-- 9. Monthly reach with month-over-month change (CTE + LAG)
WITH monthly AS (
    SELECT SUBSTR(post_date, 1, 7) AS month, SUM(reach) AS total_reach
    FROM posts
    GROUP BY SUBSTR(post_date, 1, 7)
)
SELECT month,
       total_reach,
       ROUND((total_reach - LAG(total_reach) OVER (ORDER BY month)) * 100.0
             / LAG(total_reach) OVER (ORDER BY month), 1) AS mom_change_pct
FROM monthly
ORDER BY month;

-- 10. Top 10 accounts by average engagement (min 20 posts)
SELECT a.account_id, a.niche, a.followers,
       COUNT(*)                               AS posts,
       ROUND(AVG(p.engagement_rate) * 100, 2) AS avg_engagement_pct
FROM posts p
JOIN accounts a ON p.account_id = a.account_id
GROUP BY a.account_id, a.niche, a.followers
HAVING COUNT(*) >= 20
ORDER BY avg_engagement_pct DESC
LIMIT 10;

-- 11. Best post type inside each niche (CTE + window function)
WITH niche_type AS (
    SELECT a.niche, p.post_type, AVG(p.engagement_rate) AS eng
    FROM posts p
    JOIN accounts a ON p.account_id = a.account_id
    GROUP BY a.niche, p.post_type
)
SELECT niche, post_type, ROUND(eng * 100, 2) AS avg_engagement_pct
FROM (
    SELECT *, RANK() OVER (PARTITION BY niche ORDER BY eng DESC) AS rnk
    FROM niche_type
) t
WHERE rnk = 1;
