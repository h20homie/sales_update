
import os
import pandas as pd
import numpy as np
from utils import ensure_dirs, RAW_DIR, PROCESSED_DIR, OUTPUTS_DIR

ensure_dirs()
raw_path = os.path.join(RAW_DIR, 'raw_history.csv')
if not os.path.exists(raw_path):
    raise SystemExit('No raw history found. Run generate_fake_data.py first.')

df = pd.read_csv(raw_path)
for col in ['market','account','brand','category','rep']:
    df[col] = df[col].astype(str).str.strip()

df['date'] = pd.to_datetime(df['date'])
df['gap_to_goal'] = df['goal'] - df['sales_volume']
df['pct_attained'] = np.where(df['goal']>0, df['sales_volume']/df['goal'], np.nan)

account_lift = df['account'].map({'Tom Thumb':0.08,'Kroger':0.10,'Central Market':0.07,'Whole Foods':0.06,'Market Street':0.09}).fillna(0.07)
base_lift = 1.0 + account_lift * df['displays']
df['expected_no_display'] = (df['sales_volume']/base_lift).round(0)
df['uplift_estimate'] = (df['sales_volume'] - df['expected_no_display']).clip(lower=0)

df['week'] = df['date'].dt.isocalendar().week.astype(int)
df['year'] = df['date'].dt.year.astype(int)

processed_path = os.path.join(PROCESSED_DIR, 'processed.csv')
df.to_csv(processed_path, index=False)

territory_summary = (df.groupby(['year','week','market']).agg(goal=('goal','sum'),sales=('sales_volume','sum'),displays=('displays','sum'),pods=('pods','sum'),voids=('voids','sum'),uplift=('uplift_estimate','sum')).reset_index())
territory_summary['gap_to_goal'] = territory_summary['goal'] - territory_summary['sales']
territory_summary['pct_attained'] = np.where(territory_summary['goal']>0, territory_summary['sales']/territory_summary['goal'], np.nan)

account_summary = (df.groupby(['year','week','market','account']).agg(goal=('goal','sum'),sales=('sales_volume','sum'),displays=('displays','sum'),pods=('pods','sum'),voids=('voids','sum'),uplift=('uplift_estimate','sum')).reset_index())
account_summary['gap_to_goal'] = account_summary['goal'] - account_summary['sales']
account_summary['pct_attained'] = np.where(account_summary['goal']>0, account_summary['sales']/account_summary['goal'], np.nan)

rep_scorecards = (df.groupby(['rep','market','account']).agg(goal=('goal','sum'),sales=('sales_volume','sum'),displays=('displays','sum'),pods=('pods','sum'),voids=('voids','sum'),uplift=('uplift_estimate','sum')).reset_index())
rep_scorecards['gap_to_goal'] = rep_scorecards['goal'] - rep_scorecards['sales']
rep_scorecards['pct_attained'] = np.where(rep_scorecards['goal']>0, rep_scorecards['sales']/rep_scorecards['goal'], np.nan)

territory_summary.to_csv(os.path.join(OUTPUTS_DIR,'territory_summary.csv'), index=False)
account_summary.to_csv(os.path.join(OUTPUTS_DIR,'account_summary.csv'), index=False)
rep_scorecards.to_csv(os.path.join(OUTPUTS_DIR,'rep_scorecards.csv'), index=False)
print('Processed & rollups saved.')
