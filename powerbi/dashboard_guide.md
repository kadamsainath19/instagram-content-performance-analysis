# Power BI dashboard: step-by-step build guide

A `.pbix` file can only be created inside Power BI Desktop, so this guide, `measures.dax` and the two CSV files in `data/` give you everything needed to build it in about an hour. Save the finished file as `powerbi/instagram_dashboard.pbix` and add screenshots to `images/`.

## 1. Load the data
1. **Home > Get Data > Text/CSV** and load `data/accounts.csv` and `data/posts.csv`.
2. Click **Transform Data** (Power Query) and check the types:
   - `post_date` = Date
   - `hour`, `reach`, `likes`, `comments`, `shares`, `saves` and similar = Whole number
   - `engagement_rate` = Decimal number
   - `account_id`, `niche`, `post_type`, `weekday` = Text
3. **Close & Apply**.

## 2. Create the relationship (this is the foreign key)
1. Open **Model view**.
2. Drag `accounts[account_id]` onto `posts[account_id]`.
3. Check it is **One to many (1:*)**, with the single filter direction from accounts to posts.

## 3. Add measures and columns
Copy everything from `measures.dax`: measures on the `posts` table, plus the calculated columns. Then use **Column tools > Sort by column** so that `Time Slot`, `Hashtag Group` and `weekday` sort in the right order. Format `Avg Engagement Rate` as a percentage and `Avg Reach per Post` as a whole number with thousands separators.

## 4. Build the report page

| # | Visual | Fields | Insight it shows |
|---|---|---|---|
| 1 | 4 **Cards** | Total Posts, Total Reach, Avg Reach per Post, Avg Engagement Rate | Headline numbers |
| 2 | **Clustered column** | Axis: `post_type`; Values: Avg Engagement Rate | Reels have the highest engagement |
| 3 | **Clustered column** | Axis: `post_type`; Values: Avg Reach per Post | Reels reach far more people |
| 4 | **Column chart** | Axis: `Time Slot`; Values: Avg Reach per Post | Evenings are best |
| 5 | **Matrix** (heatmap) | Rows: `weekday`; Columns: `hour`; Values: Avg Reach per Post; **Conditional formatting > Background color > Color scale** | Best weekday and hour |
| 6 | **Bar chart** | Axis: `accounts[niche]`; Values: Avg Reach per Post | Niche comparison (uses the relationship) |
| 7 | **Column chart** | Axis: `Hashtag Group`; Values: Avg Reach per Post | More hashtags help up to about 15 |
| 8 | **Line chart** | Axis: `post_date` (Month); Values: Total Reach | Monthly trend |

## 5. Slicers
Add slicers for **niche**, **post_type** and **post_date** (Between). Use **Format > Edit interactions** if you want a visual not to react to a slicer.

## 6. Make it look professional
- Page title: *Instagram Content Performance Dashboard*, plus a small text box: *Synthetic proxy data, for practice*.
- Use one colour theme (View > Themes) and align all visuals to the grid.
- Keep the cards on the top row, charts below, slicers on the left or top.
- Give every visual a clear title and axis labels.
- Add a second page called **Insights** with 4 or 5 text boxes holding your key findings and recommendations.

## 7. Publish
Save the `.pbix`, take screenshots into `images/` (for example `powerbi_dashboard.png`) and link them from the README. If you have a Power BI account, you can also use **File > Publish to web** and add the link, but only for non-sensitive data like this.
