
import os
import random
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from utils import ensure_dirs, RAW_DIR, MARKETS, ACCOUNTS, BRANDS, REPS, CATEGORIES

random.seed(42)
np.random.seed(42)

parser = argparse.ArgumentParser(description='Generate simulated CPWS-style data over N days.')
parser.add_argument('--days', type=int, default=1, help='Number of days to generate (backwards from today)')
parser.add_argument('--start', type=str, default=None, help='Optional start date YYYY-MM-DD. If provided, goes forward N days.')
parser.add_argument('--force', action='store_true', help='Overwrite existing daily files and rebuild history for those days.')
args = parser.parse_args()

ensure_dirs()

if args.start:
    start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
    date_list = [start_date + timedelta(days=i) for i in range(max(1, args.days))]
else:
    today = datetime.utcnow().date()
    date_list = [today - timedelta(days=i) for i in range(max(1, args.days))][::-1]

all_new = []
for run_date in date_list:
    rows = []
    for _ in range(800):
        market = random.choice(MARKETS)
        account = random.choice(ACCOUNTS)
        brand = random.choice(BRANDS)
        category = random.choice(CATEGORIES)
        rep = random.choice(REPS)
        base_goal = {'Wine':120,'Spirits':100,'Beer':150}[category]
        account_factor = 1.0 + (ACCOUNTS.index(account)*0.05)
        market_factor = 1.0 + (MARKETS.index(market)*0.07)
        daily_goal = int(np.random.normal(base_goal*account_factor*market_factor,15))
        daily_goal = max(daily_goal, 20)
        displays = max(0, int(np.random.poisson(1)))
        pods = max(1, int(np.random.normal(12,3)))
        voids = max(0, int(np.random.poisson(1)))
        uplift = 1.0 + 0.10*displays
        void_penalty = 1.0 - min(voids*0.03, 0.4)
        noise = np.random.normal(0.95, 0.1)
        sales = int(max(0, daily_goal*uplift*void_penalty*noise))
        rows.append({'date':run_date.isoformat(),'market':market,'account':account,'brand':brand,'category':category,'rep':rep,'goal':daily_goal,'sales_volume':sales,'displays':displays,'pods':pods,'voids':voids})
    df_day = pd.DataFrame(rows)
    daily_path = os.path.join(RAW_DIR, f'daily_{run_date.isoformat()}.csv')
    if not os.path.exists(daily_path) or args.force:
        df_day.to_csv(daily_path, index=False)
    all_new.append(df_day)

history_path = os.path.join(RAW_DIR, 'raw_history.csv')
if os.path.exists(history_path) and not args.force:
    hist = pd.read_csv(history_path)
else:
    hist = pd.DataFrame(columns=['date','market','account','brand','category','rep','goal','sales_volume','displays','pods','voids'])

combined = pd.concat([hist]+all_new, ignore_index=True)
combined.drop_duplicates(subset=['date','market','account','brand','rep'], keep='last', inplace=True)
combined.to_csv(history_path, index=False)
print(f"Generated {len(date_list)} day(s); history rows: {len(combined):,}")
