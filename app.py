import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Fleet Safety & Compliance Hub", layout="wide")

# Custom Styling for the PM Dashboard
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 1. Load Data (This reads the fleet_data.csv you created)
@st.cache_data
def load_data():
    df = pd.read_csv('fleet_data.csv')
    df['CDL_Expiration'] = pd.to_datetime(df['CDL_Expiration'])
    df['Annual_Inspection_Due'] = pd.to_datetime(df['Annual_Inspection_Due'])
    return df

try:
    df = load_data()
    today = pd.Timestamp(datetime.now().date())

    # 2. Compliance Logic (The "Safety Manager" Brain)
    def calculate_status(due_date):
        days_diff = (due_date - today).days
        if days_diff < 0:
            return "🔴 EXPIRED"
        elif days_diff <= 30:
            return "🟡 WARNING (Under 30 Days)"
        else:
            return "🟢 COMPLIANT"

    df['CDL_Status'] = df['CDL_Expiration'].apply(calculate_status)
    df['Inspection_Status'] = df['Annual_Inspection_Due'].apply(calculate_status)

    # 3. Dashboard Header
    st.title("🚛 Fleet Compliance & Safety Audit Hub")
    st.markdown(f"**Operational Date:** {today.strftime('%B %d, %2026')}")
    st.divider()

    # 4. KPI Metrics (High-level Stakeholder View)
    expired_total = len(df[(df['CDL_Status'] == "🔴 EXPIRED") | (df['Inspection_Status'] == "🔴 EXPIRED")])
    warning_total = len(df[(df['CDL_Status'].str.contains("WARNING")) | (df['Inspection_Status'].str.contains("WARNING"))])
    fleet_health = int(((len(df) - expired_total) / len(df)) * 100)

    m1, m2, m3 = st.columns(3)
    m1.metric("Fleet Health Score", f"{fleet_health}%")
    m2.metric("Critical Violations", expired_total, delta_color="inverse")
    m3.metric("Attention Required", warning_total)

    # 5. Interactive Audit Table
    st.subheader("📋 Safety Audit Table")
    
    # Sidebar Filters
    st.sidebar.header("Filter Audit View")
    view_filter = st.sidebar.multiselect(
        "Filter by Compliance Status:",
        options=["🔴 EXPIRED", "🟡 WARNING (Under 30 Days)", "🟢 COMPLIANT"],
        default=["🔴 EXPIRED", "🟡 WARNING (Under 30 Days)"]
    )

    filtered_df = df[(df['CDL_Status'].isin(view_filter)) | (df['Inspection_Status'].isin(view_filter))]
    
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # 6. PM Insight (Tells the recruiter what you did)
    with st.expander("💡 Project Manager Logic & Risk Mitigation Strategy"):
        st.write("""
        **Objective:** Transition from reactive paper-based tracking to a proactive data-driven compliance model.
        
        **Management Features:**
        - **Risk Mitigation:** The dashboard uses a 30-day "Warning" buffer to allow for scheduling physicals and inspections before a violation occurs.
        - **Resource Allocation:** Managers can filter for 'Expired' status to immediately ground non-compliant equipment or drivers.
        - **Data Integrity:** Centralizes CDL and Truck data into a single source of truth for DOT audits.
        """)

except Exception as e:
    st.error("Error loading data. Please ensure 'fleet_data.csv' is in the same folder.")
