
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

DATA_DIR = 'data'
PROCESSED = os.path.join(DATA_DIR, 'processed', 'processed.csv')
TERR = os.path.join(DATA_DIR, 'outputs', 'territory_summary.csv')
ACC = os.path.join(DATA_DIR, 'outputs', 'account_summary.csv')
REP = os.path.join(DATA_DIR, 'outputs', 'rep_scorecards.csv')
RECAPS_DIR = os.path.join('docs', 'weekly_recaps')

st.set_page_config(page_title='CPWS Roll-Up (Simulated)', layout='wide')
st.title('CPWS Roll-Up Dashboard (Interactive, Simulated Data)')
st.caption('Auto-updating pipeline with simulated CPWS-style data. Not real customer data.')

@st.cache_data(show_spinner=False)
def load_data():
    if not (os.path.exists(PROCESSED) and os.path.exists(TERR) and os.path.exists(ACC)):
        st.error('Processed outputs not found. Run the pipeline first.')
        st.stop()
    df = pd.read_csv(PROCESSED, parse_dates=['date'])
    terr = pd.read_csv(TERR)
    acc = pd.read_csv(ACC)
    rep = pd.read_csv(REP) if os.path.exists(REP) else pd.DataFrame()
    return df, terr, acc, rep

@st.cache_data(show_spinner=False)
def latest_recaps(n=5):
    if not os.path.isdir(RECAPS_DIR):
        return []
    pdfs = [f for f in os.listdir(RECAPS_DIR) if f.endswith('.pdf')]
    pdfs.sort(reverse=True)
    return pdfs[:n]

df, terr, acc, rep = load_data()

st.sidebar.header('Filters')
weeks = sorted(terr['week'].unique())
sel_week = st.sidebar.selectbox('ISO Week', options=weeks, index=len(weeks)-1)
markets = sorted(df['market'].unique())
sel_markets = st.sidebar.multiselect('Markets', options=markets, default=markets)
accounts = sorted(df['account'].unique())
sel_accounts = st.sidebar.multiselect('Accounts', options=accounts)

fil_df = df[df['market'].isin(sel_markets)]
if sel_accounts:
    fil_df = fil_df[fil_df['account'].isin(sel_accounts)]

wk_df = fil_df[fil_df['date'].dt.isocalendar().week.astype(int) == sel_week]

goal = wk_df['goal'].sum()
sales = wk_df['sales_volume'].sum()
g2g = max(goal - sales, 0)
pct = (sales / goal) if goal else np.nan

c1, c2, c3 = st.columns(3)
c1.metric('Total Sales (Week)', f"{int(sales):,}")
c2.metric('Gap to Goal', f"{int(g2g):,}")
c3.metric('% Attained', f"{pct:.0%}" if pd.notna(pct) else '—')

terr_wk = terr[(terr['week']==sel_week) & (terr['market'].isin(sel_markets))].sort_values('pct_attained', ascending=False)
fig_bar = px.bar(terr_wk, x='market', y='pct_attained', text='pct_attained', title=f'Territory % Attained — Week {sel_week}')
fig_bar.update_traces(texttemplate='%{text:.0%}', textposition='outside')
fig_bar.update_yaxes(tickformat='.0%')
st.plotly_chart(fig_bar, use_container_width=True)

trend = fil_df.groupby(['date','market'])['sales_volume'].sum().reset_index()
fig_line = px.line(trend, x='date', y='sales_volume', color='market', title='Daily Sales Volume Trend')
st.plotly_chart(fig_line, use_container_width=True)

acc_wk = acc[(acc['week']==sel_week) & (acc['market'].isin(sel_markets))].copy()
acc_wk['disp_per_1k_goal'] = (acc_wk['displays'] / acc_wk['goal'].replace(0,1)) * 1000
fig_heat = px.density_heatmap(acc_wk, x='account', y='market', z='disp_per_1k_goal', color_continuous_scale='Blues', title='Display Intensity (per 1,000 Goal)')
st.plotly_chart(fig_heat, use_container_width=True)

with st.expander('Rep Scorecards (filtered)'):
    if rep.empty:
        st.info('No rep scorecards yet.')
    else:
        rep_f = rep[rep['market'].isin(sel_markets)]
        if sel_accounts:
            rep_f = rep_f[rep_f['account'].isin(sel_accounts)]
        rep_f = rep_f.sort_values('pct_attained', ascending=False)
        st.dataframe(rep_f, use_container_width=True)

with st.expander('Download Data'):
    st.download_button('Processed CSV', data=df.to_csv(index=False), file_name='processed.csv')
    st.download_button('Territory Summary CSV', data=terr.to_csv(index=False), file_name='territory_summary.csv')
    st.download_button('Account Summary CSV', data=acc.to_csv(index=False), file_name='account_summary.csv')
    if not rep.empty:
        st.download_button('Rep Scorecards CSV', data=rep.to_csv(index=False), file_name='rep_scorecards.csv')

recaps = latest_recaps(5)
if recaps:
    st.subheader('Latest Weekly Recaps (PDF)')
    for r in recaps:
        st.markdown(f'- [{r}](docs/weekly_recaps/{r})')

st.caption('© 2026 Jesse Flippen · Simulated data for demonstration only.')
