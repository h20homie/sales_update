
import os
import pandas as pd
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from utils import PROCESSED_DIR, RECAPS_DIR

processed_path = os.path.join(PROCESSED_DIR, 'processed.csv')
if not os.path.exists(processed_path):
    raise SystemExit('Processed data not found. Run process_data.py first.')

df = pd.read_csv(processed_path, parse_dates=['date'])

df['week'] = df['date'].dt.isocalendar().week.astype(int)
df['year'] = df['date'].dt.year.astype(int)
latest_week = int(df['week'].max())
latest_year = int(df[df['week']==latest_week]['year'].max())

week_df = df[(df['year']==latest_year) & (df['week']==latest_week)]
prev_df = df[(df['year']==latest_year) & (df['week']==latest_week-1)]

wk_market = week_df.groupby('market').agg(goal=('goal','sum'), sales=('sales_volume','sum'), displays=('displays','sum'), voids=('voids','sum')).reset_index()
wk_market['pct_attained'] = wk_market['sales'] / wk_market['goal'].replace(0,1)
prev_market = prev_df.groupby('market')['sales_volume'].sum().rename('sales_prev')
wk_market = wk_market.merge(prev_market, on='market', how='left')
wk_market['sales_prev'] = wk_market['sales_prev'].fillna(0)
wk_market['wow_change'] = wk_market['sales'] - wk_market['sales_prev']

wins = wk_market.sort_values('wow_change', ascending=False).head(5)
risks = wk_market.sort_values('pct_attained', ascending=True).head(5)

os.makedirs(RECAPS_DIR, exist_ok=True)
report_name = f'recap_{latest_year}-W{latest_week:02d}.pdf'
report_path = os.path.join(RECAPS_DIR, report_name)

c = canvas.Canvas(report_path, pagesize=LETTER)
width, height = LETTER
margin = 0.75 * inch

c.setFillColor(colors.black)
c.setFont('Helvetica-Bold', 16)
c.drawString(margin, height - margin, 'CPWS Weekly Recap (Simulated)')
c.setFont('Helvetica', 10)
c.drawString(margin, height - margin - 16, f'Week {latest_week}, {latest_year}')

c.setFont('Helvetica-Bold', 12)
c.drawString(margin, height - margin - 48, 'Market Summary')

c.setFont('Helvetica', 10)
y = height - margin - 64
c.drawString(margin, y, 'Market')
c.drawString(margin + 140, y, '% Attained')
c.drawString(margin + 240, y, 'Displays')
c.drawString(margin + 320, y, 'Voids')
y -= 14

for _, r in wk_market.sort_values('pct_attained', ascending=False).iterrows():
    c.drawString(margin, y, str(r['market']))
    c.drawString(margin + 140, y, f"{r['pct_attained']:.0%}")
    c.drawString(margin + 240, y, str(int(r['displays'])))
    c.drawString(margin + 320, y, str(int(r['voids'])))
    y -= 14

y -= 10
c.setFont('Helvetica-Bold', 12)
c.drawString(margin, y, 'Top Wins (WoW Sales Change)')
y -= 16
c.setFont('Helvetica', 10)
for _, r in wins.iterrows():
    c.drawString(margin, y, f"{r['market']}: +{int(r['wow_change'])} units vs LW")
    y -= 14

y -= 10
c.setFont('Helvetica-Bold', 12)
c.drawString(margin, y, 'Top Risks (Lowest % Attained)')
y -= 16
c.setFont('Helvetica', 10)
for _, r in risks.iterrows():
    c.drawString(margin, y, f"{r['market']}: {r['pct_attained']:.0%} attained")
    y -= 14

c.setFont('Helvetica', 8)
c.setFillColor(colors.grey)
c.drawString(margin, margin, 'Auto-generated via GitHub Actions · Simulated data for demo')

c.save()
print('Wrote', report_path)
