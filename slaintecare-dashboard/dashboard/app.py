"""
app.py
Sláintecare Health Reform Analytics Dashboard
Interactive Plotly Dash dashboard visualising Irish health system KPIs.

Run: python dashboard/app.py
Open: http://localhost:8050
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Load Gold data ─────────────────────────────────────────────────────────────
def load_data():
    try:
        hospital_kpis  = pd.read_parquet("data/gold/hospital_kpis.parquet")
        rha_summary    = pd.read_parquet("data/gold/rha_summary.parquet")
        national_trend = pd.read_parquet("data/gold/national_trend.parquet")
        gp_coverage    = pd.read_parquet("data/silver/gp_coverage.parquet")
        return hospital_kpis, rha_summary, national_trend, gp_coverage
    except FileNotFoundError:
        # Run pipeline first if data not ready
        from src.transformation.bronze_transform import process_synthetic_waiting_list
        from src.transformation.silver_transform import build_silver_waiting_list, build_silver_gp_coverage
        from src.transformation.gold_aggregation import build_gold_hospital_kpis, build_gold_rha_summary, build_gold_national_trend
        from src.ingestion.hse_loader import load_hse_data

        process_synthetic_waiting_list("data/bronze/waiting_list.parquet")
        build_silver_waiting_list("data/bronze/waiting_list.parquet", "data/silver/waiting_list.parquet")
        hse = load_hse_data()
        build_silver_gp_coverage("data/raw/hse/gp_visit_cards.csv", "data/silver/gp_coverage.parquet")
        build_gold_hospital_kpis("data/silver/waiting_list.parquet", "data/gold/hospital_kpis.parquet")
        build_gold_rha_summary("data/silver/waiting_list.parquet", "data/gold/rha_summary.parquet")
        build_gold_national_trend("data/silver/waiting_list.parquet", "data/gold/national_trend.parquet")
        return load_data()


hospital_kpis, rha_summary, national_trend, gp_coverage = load_data()

# ── Colour palette (Irish government palette) ──────────────────────────────────
RHA_COLORS = {
    "Dublin & North East": "#005F87",
    "Dublin & Midlands":   "#007A4D",
    "South West":          "#C8102E",
    "South East":          "#FF8200",
    "West":                "#6B2D8B",
    "Mid West":            "#00A9CE",
    "Other / National":    "#888888",
}

STATUS_COLORS = {
    "On Target ✅":  "#007A4D",
    "Moderate ⚠️":  "#FF8200",
    "Serious 🔶":   "#E87722",
    "Critical 🔴":  "#C8102E",
}

# ── Summary KPIs ───────────────────────────────────────────────────────────────
latest_month  = national_trend["month_str"].max()
latest        = national_trend[national_trend["month_str"] == latest_month].iloc[0]
prev_year_row = national_trend[national_trend["month_str"] == national_trend["month_str"].unique()[-13]] \
                if len(national_trend) > 13 else national_trend.iloc[[0]]

total_waiting_now   = int(latest["total_waiting"])
pct_beyond_target   = float(latest["pct_beyond_target"])
pct_over_12m        = float(latest["pct_over_12_months"])
hospitals_critical  = int(hospital_kpis[hospital_kpis["month_str"] == latest_month]
                          ["hospital_status"].astype(str).str.contains("Critical").sum())

# ── App layout ─────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Sláintecare Analytics Dashboard"
)

app.layout = dbc.Container([

    # ── Header ────────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            html.H1("🇮🇪 Sláintecare Health Reform Analytics Dashboard",
                    className="text-white mb-1 mt-3",
                    style={"fontWeight": "700"}),
            html.P(f"Tracking Ireland's public health system KPIs | Data: NTPF & HSE Open Data | Latest: {latest_month}",
                   className="text-white-50 mb-3"),
        ])
    ], className="bg-dark rounded mb-4 p-3"),

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Total Patients Waiting (OP)", className="text-muted"),
                html.H3(f"{total_waiting_now:,}", className="text-primary fw-bold"),
                html.Small("Outpatient waiting list — all hospitals", className="text-muted"),
            ])
        ], className="shadow-sm border-0"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("% Waiting Beyond 12-Week Target", className="text-muted"),
                html.H3(f"{pct_beyond_target:.1f}%",
                        className=f"fw-bold {'text-danger' if pct_beyond_target > 40 else 'text-warning'}"),
                html.Small("Sláintecare OP target: 12 weeks max", className="text-muted"),
            ])
        ], className="shadow-sm border-0"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("% Waiting Over 12 Months", className="text-muted"),
                html.H3(f"{pct_over_12m:.1f}%",
                        className=f"fw-bold {'text-danger' if pct_over_12m > 5 else 'text-success'}"),
                html.Small("Sláintecare target: 0%", className="text-muted"),
            ])
        ], className="shadow-sm border-0"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Hospitals in Critical Status", className="text-muted"),
                html.H3(f"{hospitals_critical}",
                        className=f"fw-bold {'text-danger' if hospitals_critical > 3 else 'text-warning'}"),
                html.Small(f"As of {latest_month}", className="text-muted"),
            ])
        ], className="shadow-sm border-0"), width=3),
    ], className="mb-4"),

    # ── Filters ───────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            html.Label("Filter by Regional Health Area:", className="fw-semibold"),
            dcc.Dropdown(
                id="rha-filter",
                options=[{"label": "All RHAs", "value": "All"}] +
                        [{"label": r, "value": r} for r in sorted(rha_summary["rha"].unique())],
                value="All",
                clearable=False,
                style={"fontSize": "14px"}
            )
        ], width=4),

        dbc.Col([
            html.Label("Select Year Range:", className="fw-semibold"),
            dcc.RangeSlider(
                id="year-slider",
                min=2021, max=2025, step=1, value=[2021, 2025],
                marks={y: str(y) for y in range(2021, 2026)},
            )
        ], width=8),
    ], className="mb-4 p-3 bg-light rounded"),

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 National Waiting List Trend (2021–2025)", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(id="national-trend-chart", style={"height": "320px"}))
            ], className="shadow-sm border-0")
        ], width=8),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🗺️ Total Waiting by RHA", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(id="rha-bar-chart", style={"height": "320px"}))
            ], className="shadow-sm border-0")
        ], width=4),
    ], className="mb-4"),

    # ── Charts Row 2 ──────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🏥 Hospital League Table — % Waiting Beyond Target", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(id="hospital-league-chart", style={"height": "350px"}))
            ], className="shadow-sm border-0")
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💳 GP Visit Card Coverage by RHA", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(id="gp-coverage-chart", style={"height": "350px"}))
            ], className="shadow-sm border-0")
        ], width=6),
    ], className="mb-4"),

    # ── Footer ────────────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col(html.P(
            "Data sources: NTPF Open Data (ntpf.ie) · HSE Open Data (data.ehealthireland.ie) · "
            "Licence: Open Government Licence (Ireland) · "
            "Built by Naresh Kumar Muttakoduru | github.com/Naresh9010/slaintecare-dashboard",
            className="text-muted text-center small mb-3"
        ))
    ])

], fluid=True)


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("national-trend-chart", "figure"),
    Input("year-slider", "value"),
)
def update_national_trend(year_range):
    df = national_trend[
        (national_trend["year"] >= year_range[0]) &
        (national_trend["year"] <= year_range[1])
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month_str"], y=df["total_waiting"],
        name="Total Waiting", line=dict(color="#005F87", width=2), fill="tozeroy",
        fillcolor="rgba(0,95,135,0.1)"
    ))
    fig.add_trace(go.Scatter(
        x=df["month_str"], y=df["waiting_beyond_target"],
        name="Beyond 12-Week Target", line=dict(color="#C8102E", width=2, dash="dash")
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title="Month", yaxis_title="Patients",
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    return fig


@app.callback(
    Output("rha-bar-chart", "figure"),
    Input("year-slider", "value"),
)
def update_rha_bar(year_range):
    df = rha_summary[
        (rha_summary["year"] >= year_range[0]) &
        (rha_summary["year"] <= year_range[1])
    ].groupby("rha")["total_waiting"].mean().reset_index().sort_values("total_waiting")

    fig = px.bar(
        df, x="total_waiting", y="rha", orientation="h",
        color="rha", color_discrete_map=RHA_COLORS,
    )
    fig.update_layout(
        showlegend=False, margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="Avg Monthly Patients", yaxis_title="",
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig


@app.callback(
    Output("hospital-league-chart", "figure"),
    [Input("rha-filter", "value"), Input("year-slider", "value")],
)
def update_hospital_league(rha, year_range):
    df = hospital_kpis[
        (hospital_kpis["year"] >= year_range[0]) &
        (hospital_kpis["year"] <= year_range[1])
    ]
    if rha != "All":
        df = df[df["rha"] == rha]

    top = (
        df.groupby("hospital")["avg_pct_beyond_target"]
        .mean().reset_index()
        .sort_values("avg_pct_beyond_target", ascending=False)
        .head(12)
    )

    fig = px.bar(
        top, x="avg_pct_beyond_target", y="hospital", orientation="h",
        color="avg_pct_beyond_target",
        color_continuous_scale=["#007A4D", "#FF8200", "#C8102E"],
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#888", annotation_text="Target")
    fig.update_layout(
        showlegend=False, coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis_title="% Waiting Beyond 12-Week Target", yaxis_title="",
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig


@app.callback(
    Output("gp-coverage-chart", "figure"),
    Input("year-slider", "value"),
)
def update_gp_coverage(year_range):
    df = gp_coverage.copy()
    df["year"] = pd.to_datetime(df["month"]).dt.year
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    fig = px.line(
        df, x="month", y="coverage_pct", color="rha",
        color_discrete_map=RHA_COLORS,
    )
    fig.add_hline(y=100, line_dash="dash", line_color="#C8102E",
                  annotation_text="Sláintecare Universal Target")
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=40),
        xaxis_title="Month", yaxis_title="GP Visit Card Coverage (%)",
        legend_title="RHA", plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    return fig


if __name__ == "__main__":
    print("🚀 Starting Sláintecare Dashboard...")
    print("   Open your browser at: http://localhost:8050")
    app.run(debug=True, port=8050)
