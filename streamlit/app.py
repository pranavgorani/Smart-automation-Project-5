"""
AIRFARE-X INDIA: Streamlit Dashboard.
Real-Time Airfare Price Intelligence & Index Platform for MoSPI / DIID.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

from backend.app.db.database import SessionLocal, init_db
from backend.app.models.index import IndexValue, RouteIndex, DataQualityLog, DGCAReferenceRecord
from backend.app.models.airfare import AirfareQuote
from backend.app.models.route import Route
from backend.app.analytics.elasticity import elasticity_analyzer
from backend.app.analytics.routes import route_analytics
from backend.app.analytics.trends import trend_analyzer
from backend.app.analytics.anomalies import anomaly_detector
from backend.app.index.backtest import backtest_engine
from backend.app.db.seed import run_full_seed
from backend.app.config import settings

st.set_page_config(
    page_title="AIRFARE-X INDIA | MoSPI Airfare Index",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Financial Terminal & MoSPI Government Theme)
st.markdown("""
<style>
    .main { background-color: #0B0F19; color: #F1F5F9; }
    .stMetric { background-color: #1E293B; border-radius: 8px; padding: 12px; border: 1px solid #334155; }
    .css-1d391kg { background-color: #0F172A; }
    h1, h2, h3 { color: #F8FAFC; }
    .banner { background: linear-gradient(90deg, #1E1B4B 0%, #312E81 100%); padding: 12px 18px; border-radius: 8px; border-left: 4px solid #6366F1; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_session():
    init_db()
    return SessionLocal()

db = get_db_session()

# Check and auto-seed if required
if db.query(AirfareQuote).count() < 1000:
    with st.spinner("Initializing and generating 10,000+ synthetic airfare observations..."):
        run_full_seed(db)

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=60)
st.sidebar.title("AIRFARE-X INDIA")
st.sidebar.caption("Ministry of Statistics & Programme Implementation (MoSPI)\nData Informatics & Innovation Division (DIID)")

# Demo Mode Indicator
if settings.is_demo_mode:
    st.sidebar.warning("🛡️ DEMO MODE ACTIVE\n(Synthetic observations enabled)")

nav = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Airfare Index (APIx)",
        "Route Explorer",
        "Lead-Time Analytics",
        "Airline Analytics",
        "Data Quality & Audit",
        "Backtesting & CPI Augmentation",
        "AI Insights & Anomalies",
        "Methodology",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("⚡ Run Full Demo Workflow"):
    with st.spinner("Executing one-click demo pipeline..."):
        run_full_seed(db)
        st.sidebar.success("✓ Demo dataset refreshed & indexed!")
        st.rerun()

# ------------------------------------------------------------------------------
# 1. Executive Overview
# ------------------------------------------------------------------------------
if nav == "Executive Overview":
    st.title("✈️ Real-Time Airfare Price Intelligence & Index Platform")
    st.markdown("""
    <div class="banner">
        <b>MoSPI / DIID Smart Automation Prototype</b>: Automated airfare collection across Indian domestic trunk routes 
        for high-frequency price tracking and potential augmentation of the Consumer Price Index (CPI) Transport group.
    </div>
    """, unsafe_allow_html=True)

    latest_idx = db.query(IndexValue).order_by(IndexValue.index_date.desc()).first()
    quote_count = db.query(AirfareQuote).count()
    route_count = db.query(Route).filter(Route.active == True).count()

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Current APIx", f"{latest_idx.index_value:.2f}" if latest_idx else "100.00", f"{latest_idx.daily_change:+.2f}% 24h")
    with col2:
        st.metric("7-Day Change", f"{latest_idx.weekly_change:+.2f}%" if latest_idx else "0.0%")
    with col3:
        st.metric("30-Day Change", f"{latest_idx.monthly_change:+.2f}%" if latest_idx else "0.0%")
    with col4:
        st.metric("Quotes Tracked", f"{quote_count:,}")
    with col5:
        st.metric("Quality Score", f"{latest_idx.confidence_score:.1f}%" if latest_idx else "95.0%")

    st.markdown("### 📈 30-Day Experimental Real-Time Airfare Price Index (APIx)")
    hist_records = db.query(IndexValue).order_by(IndexValue.index_date.asc()).all()
    if hist_records:
        df_hist = pd.DataFrame([r.to_dict() for r in hist_records])
        fig = px.line(
            df_hist,
            x="index_date",
            y="index_value",
            labels={"index_date": "Date", "index_value": "Index Level (Base=100)"},
            template="plotly_dark",
            title="Daily Movement in Experimental Real-Time Airfare Price Index",
        )
        fig.update_traces(line_color="#6366F1", line_width=3)
        fig.add_hline(y=100, line_dash="dash", line_color="#94A3B8", annotation_text="Base Period (100.0)")
        st.plotly_chart(fig, use_container_width=True)

    # Secondary Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Booking Horizon Gradient (T+1 to T+45)")
        lt_data = elasticity_analyzer.analyze_lead_time(db)
        df_lt = pd.DataFrame(lt_data["curve"])
        fig_lt = px.bar(
            df_lt,
            x="advance_window",
            y="median_fare",
            text="median_fare",
            template="plotly_dark",
            color="median_fare",
            color_continuous_scale="Viridis",
            labels={"advance_window": "Booking Window", "median_fare": "Median Fare (₹)"},
        )
        fig_lt.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_lt, use_container_width=True)

    with c2:
        st.subheader("Airline Comparative Distribution")
        airline_data = trend_analyzer.get_airline_analytics(db)
        df_air = pd.DataFrame(airline_data)
        fig_air = px.bar(
            df_air,
            x="airline",
            y="median_fare",
            color="airline",
            template="plotly_dark",
            labels={"airline": "Carrier", "median_fare": "Median Fare (₹)"},
        )
        st.plotly_chart(fig_air, use_container_width=True)

# ------------------------------------------------------------------------------
# 2. Airfare Index (APIx)
# ------------------------------------------------------------------------------
elif nav == "Airfare Index (APIx)":
    st.title("📊 Airfare Price Index (APIx) Time Series")
    st.caption("Laspeyres-type weighted relative price aggregation across Indian domestic trunk routes.")

    hist_records = db.query(IndexValue).order_by(IndexValue.index_date.desc()).all()
    if hist_records:
        df_all = pd.DataFrame([r.to_dict() for r in hist_records])
        st.dataframe(df_all, use_container_width=True)

        st.download_button(
            "⬇️ Export APIx Historical Series (CSV)",
            df_all.to_csv(index=False),
            "apix_historical_series.csv",
            "text/csv",
        )

# ------------------------------------------------------------------------------
# 3. Route Explorer
# ------------------------------------------------------------------------------
elif nav == "Route Explorer":
    st.title("🧭 Sector & Route Explorer")
    routes_list = [r.route_code for r in db.query(Route).all()]

    selected_route = st.selectbox("Select Trunk Route", ["ALL"] + routes_list)
    r_stats = route_analytics.get_route_details(
        db,
        origin=selected_route.split("-")[0] if selected_route != "ALL" else None,
        destination=selected_route.split("-")[1] if selected_route != "ALL" else None,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Median Fare", f"₹{r_stats['median_fare']:,.0f}")
    with k2:
        st.metric("Mean Fare", f"₹{r_stats['mean_fare']:,.0f}")
    with k3:
        st.metric("Min Fare", f"₹{r_stats['min_fare']:,.0f}")
    with k4:
        st.metric("Max Fare", f"₹{r_stats['max_fare']:,.0f}")

    if r_stats["airline_breakdown"]:
        st.subheader("Carrier Price Dispersion on Route")
        st.dataframe(pd.DataFrame(r_stats["airline_breakdown"]), use_container_width=True)

    # Route Heatmap
    st.markdown("---")
    st.subheader("🗺️ Sector Price Movement Heatmap")
    tf = st.selectbox("Comparison Timeframe", ["daily", "weekly", "monthly"])
    hm_res = route_analytics.get_route_heatmap(db, timeframe=tf)
    
    # Render table view of heatmap
    hm_data = []
    for r in hm_res["matrix"]:
        row_dict = {"Origin": r["origin"]}
        for dest, info in r["destinations"].items():
            chg = info.get("change_pct")
            row_dict[dest] = f"{chg:+.1f}%" if chg is not None else "—"
        hm_data.append(row_dict)
    st.dataframe(pd.DataFrame(hm_data).set_index("Origin"), use_container_width=True)

# ------------------------------------------------------------------------------
# 4. Lead-Time Analytics
# ------------------------------------------------------------------------------
elif nav == "Lead-Time Analytics":
    st.title("⏳ Advance Purchase & Lead-Time Elasticity")
    st.caption("Pricing dynamics across T+1 (emergency/last-minute), T+7, T+15, T+30, and T+45 (promotional baseline).")

    lt_res = elasticity_analyzer.analyze_lead_time(db)
    st.info(f"**Empirical Elasticity Estimate**: {lt_res['empirical_elasticity']} — {lt_res['interpretation']}")

    df_curve = pd.DataFrame(lt_res["curve"])
    st.dataframe(df_curve, use_container_width=True)

    fig = px.line(
        df_curve,
        x="advance_days",
        y="median_fare",
        markers=True,
        template="plotly_dark",
        labels={"advance_days": "Days to Departure (T+d)", "median_fare": "Median Airfare (₹)"},
        title="Advance Purchase Curve: Fare Progression as Departure Nears",
    )
    fig.update_traces(line_color="#10B981", line_width=3)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# 5. Airline Analytics
# ------------------------------------------------------------------------------
elif nav == "Airline Analytics":
    st.title("🛫 Airline Comparative Analytics")
    st.caption("Neutral statistical profile across carriers without subjective rankings.")

    airlines_res = trend_analyzer.get_airline_analytics(db)
    df_air = pd.DataFrame(airlines_res)
    st.dataframe(df_air, use_container_width=True)

    fig = px.scatter(
        df_air,
        x="median_fare",
        y="fare_volatility_pct",
        size="observations",
        color="airline",
        text="airline",
        template="plotly_dark",
        labels={"median_fare": "Median Fare (₹)", "fare_volatility_pct": "Fare Volatility (CV %)"},
        title="Fare Volatility vs Median Airfare by Carrier",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# 6. Data Quality & Audit
# ------------------------------------------------------------------------------
elif nav == "Data Quality & Audit":
    st.title("🛡️ Multi-Dimensional Data Quality Scorecard")
    st.caption("Rigorous compliance evaluation: Completeness (25%), Validity (20%), Timeliness (20%), Uniqueness (20%), Consistency (15%).")

    dq_log = db.query(DataQualityLog).order_by(DataQualityLog.id.desc()).first()
    if dq_log:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Overall Score", f"{dq_log.quality_score:.1f}%")
        with c2:
            st.metric("Completeness", f"{dq_log.completeness_score:.1f}%")
        with c3:
            st.metric("Validity", f"{dq_log.validity_score:.1f}%")
        with c4:
            st.metric("Timeliness", f"{dq_log.timeliness_score:.1f}%")
        with c5:
            st.metric("Uniqueness", f"{dq_log.uniqueness_score:.1f}%")

        st.markdown("### Audit Counts")
        st.write({
            "Records Valid": dq_log.records_valid,
            "Records Rejected": dq_log.records_rejected,
            "Duplicates Identified": dq_log.duplicates,
            "Outliers Flagged": dq_log.outliers,
        })

# ------------------------------------------------------------------------------
# 7. Backtesting & CPI Augmentation
# ------------------------------------------------------------------------------
elif nav == "Backtesting & CPI Augmentation":
    st.title("🔬 Prototype Validation / Back-Testing")
    st.caption("30-day econometric comparison between APIx and the benchmark DGCA monthly series.")

    bt_res = backtest_engine.run_backtest(db, days=30)
    m = bt_res["metrics"]

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        st.metric("MAE", f"{m['mae']:.2f}")
    with b2:
        st.metric("RMSE", f"{m['rmse']:.2f}")
    with b3:
        st.metric("MAPE", f"{m['mape']:.2f}%")
    with b4:
        st.metric("Correlation (r)", f"{m['correlation']:.3f}")
    with b5:
        st.metric("Directional Acc.", f"{m['directional_accuracy_pct']:.1f}%")

    # Plot APIx vs DGCA
    df_bt = pd.DataFrame(bt_res["series"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_bt["date"], y=df_bt["apix"], mode="lines+markers", name="Experimental APIx", line=dict(color="#6366F1", width=3)))
    fig.add_trace(go.Scatter(x=df_bt["date"], y=df_bt["dgca_reference"], mode="lines", name="DGCA Benchmark Series", line=dict(color="#10B981", width=2, dash="dash")))
    fig.update_layout(template="plotly_dark", title="APIx vs DGCA Benchmark Airfare Trajectory", xaxis_title="Date", yaxis_title="Index Level")
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------------
# 8. AI Insights & Anomalies
# ------------------------------------------------------------------------------
elif nav == "AI Insights & Anomalies":
    st.title("🤖 AI Grounded Anomaly Detection & MoSPI Briefing")

    summary = anomaly_detector.generate_mospi_executive_summary(db)
    st.subheader("Executive Briefing for MoSPI Leadership")
    st.markdown(f"**{summary['headline']}**")
    for t in summary["takeaways"]:
        st.markdown(f"- {t}")

    st.markdown("---")
    st.subheader("Detected Sector Price Spikes (>25%) with Grounded Explanations")
    anomalies = anomaly_detector.detect_route_anomalies(db, threshold_pct=25.0)
    if anomalies:
        for a in anomalies:
            with st.expander(f"Sector {a['route']} ({a['change_pct']:+.1f}%) on {a['date']}"):
                st.write(a["ai_explanation"]["summary"])
                st.caption(f"Factors: {', '.join(a['ai_explanation']['grounded_factors'])}")
    else:
        st.info("No extreme sector fare movements (>25%) detected in the latest observation run.")

# ------------------------------------------------------------------------------
# 9. Methodology
# ------------------------------------------------------------------------------
elif nav == "Methodology":
    st.title("📐 Statistical Methodology")
    from backend.app.index.methodology import get_methodology_spec
    spec = get_methodology_spec()
    st.json(spec)
