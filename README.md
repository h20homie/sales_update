
# CPWS Roll-Up Pipeline (Simulated Data)

**Owner:** Jesse Flippen · **Purpose:** Demonstrate an automated, recruiter-ready data pipeline mirroring CPWS sales operations — using only simulated data.

> ⚠️ **No proprietary data.** This project uses generated, anonymized, CPWS-like data for public demonstration.

---

## 🎯 What This Project Shows
- Automated **daily data generation** (simulated CPWS sales, displays, distribution)
- **Transformations & KPIs**: Gap to Goal, % Attained, display uplift, voids
- **Roll-ups** by market → account → rep → brand → day
- **Auto-built dashboard** (GitHub Pages in `/docs`)
- **Weekly PDF recap** with wins/risks
- Scheduled with **GitHub Actions**

---

## 🧱 Architecture
```mermaid
flowchart TD
    A[GitHub Actions Schedules] --> B[Generate Fake Data
(scripts/generate_fake_data.py)]
    B --> C[Process & Model KPIs
(scripts/process_data.py)]
    C --> D[Build Dashboard (HTML)
(scripts/build_dashboard.py)]
    C --> E[Weekly Recap PDF
(scripts/generate_weekly_recap.py)]
    D --> F[GitHub Pages (/docs)]
    E --> F
```

**Entities & KPIs**
- Markets: Dallas, Austin, San Antonio, Houston
- Accounts: Tom Thumb, Kroger, Central Market, Whole Foods, Market Street
- Metrics: `goal`, `sales_volume`, `gap_to_goal`, `%_attained`, `displays`, `pods`, `voids`, `uplift_estimate`

---

## ⚙️ How It Works
1. **Daily**: A workflow runs `generate_fake_data.py` → `process_data.py` → `build_dashboard.py` and commits outputs.
2. **Weekly**: Another workflow runs `generate_weekly_recap.py` and saves a PDF to `docs/weekly_recaps/`.
3. **Pages**: GitHub Pages serves `/docs/index.html` as a public dashboard.

---

## 🚀 Quick Start
1. **Use this repo**: Click **Use this template** or copy these files into a new repo.
2. **Enable Pages:** Repo **Settings → Pages →** Build from **/docs** folder on `main`.
3. **Review Schedules:** See `.github/workflows/` — adjust cron if desired.
4. **Run Manually:** From Actions tab, run the *Daily Pipeline* workflow to generate initial data.
5. **Open Dashboard:** After the first run, visit your repo’s Pages URL (shown in Settings → Pages).

---

## 📂 Repository Structure
```
cpws-rollup-pipeline/
├── .github/
│   └── workflows/
│       ├── daily_pipeline.yml
│       └── weekly_recap.yml
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
├── docs/
│   └── weekly_recaps/
├── notebooks/
├── scripts/
│   ├── build_dashboard.py
│   ├── generate_fake_data.py
│   ├── generate_weekly_recap.py
│   ├── process_data.py
│   └── utils.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 📊 KPI Definitions
- **Gap to Goal (G2G):** `goal - sales_volume`
- **% Attained:** `sales_volume / goal`
- **Display Compliance:** displays vs. plan (simulated plan)
- **Display Uplift (estimate):** sales lift modeled from display count & account mix
- **Voids:** Estimated OOS/void signals (simulated)

---

## 🧪 Local Development
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_fake_data.py
python scripts/process_data.py
python scripts/build_dashboard.py
python scripts/generate_weekly_recap.py
```

---

## 🔒 Notes
- Replace store/account lists with ones relevant to your market if desired.
- All data are randomly generated with reasonable, CPWS-like distributions.

---

## 📜 License
MIT
