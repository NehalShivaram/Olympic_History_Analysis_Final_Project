# Olympic History Explorer — Final Individual Project (Data Visualization)

Analysis of 120 years of Olympic history (1896–2016): 12 multi-dimensional analytical
questions, each answered with a publication-ready Plotly visualization, plus an
interactive Streamlit dashboard.

**Live dashboard:** _add your Streamlit Community Cloud URL here after deploying_

## Repo contents

| File | Description |
|---|---|
| `Olympic_History_Analysis.ipynb` | Full analysis notebook — prelim EDA + 12 analytical questions, each with its own Plotly visualization and written insight |
| `app.py` | Streamlit dashboard — curated, interactive subset of the analysis (3 tabs, global filters) |
| `requirements.txt` | Python dependencies for both the notebook and the dashboard |
| `athlete_events.csv` | Athlete-event records (176,225 rows — a fixed random 65% sample of the original 271,116-row dataset, kept under GitHub's 25MB web-upload limit; same 15 columns, same year/sport/country coverage) |
| `noc_regions.csv` | NOC code → country/region lookup |

Original full dataset: [120 Years of Olympic History (Kaggle)](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results)

## Run the notebook

```bash
pip install -r requirements.txt
jupyter notebook Olympic_History_Analysis.ipynb
```

## Run the dashboard locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy the dashboard to Streamlit Community Cloud

1. Push this repo to GitHub (public).
2. Go to [share.streamlit.io](https://olympichistoryanalysisfinalproject-krj2z7d9tnqnb8kgscv7rg.streamlit.app) → **New app**.
3. Select this repo, branch `main`, main file path **`app.py`**.
4. Deploy — copy the resulting `*.streamlit.app` URL back into this README.

## Analytical questions covered

1. Gender balance of athletes over time, and variation by sport
2. Medal-per-athlete efficiency by country
3. Athlete body type by sport, and change over time (e.g. basketball height)
4. Optimal age range for medals, by sport type
5. Steepest rises/declines in national medal share (last 50 years)
6. Host-country medal-share advantage
7. Winter vs. Summer participation by region (climate/geography)
8. Gender age-gap among medalists, by sport
9. National sport specialization (medal concentration index)
10. Medalist age trend by decade, Summer vs. Winter
11. Breadth of sports entered vs. total medal count
12. Gender-parity progress: team vs. individual sports

## Design notes

- Colorblind-safe (Okabe-Ito) palette used consistently across every chart
- Medal counts are deduplicated per-event (team-sport rosters would otherwise inflate totals — one Olympic gold medal creates one row per roster athlete in the raw data)
- Titles state the takeaway, not just the variables plotted
