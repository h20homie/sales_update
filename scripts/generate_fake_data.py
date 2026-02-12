
import os
import random
from datetime import datetime
import numpy as np
import pandas as pd
from utils import ensure_dirs, RAW_DIR, MARKETS, ACCOUNTS, BRANDS, REPS, CATEGORIES

random.seed(42)
np.random.seed(42)

ensure_dirs()

# Parameters
n_rows = 800  # per day

# Simulate one day of data
run_date = datetime.utcnow().date()

rows = []
for _ in range(n_rows):
    market = random.choice(MARKETS)
    account = random.choice(ACCOUNTS)
    brand = random.choice(BRANDS)
    category = random.choice(CATEGORIES)
    rep = random.choice(REPS)

    # Goals vary by account/category
    base_goal = {
        'Wine': 120,
        'Spirits': 100,
        'Beer': 150
    }[category]
    account_factor = 1.0 + (ACCOUNTS.index(account) * 0.05)  # later accounts slightly higher
    market_factor = 1.0 + (MARKETS.index(market) * 0.07)
    daily_goal = int(np.random.normal(base_goal * account_factor * market_factor, 15))
    daily_goal = max(daily_goal, 20)

    # Displays and distribution
    displays = max(0, int(np.random.poisson(1)))
    pods = max(1, int(np.random.normal(12, 3)))
    voids = max(0, int(np.random.poisson(1)))

    # Sales volume: impacted by displays, voids, market/account factors
    uplift = 1.0 + 0.10 * displays
    void_penalty = 1.0 - min(voids * 0.03, 0.4)
    noise = np.random.normal(0.95, 0.1)
    sales = int(max(0, daily_goal * uplift * void_penalty * noise))

    rows.append({
        'date': run_date.isoformat(),
        'market': market,
        'account': account,
        'brand': brand,
        'category': category,
        'rep': rep,
        'goal': daily_goal,
        'sales_volume': sales,
        'displays': displays,
        'pods': pods,
        'voids': voids
    })

new_df = pd.DataFrame(rows)

# Save daily snapshot
daily_path = os.path.join(RAW_DIR, f'daily_{run_date.isoformat()}.csv')
new_df.to_csv(daily_path, index=False)

# Append to history
history_path = os.path.join(RAW_DIR, 'raw_history.csv')
if os.path.exists(history_path):
    hist_df = pd.read_csv(history_path)
    combined = pd.concat([hist_df, new_df], ignore_index=True)
else:
    combined = new_df.copy()

combined.to_csv(history_path, index=False)
print(f"Wrote {len(new_df)} rows to {daily_path} and updated {history_path} → total {len(combined)} rows")
