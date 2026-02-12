
import os
import pandas as pd
import plotly.express as px
from plotly.io import to_html
from utils import ensure_dirs, PROCESSED_DIR, OUTPUTS_DIR, DOCS_DIR

ensure_dirs()

processed_path = os.path.join(PROCESSED_DIR, 'processed.csv')
if not os.path.exists(processed_path):
    raise SystemExit('Processed data not found. Run process_data.py first.')

df = pd.read_csv(processed_path, parse_dates=['date'])
territory_summary = pd.read_csv(os.path.join(OUTPUTS_DIR, 'territory_summary.csv'))
account_summary = pd.read_csv(os.path.join(OUTPUTS_DIR, 'account_summary.csv'))

last_dt = df['date'].max()
last_update = pd.Timestamp(last_dt).strftime('%Y-%m-%d')

# Charts
latest_week = territory_summary['week'].max()
latest_year = territory_summary[territory_summary['week'] == latest_week]['year'].max()
latest_terr = territory_summary[(territory_summary['year']==latest_year) & (territory_summary['week']==latest_week)]

bar = px.bar(latest_terr.sort_values('pct_attained', ascending=False), 
             x='market', y='pct_attained', 
             text='pct_attained',
             title=f'Territory % Attained - Week {latest_week} ({latest_year})')
bar.update_traces(texttemplate='%{text:.0%}', textposition='outside')
bar.update_yaxes(tickformat='.0%')

trend = df.groupby(['date', 'market'])['sales_volume'].sum().reset_index()
line = px.line(trend, x='date', y='sales_volume', color='market', title='Daily Sales Volume Trend by Market')

acc = account_summary[(account_summary['year']==latest_year) & (account_summary['week']==latest_week)].copy()
acc['disp_per_1k_goal'] = (acc['displays'] / acc['goal'].replace(0, 1)) * 1000
heat = px.density_heatmap(acc, x='account', y='market', z='disp_per_1k_goal', 
                          title='Display Intensity (per 1,000 Goal) - Latest Week',
                          color_continuous_scale='Blues')

cards_html = f'''
<div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px;">
  <div style="flex:1; min-width:220px; background:#f6f8fa; padding:16px; border-radius:8px;">
    <div style="font-size:12px; color:#555;">Last Update</div>
    <div style="font-size:22px; font-weight:700;">{last_update}</div>
  </div>
  <div style="flex:1; min-width:220px; background:#f6f8fa; padding:16px; border-radius:8px;">
    <div style="font-size:12px; color:#555;">Markets Tracked</div>
    <div style="font-size:22px; font-weight:700;">{df['market'].nunique()}</div>
  </div>
  <div style="flex:1; min-width:220px; background:#f6f8fa; padding:16px; border-radius:8px;">
    <div style="font-size:12px; color:#555;">Accounts</div>
    <div style="font-size:22px; font-weight:700;">{df['account'].nunique()}</div>
  </div>
  <div style="flex:1; min-width:220px; background:#f6f8fa; padding:16px; border-radius:8px;">
    <div style="font-size:12px; color:#555;">Total Displays (Latest Week)</div>
    <div style="font-size:22px; font-weight:700;">{int(latest_terr['displays'].sum())}</div>
  </div>
</div>
'''

html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CPWS Roll-Up Dashboard (Simulated)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 32px; }}
    h1 {{ margin-top: 0; }}
    .section {{ margin-top: 28px; }}
  </style>
</head>
<body>
  <h1>CPWS Roll-Up Dashboard (Simulated)</h1>
  <p>This dashboard auto-updates via GitHub Actions. Data are simulated for demonstration only.</p>
  {cards_html}
  <div class="section">{to_html(bar, full_html=False, include_plotlyjs='cdn')}</div>
  <div class="section">{to_html(line, full_html=False, include_plotlyjs=False)}</div>
  <div class="section">{to_html(heat, full_html=False, include_plotlyjs=False)}</div>
  <p style="margin-top:40px; color:#666; font-size:12px;">© 2026 Jesse Flippen · Simulated data.</p>
</body>
</html>'''

out_path = os.path.join(DOCS_DIR, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Wrote dashboard to {out_path}')
