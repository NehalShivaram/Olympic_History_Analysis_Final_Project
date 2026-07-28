"""
Olympic History Explorer
A curated, interactive dashboard built on top of the analysis in
Olympic_History_Analysis.ipynb (120 years of Olympic history dataset).

Run locally with:  streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------
# Page config & consistent CVD-safe palette (matches the analysis notebook)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Olympic History Explorer", layout="wide", page_icon="🏅")

GREY = "#B0B0B0"
HIGHLIGHT = "#0072B2"
ACCENT2 = "#D55E00"
ACCENT3 = "#009E73"
CVD_SEQUENCE = ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7", "#56B4E9", "#999999"]
TEMPLATE = "plotly_white"

TEAM_SPORTS = ["Basketball", "Football", "Volleyball", "Hockey", "Handball",
               "Water Polo", "Rugby Sevens", "Baseball", "Softball"]


# ----------------------------------------------------------------------
# Data loading (cached)
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    athletes = pd.read_csv("athlete_events.csv")
    noc = pd.read_csv("noc_regions.csv")
    df = athletes.merge(noc, on="NOC", how="left")
    df["region"] = df["region"].fillna(df["Team"])
    df["event_type"] = np.where(df.Sport.isin(TEAM_SPORTS), "Team sports", "Individual sports")

    # Deduplicated medal table: one row per medal actually awarded (not per roster athlete)
    medals = (
        df.dropna(subset=["Medal"])
          .drop_duplicates(subset=["Team", "NOC", "Games", "Event", "Medal"])
    )
    return df, medals


df, medals = load_data()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.title("🏅 Filters")

year_min, year_max = int(df.Year.min()), int(df.Year.max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max), step=1)

season = st.sidebar.radio("Season", ["Both", "Summer", "Winter"], index=0)

all_regions = sorted(df.region.dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Countries (leave empty = all)", all_regions, default=[]
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: [120 Years of Olympic History](https://www.kaggle.com/datasets/heesoo37/"
    "120-years-of-olympic-history-athletes-and-results), 1896–2016."
)


def apply_filters(frame):
    out = frame[(frame.Year >= year_range[0]) & (frame.Year <= year_range[1])]
    if season != "Both":
        out = out[out.Season == season]
    if selected_regions:
        out = out[out.region.isin(selected_regions)]
    return out


df_f = apply_filters(df)
medals_f = apply_filters(medals)

# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("Olympic History Explorer")
st.caption(
    "A curated, interactive view into 120 years of Olympic results — "
    "gender progress, national strategy, and body & age effects. "
    "Full 12-question analysis available in the companion Jupyter notebook."
)

participants_f = df_f.drop_duplicates(subset=["Games", "ID"])
n_athletes = participants_f.ID.nunique()
n_countries = df_f.region.nunique()
n_medals = len(medals_f)
pct_female = (participants_f.Sex.eq("F").sum() / len(participants_f) * 100) if len(participants_f) else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Athletes", f"{n_athletes:,}")
k2.metric("Countries", f"{n_countries:,}")
k3.metric("Medals awarded", f"{n_medals:,}")
k4.metric("% Women", f"{pct_female:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["👥 Gender & Participation", "🌍 National Strategy", "📏 Body, Age & Physiology"]
)

# ======================= TAB 1: Gender & Participation =======================
with tab1:
    st.subheader("How has gender balance evolved?")

    by_year_sex = participants_f.groupby(["Year", "Sex"]).size().unstack(fill_value=0)
    if "F" in by_year_sex and "M" in by_year_sex:
        by_year_sex["pct_female"] = by_year_sex["F"] / (by_year_sex["F"] + by_year_sex["M"]) * 100
        fig = px.area(
            by_year_sex.reset_index(), x="Year", y="pct_female",
            title="Share of female athletes over time",
            labels={"pct_female": "% of athletes who are women"}, template=TEMPLATE,
        )
        fig.update_traces(line_color=HIGHLIGHT, fillcolor="rgba(0,114,178,0.25)")
        fig.add_hline(y=50, line_dash="dot", line_color=GREY, annotation_text="parity")
        fig.update_layout(yaxis_ticksuffix="%", xaxis_title=None, showlegend=False, margin=dict(t=60))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

    col1, col2 = st.columns(2)

    with col1:
        year_options = sorted(participants_f.Year.unique())
        pick_year = st.select_slider(
            "Sport breakdown for year:", options=year_options,
            value=year_options[-1] if year_options else year_min,
        )
        snapshot = participants_f[participants_f.Year == pick_year]
        sport_gender = snapshot.groupby(["Sport", "Sex"]).size().unstack(fill_value=0)
        sport_gender = sport_gender[sport_gender.sum(axis=1) > 10]
        if "F" in sport_gender:
            sport_gender["pct_female"] = sport_gender["F"] / sport_gender.sum(axis=1) * 100
            sport_gender = sport_gender.sort_values("pct_female").reset_index()
            fig2 = px.bar(
                sport_gender, x="pct_female", y="Sport", orientation="h",
                title=f"% women by sport, {pick_year}",
                labels={"pct_female": "% women"}, template=TEMPLATE,
                color_discrete_sequence=[HIGHLIGHT],
            )
            fig2.add_vline(x=50, line_dash="dot", line_color=GREY)
            fig2.update_layout(height=500, yaxis_title=None, margin=dict(t=50))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No sport-level data for this selection.")

    with col2:
        gap = participants_f.groupby(["Year", "event_type", "Sex"]).size().unstack(fill_value=0)
        if "F" in gap and "M" in gap:
            gap["pct_female"] = gap["F"] / (gap["F"] + gap["M"]) * 100
            gap = gap.reset_index()
            fig3 = px.line(
                gap, x="Year", y="pct_female", color="event_type", markers=True,
                title="Team vs. individual sports: female participation",
                labels={"pct_female": "% women"}, template=TEMPLATE,
                color_discrete_map={"Team sports": HIGHLIGHT, "Individual sports": ACCENT2},
            )
            fig3.add_hline(y=50, line_dash="dot", line_color=GREY)
            fig3.update_layout(height=500, legend_title=None, xaxis_title=None, margin=dict(t=50))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data for the selected filters.")

# ======================= TAB 2: National Strategy =======================
with tab2:
    st.subheader("Which countries punch above their weight?")

    athletes_per_noc = df_f.drop_duplicates(subset=["NOC", "ID"]).groupby("NOC").size()
    medals_per_noc = medals_f.groupby("NOC").size()
    eff = pd.DataFrame({"athletes": athletes_per_noc, "medals": medals_per_noc}).fillna(0)
    eff = eff[eff.athletes >= 20]
    eff["medals_per_100_athletes"] = eff.medals / eff.athletes * 100
    eff = eff.merge(df_f[["NOC", "region"]].drop_duplicates(), left_index=True, right_on="NOC", how="left")

    n_show = st.slider("Number of countries to show", 5, 30, 15, key="eff_n")
    top_eff = eff.sort_values("medals_per_100_athletes", ascending=False).head(n_show)

    fig4 = px.bar(
        top_eff, x="medals_per_100_athletes", y="region", orientation="h",
        title="Medal-per-athlete efficiency (medals per 100 athletes sent)",
        labels={"medals_per_100_athletes": "Medals per 100 athletes"}, template=TEMPLATE,
        color_discrete_sequence=[ACCENT2],
    )
    fig4.update_layout(yaxis={"categoryorder": "total ascending"}, yaxis_title=None, margin=dict(t=60))
    st.plotly_chart(fig4, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Specialization: does a country over-index in a single sport?**")
        highlight_country = st.selectbox(
            "Highlight a country", ["(none)"] + sorted(medals_f.region.dropna().unique())
        )
        noc_sport_medals = medals_f.groupby(["NOC", "Sport"]).size().reset_index(name="sport_medals")
        noc_total = medals_f.groupby("NOC").size().rename("total_medals")
        sport_total = medals_f.groupby("Sport").size().rename("sport_total")
        grand_total = len(medals_f)
        spec = noc_sport_medals.merge(noc_total, on="NOC").merge(sport_total, on="Sport")
        spec = spec[spec.total_medals >= 10]
        if grand_total > 0 and len(spec):
            spec["specialization_index"] = (spec.sport_medals / spec.total_medals) / (spec.sport_total / grand_total)
            spec = spec.merge(df_f[["NOC", "region"]].drop_duplicates(), on="NOC", how="left")
            top_spec = spec[spec.sport_medals >= 8].sort_values("specialization_index", ascending=False).head(12)
            colors = [HIGHLIGHT if r == highlight_country else GREY for r in top_spec.region]
            fig5 = px.bar(
                top_spec, x="specialization_index", y="region", orientation="h",
                title="Top sport-specialization by country",
                hover_data=["Sport"], labels={"specialization_index": "Concentration vs. global avg"},
                template=TEMPLATE,
            )
            fig5.update_traces(marker_color=colors)
            fig5.add_vline(x=1, line_dash="dot", line_color=GREY)
            fig5.update_layout(yaxis_title=None, margin=dict(t=50))
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Not enough data for this selection.")

    with col2:
        st.markdown("**Rising & declining medal share**")
        if len(medals_f.Year.unique()) >= 4:
            share = medals_f.groupby(["Year", "region"]).size().reset_index(name="n")
            totals = medals_f.groupby("Year").size()
            share["share_pct"] = share.apply(lambda r: r.n / totals[r.Year] * 100, axis=1)
            pivot = share.pivot(index="Year", columns="region", values="share_pct").fillna(0)
            k = max(1, len(pivot) // 5)
            delta = (pivot.iloc[-k:].mean() - pivot.iloc[:k].mean()).sort_values()
            movers = pd.concat([delta.head(5), delta.tail(5)]).reset_index()
            movers.columns = ["region", "change_in_share_pts"]
            movers["direction"] = np.where(movers.change_in_share_pts > 0, "Rising", "Declining")
            fig6 = px.bar(
                movers, x="change_in_share_pts", y="region", orientation="h", color="direction",
                title="Biggest medal-share movers (selected range)",
                labels={"change_in_share_pts": "Change in share (pts)"}, template=TEMPLATE,
                color_discrete_map={"Rising": HIGHLIGHT, "Declining": ACCENT2},
            )
            fig6.add_vline(x=0, line_color=GREY)
            fig6.update_layout(yaxis_title=None, legend_title=None, margin=dict(t=50))
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("Select a wider year range to see movers.")

# ======================= TAB 3: Body, Age & Physiology =======================
with tab3:
    st.subheader("What does an Olympic medalist look like?")

    sport_options = sorted(df_f.Sport.unique())
    default_sports = [s for s in ["Basketball", "Gymnastics", "Rowing", "Weightlifting", "Marathon"] if s in sport_options][:5]
    picked_sports = st.multiselect("Sports to compare", sport_options, default=default_sports or sport_options[:5])

    col1, col2 = st.columns(2)

    with col1:
        sub = df_f[df_f.Sport.isin(picked_sports) & df_f.Sex.eq("M")].dropna(subset=["Height"])
        if len(sub):
            fig7 = px.box(
                sub, x="Sport", y="Height", color="Sport",
                title="Height distribution by sport (men)",
                labels={"Height": "Height (cm)"}, template=TEMPLATE,
                color_discrete_sequence=CVD_SEQUENCE,
            )
            fig7.update_layout(showlegend=False, xaxis_title=None, margin=dict(t=50))
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("No height data for this selection.")

    with col2:
        medal_ages = df_f.dropna(subset=["Medal", "Age"])
        med_by_sport = medal_ages.groupby("Sport")["Age"].median().sort_values()
        if len(med_by_sport) >= 6:
            youngest = med_by_sport.head(5)
            oldest = med_by_sport.tail(5)
            compare = pd.concat([youngest, oldest]).reset_index()
            compare["group"] = ["Youngest medalists"] * len(youngest) + ["Oldest medalists"] * len(oldest)
            fig8 = px.bar(
                compare, x="Age", y="Sport", color="group", orientation="h",
                title="Youngest vs. oldest median medalist age by sport",
                labels={"Age": "Median age"}, template=TEMPLATE,
                color_discrete_map={"Youngest medalists": HIGHLIGHT, "Oldest medalists": ACCENT2},
            )
            fig8.update_layout(yaxis_title=None, legend_title=None, margin=dict(t=50))
            st.plotly_chart(fig8, use_container_width=True)
        else:
            st.info("Not enough medalist data for this selection.")

    st.markdown("**Medalist age trend by decade**")
    medalists_age = df_f.dropna(subset=["Medal", "Age"]).copy()
    if len(medalists_age):
        medalists_age["decade"] = (medalists_age.Year // 10) * 10
        decade_age = medalists_age.groupby(["decade", "Season"])["Age"].median().reset_index()
        fig9 = px.line(
            decade_age, x="decade", y="Age", color="Season", markers=True,
            title="Median medalist age by decade",
            labels={"Age": "Median age", "decade": "Decade"}, template=TEMPLATE,
            color_discrete_map={"Summer": HIGHLIGHT, "Winter": ACCENT2},
        )
        fig9.update_layout(legend_title=None, margin=dict(t=50))
        st.plotly_chart(fig9, use_container_width=True)
    else:
        st.info("No medalist age data for this selection.")

st.markdown("---")
st.caption(
    "Built with Streamlit + Plotly · Full analysis (12 questions) in the companion notebook · "
    "Source data: 120 Years of Olympic History (Kaggle)."
)
