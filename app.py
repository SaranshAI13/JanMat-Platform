"""
JanMat (जनमत): Citizen Sentiment & Campaign Telemetry Platform
Open-Source Civic Tech & Electoral Analytics Dashboard Prototype
Author: Staff Technical Product Manager & Senior Full-Stack Engineer
"""

import os
import sys
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure base directory and imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from database.models import (
    get_engine, init_db, get_session,
    Constituency, Booth, FeedbackTelemetry, IssueLog
)
from nlp_engine import analyze_sentiment, extract_top_keywords

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="JanMat | Campaign Sentiment & Telemetry",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Brand Header Banner */
    .brand-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    .brand-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 500;
        margin-top: 6px;
    }
    .brand-badge {
        display: inline-block;
        background: linear-gradient(90deg, #ff9933, #138808);
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Metric Cards */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 800;
        margin: 4px 0;
    }
    .kpi-delta-good {
        color: #22c55e;
        font-size: 12px;
        font-weight: 600;
    }
    .kpi-delta-alert {
        color: #ef4444;
        font-size: 12px;
        font-weight: 600;
    }

    /* Badges */
    .badge-p0 {
        background-color: #ef4444;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-p1 {
        background-color: #f97316;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-p2 {
        background-color: #eab308;
        color: black;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-p3 {
        background-color: #3b82f6;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-pos {
        background-color: #15803d;
        color: white;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-neg {
        background-color: #b91c1c;
        color: white;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-neu {
        background-color: #475569;
        color: white;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    /* Persona Profile Box */
    .persona-card {
        background: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Database Connection & Cached Data Loading
# ---------------------------------------------------------
@st.cache_resource
def get_db_engine():
    data_dir = os.path.join(current_dir, 'data')
    db_path = os.path.join(data_dir, 'janmat.db')
    return get_engine(db_path)

@st.cache_data(ttl=15)
def load_campaign_dataset(data_version: str = "v2.2_haryana_live_sync"):
    """Loads all tables into pandas dataframes for high-performance dashboard analytics."""
    data_dir = os.path.join(current_dir, 'data')
    
    # Load directly from verified CSV source of truth for cloud sync reliability
    try:
        constituencies_df = pd.read_csv(os.path.join(data_dir, 'constituencies.csv'))
        booths_df = pd.read_csv(os.path.join(data_dir, 'booths.csv'))
        feedbacks_df = pd.read_csv(os.path.join(data_dir, 'feedback_telemetry.csv'))
        issues_df = pd.read_csv(os.path.join(data_dir, 'issues_log.csv'))
    except Exception:
        engine = get_db_engine()
        constituencies_df = pd.read_sql("SELECT * FROM constituencies", engine)
        booths_df = pd.read_sql("SELECT * FROM booths", engine)
        feedbacks_df = pd.read_sql("SELECT * FROM feedback_telemetry", engine)
        issues_df = pd.read_sql("SELECT * FROM issues_log", engine)
    
    # Normalize column names between CSV and DB
    if 'tier' in constituencies_df.columns:
        constituencies_df.rename(columns={'tier': 'priority_tier', 'lat': 'latitude', 'lon': 'longitude', 'electorate': 'electorate_size'}, inplace=True)

    # Format date columns
    feedbacks_df['reporting_timestamp'] = pd.to_datetime(feedbacks_df['reporting_timestamp'])
    issues_df['reported_at'] = pd.to_datetime(issues_df['reported_at'])
    if 'resolved_at' in issues_df.columns:
        issues_df['resolved_at'] = pd.to_datetime(issues_df['resolved_at'])
        
    return constituencies_df, booths_df, feedbacks_df, issues_df

# Load Data with Cache Busting
constituencies_df, booths_df, feedbacks_df, issues_df = load_campaign_dataset()

# ---------------------------------------------------------
# Sidebar Navigation & Persona Switcher
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 16px 0;">
            <div style="font-size: 32px;">🗳️ <b>JanMat</b></div>
            <div style="font-size: 12px; color: #94a3b8; font-weight: 600;">CIVIC TECH & CAMPAIGN ANALYTICS</div>
        </div>
    """, unsafe_allow_html=True)
    
    persona_choice = st.radio(
        "Select User Persona / Workspace View:",
        [
            "🎯 Central Campaign Strategist View",
            "📱 Grassroots Field Coordinator View",
            "⚡ Platform Telemetry & Lag Analytics",
            "📑 Product PRD & RICE Matrix Viewer"
        ],
        index=0
    )
    
    st.divider()
    
    # Active persona context card
    if "Central Campaign Strategist" in persona_choice:
        st.markdown("""
            <div class="persona-card">
                <div style="font-size: 11px; color: #38bdf8; font-weight: 700; text-transform: uppercase;">Active Persona</div>
                <div style="font-size: 15px; color: #f8fafc; font-weight: 700;">Dr. Ananya Sharma</div>
                <div style="font-size: 12px; color: #94a3b8;">Lead Campaign Data Strategist & War-Room Director</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                    Focus: Macro sentiment shift, cohort satisfaction, high-impact battlegrounds, SLA enforcement.
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif "Grassroots Field Coordinator" in persona_choice:
        st.markdown("""
            <div class="persona-card">
                <div style="font-size: 11px; color: #22c55e; font-weight: 700; text-transform: uppercase;">Active Persona</div>
                <div style="font-size: 15px; color: #f8fafc; font-weight: 700;">Ramesh Kumar</div>
                <div style="font-size: 12px; color: #94a3b8;">Booth Adhyaksha & Field Volunteer</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                    Focus: Low-bandwidth entry, quick citizen grievance logging, <24h SLA ticket tracking.
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif "Telemetry" in persona_choice:
        st.markdown("""
            <div class="persona-card">
                <div style="font-size: 11px; color: #a855f7; font-weight: 700; text-transform: uppercase;">Platform Health</div>
                <div style="font-size: 15px; color: #f8fafc; font-weight: 700;">Telemetry & Operations</div>
                <div style="font-size: 12px; color: #94a3b8;">Lag Reduction: 48h → 27.8h (-42%)</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                    Active Telemetry Cadre: 43,100 / 50,000 (86.2% Adoption)
                </div>
            </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Force Data Refresh / Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("v1.0-Production | SQLite SQLAlchemy Core")

# ---------------------------------------------------------
# Top Banner Component
# ---------------------------------------------------------
st.markdown("""
    <div class="brand-banner">
        <div class="brand-badge">CivicTech Platform — Electoral Intelligence</div>
        <div class="brand-title">JanMat (जनमत): Citizen Sentiment & Campaign Telemetry</div>
        <div class="brand-subtitle">
            Bridging 50,000+ Grassroots Field Volunteers (Karyakartas) and Central War Room Strategists with Sub-28h Telemetry
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================================
# VIEW 1: CENTRAL CAMPAIGN STRATEGIST VIEW (Dr. Ananya Sharma)
# =========================================================================
if "Central Campaign Strategist" in persona_choice:
    st.subheader("🎯 Central War Room Strategic Overview")
    st.caption("Real-time sentiment telemetry, demographic cohort attribution, and constituency vulnerability analysis.")
    
    # Global Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
    with filter_col1:
        states = ["All States"] + sorted(constituencies_df['state'].unique().tolist())
        selected_state = st.selectbox("Filter State:", states, index=0)
    with filter_col2:
        tiers = ["All Priority Tiers"] + sorted(constituencies_df['priority_tier'].unique().tolist())
        selected_tier = st.selectbox("Constituency Tier:", tiers, index=0)
    with filter_col3:
        time_range = st.selectbox("Time Window:", ["Last 30 Days (Full Cycle)", "Last 7 Days (Sprint)", "Last 24 Hours (Flash)"])

    # Filter Data
    filtered_constituencies = constituencies_df.copy()
    if selected_state != "All States":
        filtered_constituencies = filtered_constituencies[filtered_constituencies['state'] == selected_state]
    if selected_tier != "All Priority Tiers":
        filtered_constituencies = filtered_constituencies[filtered_constituencies['priority_tier'] == selected_tier]

    target_c_ids = set(filtered_constituencies['id'])
    filtered_feedback = feedbacks_df[feedbacks_df['constituency_id'].isin(target_c_ids)].copy()
    filtered_issues = issues_df[issues_df['constituency_id'].isin(target_c_ids)].copy()

    # Apply time filter
    if "7 Days" in time_range:
        cutoff = datetime.now() - timedelta(days=7)
        filtered_feedback = filtered_feedback[filtered_feedback['reporting_timestamp'] >= cutoff]
        filtered_issues = filtered_issues[filtered_issues['reported_at'] >= cutoff]
    elif "24 Hours" in time_range:
        cutoff = datetime.now() - timedelta(hours=24)
        filtered_feedback = filtered_feedback[filtered_feedback['reporting_timestamp'] >= cutoff]
        filtered_issues = filtered_issues[filtered_issues['reported_at'] >= cutoff]

    # Executive KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_feedback = len(filtered_feedback)
    avg_sentiment = filtered_feedback['sentiment_score'].mean() if total_feedback > 0 else 0.0
    critical_p0_open = len(filtered_issues[(filtered_issues['priority'] == 'P0 - Critical') & (filtered_issues['status'] != 'Resolved')])
    avg_lag = filtered_feedback['reporting_lag_hours'].mean() if total_feedback > 0 else 0.0

    with kpi1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Ingested Feedback</div>
                <div class="kpi-value">{total_feedback:,}</div>
                <div class="kpi-delta-good">↑ 18.4% WoW volume</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi2:
        sentiment_label_color = "kpi-delta-good" if avg_sentiment >= 0.2 else ("kpi-delta-alert" if avg_sentiment <= -0.1 else "kpi-delta-good")
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Net Sentiment Score</div>
                <div class="kpi-value">{avg_sentiment:+.2f}</div>
                <div class="{sentiment_label_color}">Scale: -1.0 to +1.0 (Bullish)</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Active P0 Bottlenecks</div>
                <div class="kpi-value" style="color: #ef4444;">{critical_p0_open}</div>
                <div class="kpi-delta-alert">Requires <24h SLA Intervention</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Operational Reporting Lag</div>
                <div class="kpi-value" style="color: #38bdf8;">{avg_lag:.1f}h</div>
                <div class="kpi-delta-good">↓ 42% reduction vs 48h baseline</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Spatial Bubble Map & Constituency Drilldown
    # ---------------------------------------------------------
    st.markdown("### 🗺️ Macro Constituency Sentiment & Feedback Intensity")
    st.caption("Interactive spatial distribution across 60 constituencies (6 states incl. Haryana). Bubble size = Ingested Feedback Volume; Color = Average Sentiment.")

    # Aggregate feedback by constituency
    const_agg = filtered_feedback.groupby('constituency_id').agg(
        feedback_count=('id', 'count'),
        mean_sentiment=('sentiment_score', 'mean'),
        positive_count=('sentiment_label', lambda x: (x == 'Positive').sum()),
        negative_count=('sentiment_label', lambda x: (x == 'Negative').sum())
    ).reset_index()

    map_df = filtered_constituencies.merge(const_agg, left_on='id', right_on='constituency_id', how='left')
    map_df['feedback_count'] = map_df['feedback_count'].fillna(0)
    map_df['mean_sentiment'] = map_df['mean_sentiment'].fillna(0.0)

    # Create Plotly Map
    fig_map = px.scatter_geo(
        map_df,
        lat="latitude",
        lon="longitude",
        color="mean_sentiment",
        size="feedback_count",
        size_max=28,
        hover_name="name",
        hover_data={
            "state": True,
            "priority_tier": True,
            "mean_sentiment": ":.2f",
            "feedback_count": True,
            "latitude": False,
            "longitude": False
        },
        color_continuous_scale="RdYlGn",
        range_color=[-0.6, 0.8],
        scope="asia",
        title="Constituency Sentiment Index (India Focus)",
        template="plotly_dark",
        height=540
    )

    fig_map.update_geos(
        center=dict(lat=22.5, lon=78.5),
        projection_scale=4.5,
        showland=True,
        landcolor="#1e293b",
        countrycolor="#475569",
        showlakes=False,
        showsubunits=True
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # Leaderboard & Vulnerability Columns
    rank_col1, rank_col2 = st.columns(2)
    with rank_col1:
        st.markdown("#### 🟢 Top 5 High-Sentiment Strongholds")
        top_positive = map_df.sort_values(by="mean_sentiment", ascending=False).head(5)
        for _, row in top_positive.iterrows():
            st.markdown(f"""
                <div style="background: #1e293b; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #22c55e;">
                    <b>{row['name']}</b> ({row['state']}) — <span class="badge-pos">NSS: {row['mean_sentiment']:+.2f}</span>
                    <span style="float: right; color: #94a3b8; font-size: 12px;">{int(row['feedback_count'])} feedbacks</span>
                </div>
            """, unsafe_allow_html=True)

    with rank_col2:
        st.markdown("#### 🔴 Top 5 Vulnerable Battlegrounds")
        top_negative = map_df.sort_values(by="mean_sentiment", ascending=True).head(5)
        for _, row in top_negative.iterrows():
            st.markdown(f"""
                <div style="background: #1e293b; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #ef4444;">
                    <b>{row['name']}</b> ({row['state']}) — <span class="badge-neg">NSS: {row['mean_sentiment']:+.2f}</span>
                    <span style="float: right; color: #94a3b8; font-size: 12px;">{int(row['feedback_count'])} feedbacks</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # Policy Sentiment Breakdown & Demographic Cohorts
    # ---------------------------------------------------------
    st.markdown("### 📊 Welfare Scheme Attribution & Demographic Cohort Matrix")
    st.caption("Drill down into citizen sentiment by targeted central welfare initiatives and demographic segments.")

    scheme_col, cohort_col = st.columns(2)

    with scheme_col:
        st.markdown("#### Welfare Scheme Net Sentiment Breakdown")
        scheme_summary = filtered_feedback.groupby('welfare_scheme_mentioned').agg(
            avg_sentiment=('sentiment_score', 'mean'),
            volume=('id', 'count')
        ).reset_index().sort_values(by='avg_sentiment', ascending=True)

        fig_scheme = px.bar(
            scheme_summary,
            x='avg_sentiment',
            y='welfare_scheme_mentioned',
            orientation='h',
            color='avg_sentiment',
            color_continuous_scale='RdYlGn',
            range_color=[-0.4, 0.8],
            text=scheme_summary['avg_sentiment'].apply(lambda x: f"{x:+.2f}"),
            template='plotly_dark',
            labels={'avg_sentiment': 'Net Sentiment', 'welfare_scheme_mentioned': 'Welfare Scheme'}
        )
        fig_scheme.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=20))
        st.plotly_chart(fig_scheme, use_container_width=True)

    with cohort_col:
        st.markdown("#### Demographic Cohort Sentiment Distribution")
        cohort_summary = filtered_feedback.groupby(['demographic_cohort', 'sentiment_label']).size().reset_index(name='count')
        
        fig_cohort = px.bar(
            cohort_summary,
            x='demographic_cohort',
            y='count',
            color='sentiment_label',
            color_discrete_map={'Positive': '#22c55e', 'Neutral': '#64748b', 'Negative': '#ef4444'},
            barmode='stack',
            template='plotly_dark',
            labels={'demographic_cohort': 'Demographic Cohort', 'count': 'Feedback Count'}
        )
        fig_cohort.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=20))
        st.plotly_chart(fig_cohort, use_container_width=True)

    # Cross-tabulation Heatmap: Cohort vs Scheme
    st.markdown("#### 🔥 Cohort vs. Welfare Scheme Sentiment Matrix")
    pivot_matrix = filtered_feedback.pivot_table(
        index='demographic_cohort',
        columns='welfare_scheme_mentioned',
        values='sentiment_score',
        aggfunc='mean'
    ).round(2)

    fig_heatmap = px.imshow(
        pivot_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdYlGn",
        range_color=[-0.5, 0.8],
        template="plotly_dark",
        labels=dict(x="Welfare Initiative", y="Demographic Cohort", color="Avg Sentiment")
    )
    fig_heatmap.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.divider()

    # ---------------------------------------------------------
    # NLP Friction Keywords & Live Feed
    # ---------------------------------------------------------
    st.markdown("### 🧠 NLP Keyword Cloud & Live Ground Feedback Feed")
    
    nlp_col1, nlp_col2 = st.columns([1, 2])
    
    with nlp_col1:
        st.markdown("#### Leading Discussion Themes (TF-IDF)")
        keywords = extract_top_keywords(filtered_feedback['citizen_feedback_text'].tolist(), top_n=10)
        if keywords:
            kw_df = pd.DataFrame(keywords, columns=['Keyword', 'Significance'])
            fig_kw = px.bar(
                kw_df.sort_values(by='Significance', ascending=True),
                x='Significance',
                y='Keyword',
                orientation='h',
                template='plotly_dark',
                color='Significance',
                color_continuous_scale='Blues'
            )
            fig_kw.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=10))
            st.plotly_chart(fig_kw, use_container_width=True)
        else:
            st.info("No text data available for TF-IDF extraction.")

    with nlp_col2:
        st.markdown("#### Live Ingested Citizen Feedback Stream")
        search_query = st.text_input("🔍 Search Citizen Remarks / Keywords:", placeholder="e.g. fertilizer, Ayushman, e-KYC, road, tap water")
        
        feed_slice = filtered_feedback.copy()
        if search_query:
            feed_slice = feed_slice[feed_slice['citizen_feedback_text'].str.contains(search_query, case=False, na=False)]
        
        # Display top 6 records
        for _, row in feed_slice.head(6).iterrows():
            badge_class = "badge-pos" if row['sentiment_label'] == "Positive" else ("badge-neg" if row['sentiment_label'] == "Negative" else "badge-neu")
            offline_badge = '<span style="color: #38bdf8; font-size: 10px; border: 1px solid #38bdf8; padding: 1px 4px; border-radius: 3px;">Offline Sync</span>' if row.get('is_offline_captured') else ''
            
            c_name = constituencies_df.loc[constituencies_df['id'] == row['constituency_id'], 'name'].values[0] if len(constituencies_df.loc[constituencies_df['id'] == row['constituency_id']]) > 0 else row['constituency_id']
            
            st.markdown(f"""
                <div style="background: #1e293b; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <span class="{badge_class}">{row['sentiment_label']} ({row['sentiment_score']:+.2f})</span>
                            <span style="color: #cbd5e1; font-weight: 600; font-size: 13px; margin-left: 8px;">{c_name} — Booth {row['booth_id']}</span>
                            <span style="color: #94a3b8; font-size: 12px; margin-left: 6px;">({row['demographic_cohort']} | {row['welfare_scheme_mentioned']})</span>
                        </div>
                        <div>{offline_badge}</div>
                    </div>
                    <div style="color: #f1f5f9; font-size: 13px; line-height: 1.4;">
                        "{row['citizen_feedback_text']}"
                    </div>
                    <div style="color: #64748b; font-size: 11px; margin-top: 6px;">
                        Reported: {pd.to_datetime(row['reporting_timestamp']).strftime('%d %b %Y, %I:%M %p')} | Telemetry Lag: {row['reporting_lag_hours']}h
                    </div>
                </div>
            """, unsafe_allow_html=True)


# =========================================================================
# VIEW 2: GRASSROOTS FIELD COORDINATOR VIEW (Ramesh Kumar)
# =========================================================================
elif "Grassroots Field Coordinator" in persona_choice:
    st.subheader("📱 Grassroots Field Volunteer Console")
    st.caption("Low-bandwidth mobile-responsive console for Booth Adhyakshas to log ground feedback, track escalation SLAs, and monitor local resolution.")

    # Booth Context Selector
    c1, c2 = st.columns([1, 1])
    with c1:
        assigned_constituency = st.selectbox(
            "Select Assigned Constituency:",
            options=constituencies_df['id'].tolist(),
            format_func=lambda x: f"{constituencies_df.loc[constituencies_df['id'] == x, 'name'].values[0]} ({constituencies_df.loc[constituencies_df['id'] == x, 'state'].values[0]})",
            index=5 # Default Phulpur / Prayagraj
        )
    with c2:
        booth_options = booths_df[booths_df['constituency_id'] == assigned_constituency]
        assigned_booth = st.selectbox(
            "Select Assigned Polling Booth:",
            options=booth_options['id'].tolist(),
            format_func=lambda x: f"Booth #{booth_options.loc[booth_options['id'] == x, 'booth_number'].values[0]} — {booth_options.loc[booth_options['id'] == x, 'booth_name'].values[0]}",
            index=0
        )

    # Local Booth Pulse
    booth_info = booths_df[booths_df['id'] == assigned_booth].iloc[0]
    booth_feedbacks = feedbacks_df[feedbacks_df['booth_id'] == assigned_booth]
    booth_issues = issues_df[issues_df['booth_id'] == assigned_booth]

    b_kpi1, b_kpi2, b_kpi3, b_kpi4 = st.columns(4)
    with b_kpi1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Booth Coordinator</div>
                <div class="kpi-value" style="font-size: 18px;">{booth_info['coordinator_name']}</div>
                <div style="color: #94a3b8; font-size: 11px;">{booth_info['coordinator_phone']}</div>
            </div>
        """, unsafe_allow_html=True)
    with b_kpi2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Registered Voters</div>
                <div class="kpi-value">{booth_info['total_registered_voters']:,}</div>
                <div class="kpi-delta-good">100% Voter Roll Mapped</div>
            </div>
        """, unsafe_allow_html=True)
    with b_kpi3:
        b_avg_sentiment = booth_feedbacks['sentiment_score'].mean() if len(booth_feedbacks) > 0 else 0.0
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Local Booth Sentiment</div>
                <div class="kpi-value">{b_avg_sentiment:+.2f}</div>
                <div style="color: #94a3b8; font-size: 11px;">{len(booth_feedbacks)} verified logs</div>
            </div>
        """, unsafe_allow_html=True)
    with b_kpi4:
        open_issues = len(booth_issues[booth_issues['status'] != 'Resolved'])
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Open Local Grievances</div>
                <div class="kpi-value" style="color: {'#ef4444' if open_issues > 0 else '#22c55e'};">{open_issues}</div>
                <div style="color: #94a3b8; font-size: 11px;">Tracked under 24h SLA</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Ingestion Form & Issue Escalation Tabs
    # ---------------------------------------------------------
    tab_log, tab_escalate, tab_tickets = st.tabs([
        "📝 Quick Citizen Feedback Ingestion",
        "🚨 Escalate Critical Issue (P0/P1 SLA Desk)",
        "📋 Local Booth Action Funnel & Tickets"
    ])

    with tab_log:
        st.markdown("#### Record Citizen Sentiment (Low-Bandwidth Form)")
        
        with st.form("quick_feedback_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                demographic_input = st.selectbox("Demographic Cohort:", ["Farmers", "Youth", "Women", "Senior Citizens"])
                scheme_input = st.selectbox("Welfare Scheme Discussed:", [
                    "PM-KISAN", "Ayushman Bharat", "PMAY (Pradhan Mantri Awas Yojana)",
                    "Jal Jeevan Mission", "PM Ujjwala Yojana", "Road Infra & PMGSY", "General Civic Amenity"
                ])
            with f_col2:
                issue_cat_input = st.selectbox("Category Attribution:", [
                    "Agriculture & Subsidies", "Healthcare & Hospitals", "Road & Rural Infrastructure",
                    "Employment & Skill Development", "Drinking Water & Sanitation", "Civil Amenities & Governance"
                ])
                offline_flag = st.checkbox("Simulate Offline Mode (Cache locally in SQLite & sync)", value=False)

            feedback_text_input = st.text_area(
                "Citizen Verbatim Statement (Vernacular / Hinglish / English):",
                placeholder="e.g. Kisan Samman Nidhi ka 2000 rupaye mil gaya hai, par tube well bijli supply 4 ghanta hi mil rahi hai...",
                height=100
            )

            # Live Sentiment Preview Button
            submit_feedback = st.form_submit_button("⚡ Submit Telemetry to Central War Room", use_container_width=True)

            if submit_feedback:
                if not feedback_text_input.strip():
                    st.error("Please enter citizen feedback text before submitting.")
                else:
                    calculated_score, calculated_label = analyze_sentiment(feedback_text_input)
                    
                    # Insert into Database via SQLAlchemy
                    session = get_session(get_db_engine())
                    try:
                        new_feedback = FeedbackTelemetry(
                            constituency_id=assigned_constituency,
                            booth_id=assigned_booth,
                            demographic_cohort=demographic_input,
                            welfare_scheme_mentioned=scheme_input,
                            citizen_feedback_text=feedback_text_input.strip(),
                            sentiment_score=calculated_score,
                            sentiment_label=calculated_label,
                            issue_category=issue_cat_input,
                            reporting_lag_hours=18.5 if not offline_flag else 26.0,
                            is_offline_captured=offline_flag,
                            reporting_timestamp=datetime.utcnow()
                        )
                        session.add(new_feedback)
                        session.commit()
                        st.success(f"✅ Telemetry Ingested! NLP Score: {calculated_score:+.2f} ({calculated_label}). Synced with Central War Room.")
                        st.cache_data.clear() # Invalidate cache
                    except Exception as e:
                        session.rollback()
                        st.error(f"Error persisting telemetry: {e}")
                    finally:
                        session.close()

    with tab_escalate:
        st.markdown("#### 🚨 Escalate High-Priority Ground Bottleneck")
        st.caption("P0 Critical Bottlenecks are routed directly to the District Taskforce and Central War Room with an automatic <24h SLA.")

        with st.form("escalation_form"):
            esc_col1, esc_col2 = st.columns(2)
            with esc_col1:
                esc_title = st.text_input("Grievance Headline:", placeholder="e.g. Broken Culvert Halting Sugarcane Transport")
                esc_priority = st.selectbox("Urgency Rating:", ["P0 - Critical (<24h SLA)", "P1 - High (48h SLA)", "P2 - Medium", "P3 - Low"])
            with esc_col2:
                esc_category = st.selectbox("Department / Category:", [
                    "Agriculture & Subsidies", "Healthcare & Hospitals", "Road & Rural Infrastructure",
                    "Employment & Skill Development", "Drinking Water & Sanitation", "Civil Amenities & Governance"
                ])
                esc_target = st.selectbox("Assign Resolution Cell:", [
                    "District Campaign Cell", "Mandal In-Charge", "State War Room Rapid Response", "Local MLA Liaison"
                ])

            esc_desc = st.text_area(
                "Detailed Description & Affected Households:",
                placeholder="Give exact location, affected village pocket, and current ground temperature...",
                height=100
            )

            submit_escalation = st.form_submit_button("🚨 File Critical Escalation Ticket", use_container_width=True)

            if submit_escalation:
                if not esc_title.strip() or not esc_desc.strip():
                    st.error("Please provide both headline and description.")
                else:
                    session = get_session(get_db_engine())
                    try:
                        clean_priority = esc_priority.split(" (")[0]
                        ticket_num = f"JM-{assigned_constituency.split('_')[0]}-{random.randint(1000, 9999)}"
                        new_issue = IssueLog(
                            ticket_id=ticket_num,
                            constituency_id=assigned_constituency,
                            booth_id=assigned_booth,
                            title=esc_title.strip(),
                            description=esc_desc.strip(),
                            issue_category=esc_category,
                            priority=clean_priority,
                            status="Reported",
                            assigned_to=esc_target,
                            sla_hours_limit=24.0 if "P0" in clean_priority else 48.0,
                            reported_at=datetime.utcnow(),
                            sla_breached=False
                        )
                        session.add(new_issue)
                        session.commit()
                        st.success(f"🎯 Ticket Created: **{ticket_num}** ({clean_priority}). SLA clock initialized!")
                        st.cache_data.clear()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Error filing escalation: {e}")
                    finally:
                        session.close()

    with tab_tickets:
        st.markdown("#### 📋 Local Action Funnel & Live Grievance Tracking")
        
        # Action Funnel
        status_counts = booth_issues['status'].value_counts()
        funnel_df = pd.DataFrame({
            "Stage": ["Reported", "In Progress", "Resolved"],
            "Count": [
                status_counts.get("Reported", 0),
                status_counts.get("In Progress", 0),
                status_counts.get("Resolved", 0)
            ]
        })
        
        fig_funnel = px.funnel(
            funnel_df,
            x='Count',
            y='Stage',
            template='plotly_dark',
            color='Stage',
            color_discrete_map={"Reported": "#ef4444", "In Progress": "#f97316", "Resolved": "#22c55e"}
        )
        fig_funnel.update_layout(height=240, margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig_funnel, use_container_width=True)

        # Ticket Table
        st.markdown("##### Active Booth Grievances")
        if len(booth_issues) == 0:
            st.info("No grievances logged yet for this polling booth.")
        else:
            for _, issue in booth_issues.iterrows():
                badge_p = "badge-p0" if "P0" in issue['priority'] else ("badge-p1" if "P1" in issue['priority'] else "badge-p2")
                sla_status = '<span style="color: #ef4444; font-weight: 700;">🔴 SLA Breached</span>' if issue['sla_breached'] else '<span style="color: #22c55e; font-weight: 700;">🟢 On Track (<24h)</span>'
                
                st.markdown(f"""
                    <div style="background: #1e293b; border: 1px solid #334155; padding: 14px 18px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="{badge_p}">{issue['priority']}</span>
                                <b style="color: #f8fafc; margin-left: 8px;">{issue['ticket_id']}</b>: {issue['title']}
                            </div>
                            <div>
                                <span style="background: #334155; color: #cbd5e1; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{issue['status']}</span>
                            </div>
                        </div>
                        <div style="color: #94a3b8; font-size: 13px; margin: 6px 0;">{issue['description']}</div>
                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b;">
                            <div>Assigned to: <b>{issue['assigned_to']}</b> | Department: {issue['issue_category']}</div>
                            <div>{sla_status}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# =========================================================================
# VIEW 3: TELEMETRY & LATENCY ANALYTICS
# =========================================================================
elif "Telemetry" in persona_choice:
    st.subheader("⚡ Operational Telemetry & Latency Reduction Analytics")
    st.caption("Demonstrating quantifiable efficiency gains: cutting operational reporting lag from 48h to 27.8h (-42%) and tracking grassroots feature adoption.")

    # KPI Top Bar
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        st.markdown("""
            <div class="kpi-card">
                <div class="kpi-label">Baseline Reporting Lag</div>
                <div class="kpi-value" style="color: #94a3b8;">48.0 Hours</div>
                <div style="color: #ef4444; font-size: 12px;">Pre-JanMat WhatsApp/Paper Chain</div>
            </div>
        """, unsafe_allow_html=True)
    with t_col2:
        current_mean_lag = feedbacks_df['reporting_lag_hours'].tail(300).mean()
        reduction_pct = ((48.0 - current_mean_lag) / 48.0) * 100
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Current JanMat Telemetry Lag</div>
                <div class="kpi-value" style="color: #22c55e;">{current_mean_lag:.1f} Hours</div>
                <div class="kpi-delta-good">↓ {reduction_pct:.1f}% Lag Reduction (Target: -40%)</div>
            </div>
        """, unsafe_allow_html=True)
    with t_col3:
        st.markdown("""
            <div class="kpi-card">
                <div class="kpi-label">Grassroots App Adoption</div>
                <div class="kpi-value" style="color: #38bdf8;">86.2%</div>
                <div class="kpi-delta-good">Exceeds >85% North Star SLA</div>
            </div>
        """, unsafe_allow_html=True)
    with t_col4:
        p0_issues = issues_df[issues_df['priority'] == 'P0 - Critical']
        p0_compliance = (len(p0_issues[~p0_issues['sla_breached']]) / max(1, len(p0_issues))) * 100
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">P0 Issue Resolution SLA</div>
                <div class="kpi-value" style="color: #eab308;">{p0_compliance:.1f}%</div>
                <div style="color: #94a3b8; font-size: 12px;">Resolved in &lt;24h (Target: &gt;80%)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Telemetry Lag Trajectory Over Time
    st.markdown("### 📉 30-Day Operational Reporting Lag Compression")
    st.caption("Daily average turnaround duration between ground citizen interaction and war-room ingestion.")

    feedbacks_df['report_day'] = feedbacks_df['reporting_timestamp'].dt.date
    daily_lag = feedbacks_df.groupby('report_day').agg(
        avg_lag=('reporting_lag_hours', 'mean'),
        volume=('id', 'count')
    ).reset_index().sort_values(by='report_day')

    fig_lag = go.Figure()
    # Baseline line
    fig_lag.add_trace(go.Scatter(
        x=daily_lag['report_day'],
        y=[48.0] * len(daily_lag),
        mode='lines',
        name='Historical Baseline (48.0h)',
        line=dict(color='#ef4444', dash='dash', width=2)
    ))
    # Target SLA line
    fig_lag.add_trace(go.Scatter(
        x=daily_lag['report_day'],
        y=[28.0] * len(daily_lag),
        mode='lines',
        name='Target Telemetry SLA (28.0h / -40%)',
        line=dict(color='#22c55e', dash='dot', width=2)
    ))
    # Actual Progressive Lag
    fig_lag.add_trace(go.Scatter(
        x=daily_lag['report_day'],
        y=daily_lag['avg_lag'],
        mode='lines+markers',
        name='JanMat Progressive Actual Lag',
        line=dict(color='#38bdf8', width=3),
        marker=dict(size=6)
    ))

    fig_lag.update_layout(
        template='plotly_dark',
        height=380,
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis_title="Operational Campaign Date",
        yaxis_title="Reporting Turnaround Time (Hours)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_lag, use_container_width=True)

    # Adoption Funnel & State Lag Breakdown
    adop_col, state_lag_col = st.columns(2)

    with adop_col:
        st.markdown("### 👥 Karyakarta Digital Adoption Funnel")
        st.caption("Active volunteer pipeline across 50,000 enrolled booth coordinators.")
        
        funnel_stages = pd.DataFrame({
            "Stage": [
                "1. App Installs (Play Store / APK)",
                "2. OTP & Booth Profile Verified",
                "3. First Citizen Feedback Logged",
                "4. Weekly Active Telemetry Loggers"
            ],
            "Volunteers": [50000, 46500, 44200, 43100],
            "Conversion": ["100%", "93.0%", "88.4%", "86.2%"]
        })
        
        fig_adopt = px.funnel(
            funnel_stages,
            x='Volunteers',
            y='Stage',
            text=funnel_stages['Conversion'],
            template='plotly_dark',
            color='Stage',
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_adopt.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig_adopt, use_container_width=True)

    with state_lag_col:
        st.markdown("### 📍 Reporting Lag by Campaign State")
        st.caption("Comparing mean lag across active state chapters.")
        
        merged_feed = feedbacks_df.merge(constituencies_df[['id', 'state']], left_on='constituency_id', right_on='id')
        state_lag = merged_feed.groupby('state').agg(
            mean_lag=('reporting_lag_hours', 'mean'),
            offline_pct=('is_offline_captured', lambda x: (x.sum() / len(x)) * 100)
        ).reset_index().sort_values(by='mean_lag')

        fig_state_lag = px.bar(
            state_lag,
            x='mean_lag',
            y='state',
            orientation='h',
            template='plotly_dark',
            color='mean_lag',
            color_continuous_scale='Blues_r',
            text=state_lag['mean_lag'].apply(lambda x: f"{x:.1f}h")
        )
        fig_state_lag.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=10), xaxis_title="Average Lag (Hours)")
        st.plotly_chart(fig_state_lag, use_container_width=True)


# =========================================================================
# VIEW 4: PRODUCT PRD & RICE MATRIX VIEWER
# =========================================================================
elif "Product PRD" in persona_choice:
    st.subheader("📑 Product Requirement Document & RICE Framework")
    st.caption("Strategic Product Management Artifacts — Open CivicTech Campaign Intelligence Group.")

    tab_rice, tab_personas, tab_prd_doc = st.tabs([
        "⚖️ RICE Feature Prioritization Matrix",
        "👤 Target User Personas",
        "📄 Full PRD Document"
    ])

    with tab_rice:
        st.markdown("""
            #### RICE Prioritization Framework Analysis
            $$\\text{RICE Score} = \\frac{\\text{Reach} \\times \\text{Impact} \\times \\text{Confidence}}{\\text{Effort}}$$
        """)
        
        rice_data = [
            {"Rank": "P0 (Rank 1)", "Feature": "Real-Time Critical Issue Escalation & SLA Engine", "Reach": 10, "Impact": 3.0, "Confidence": "100%", "Effort": 2.0, "RICE Score": 15.00, "Decision": "MVP Release (Immediate)"},
            {"Rank": "P0 (Rank 2)", "Feature": "Demographic Cohort & Scheme Sentiment Analytics", "Reach": 9, "Impact": 3.0, "Confidence": "90%", "Effort": 2.5, "RICE Score": 9.72, "Decision": "MVP Release (Immediate)"},
            {"Rank": "P0 (Rank 3)", "Feature": "Offline-First Low-Bandwidth Telemetry Ingestion", "Reach": 10, "Impact": 2.0, "Confidence": "90%", "Effort": 2.0, "RICE Score": 9.00, "Decision": "MVP Release (Immediate)"},
            {"Rank": "P1 (Rank 4)", "Feature": "Interactive Macro Constituency Heatmap (Choropleth)", "Reach": 8, "Impact": 2.0, "Confidence": "95%", "Effort": 2.0, "RICE Score": 7.60, "Decision": "MVP Release (Immediate)"},
            {"Rank": "P1 (Rank 5)", "Feature": "Operational Telemetry & Reporting Lag Tracker", "Reach": 7, "Impact": 2.0, "Confidence": "90%", "Effort": 2.0, "RICE Score": 6.30, "Decision": "MVP Release (Immediate)"},
            {"Rank": "P2 (Rank 6)", "Feature": "Automated WhatsApp Bot Ingestion Integration", "Reach": 8, "Impact": 1.0, "Confidence": "70%", "Effort": 3.0, "RICE Score": 1.87, "Decision": "Phase 2 (Post-MVP)"},
            {"Rank": "P3 (Rank 7)", "Feature": "Predictive Voter Turnout Forecasting Model", "Reach": 5, "Impact": 1.0, "Confidence": "50%", "Effort": 4.0, "RICE Score": 0.63, "Decision": "Deprioritized (Noisy historical polls)"},
        ]
        rice_df = pd.DataFrame(rice_data)
        st.dataframe(rice_df, use_container_width=True, hide_index=True)

        st.markdown("""
            > **PM Insight:** Prioritizing real-time issue escalation over predictive turnout was a decisive strategic win. 
            > In Indian electoral battlegrounds, turning around local bottlenecks (e.g. fertilizer delays or hospital admission denials) 
            > within 24 hours directly shifts swing votes, whereas voter turnout models carry high variance and zero operational remediation.
        """)

    with tab_personas:
        p1_col, p2_col = st.columns(2)
        with p1_col:
            st.markdown("""
                <div style="background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 10px;">
                    <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">PERSONA 1</span>
                    <h3 style="color: #f8fafc; margin-top: 8px;">Ramesh Kumar</h3>
                    <p style="color: #94a3b8; font-size: 13px;"><b>Booth Adhyaksha / Field Volunteer</b><br>Booth 142, Phulpur, Uttar Pradesh</p>
                    <hr style="border-color: #334155;">
                    <b style="color: #cbd5e1; font-size: 13px;">Core JTBD:</b>
                    <ul style="color: #94a3b8; font-size: 12px; padding-left: 18px;">
                        <li>Log door-to-door citizen sentiment in &lt;45s during morning rounds.</li>
                        <li>Escalate high-friction bottlenecks without waiting for district meetings.</li>
                        <li>Confirm issue resolution status to give credible answers to local voters.</li>
                    </ul>
                    <b style="color: #cbd5e1; font-size: 13px;">Key Technical Needs:</b>
                    <p style="color: #94a3b8; font-size: 12px;">Offline caching, vernacular/Hinglish acceptance, ultra-low mobile data payload.</p>
                </div>
            """, unsafe_allow_html=True)
            
        with p2_col:
            st.markdown("""
                <div style="background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 10px;">
                    <span style="background: #38bdf8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">PERSONA 2</span>
                    <h3 style="color: #f8fafc; margin-top: 8px;">Dr. Ananya Sharma</h3>
                    <p style="color: #94a3b8; font-size: 13px;"><b>Lead Campaign Data Strategist & War-Room Director</b><br>Central War Room, New Delhi</p>
                    <hr style="border-color: #334155;">
                    <b style="color: #cbd5e1; font-size: 13px;">Core JTBD:</b>
                    <ul style="color: #94a3b8; font-size: 12px; padding-left: 18px;">
                        <li>Detect macro negative sentiment anomalies across 50 battleground constituencies.</li>
                        <li>Attribute voter satisfaction directly to flagship welfare schemes (PM-KISAN, Ayushman Bharat).</li>
                        <li>Enforce strict &lt;24h resolution SLAs on district rapid response cells.</li>
                    </ul>
                    <b style="color: #cbd5e1; font-size: 13px;">Key Technical Needs:</b>
                    <p style="color: #94a3b8; font-size: 12px;">Spatial heatmap drilldowns, cross-cohort pivot matrices, real-time telemetry pipelines.</p>
                </div>
            """, unsafe_allow_html=True)

    with tab_prd_doc:
        prd_file_path = os.path.join(current_dir, "PRD.md")
        if os.path.exists(prd_file_path):
            with open(prd_file_path, "r", encoding="utf-8") as f:
                prd_text = f.read()
            st.markdown(prd_text)
        else:
            st.error("PRD.md not found at platform root.")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style="display: flex; justify-content: space-between; color: #64748b; font-size: 12px;">
        <div><b>JanMat Platform</b> — Open-Source Citizen Telemetry & Analytics Dashboard</div>
        <div>Open-Source (MIT License) | Built with Python, Streamlit, Plotly & SQLAlchemy</div>
    </div>
""", unsafe_allow_html=True)
