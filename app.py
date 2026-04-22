import subprocess
import sys

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os

st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Global reset & font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── App background ── */
    .stApp {
        background: #f0f4f8;
    }

    /* ── Main block container ── */
    .block-container {
        padding: 1.5rem 2.5rem 2rem 2.5rem !important;
        max-width: 1400px;
    }

    /* ── Header band ── */
    .dashboard-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 60%, #4a90d9 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 8px 32px rgba(31, 78, 121, 0.22);
    }
    .dashboard-header h1 {
        color: #ffffff;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: rgba(255,255,255,0.82);
        font-size: 1rem;
        margin: 0;
        font-weight: 400;
    }

    /* ── KPI tiles ── */
    .kpi-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-left: 5px solid;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    .kpi-card.blue   { border-color: #1f4e79; }
    .kpi-card.green  { border-color: #1a7a4a; }
    .kpi-card.orange { border-color: #c75e15; }
    .kpi-card.purple { border-color: #6b3fa0; }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #6b7280;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #9ca3af;
    }

    /* ── Chart / section cards ── */
    .chart-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        margin-bottom: 0.6rem;
    }
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1f4e79;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }

    /* ── Section divider ── */
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #9ca3af;
        margin: 1.25rem 0 0.6rem 0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #1f4e79 !important;
    }
    [data-testid="stSidebar"] {
    background: #1f4e79 !important;
}

/* Text labels */
[data-testid="stSidebar"] label {
    color: rgba(255,255,255,0.9) !important;
}

/* Input text inside fields */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] span {
    color: #111827 !important;
}

/* Dropdown background */
[data-testid="stSidebar"] [data-baseweb="select"] {
    background: #ffffff !important;
    border-radius: 8px !important;
}
    [data-testid="stSidebar"] .stMultiSelect > label,
    [data-testid="stSidebar"] .stDateInput > label,
    [data-testid="stSidebar"] .stSelectbox > label {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255,255,255,0.12) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: rgba(255,255,255,0.25) !important;
        border-radius: 4px !important;
    }

    /* ── Data table ── */
    .dataframe-container {
        background: #ffffff;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    }

    /* ── Plotly chart background ── */
    .js-plotly-plot { background: transparent !important; }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* ── Upload box ── */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# COLUMN DETECTION HELPERS
# ─────────────────────────────────────────────

COLUMN_ALIASES = {
    "employee_id":   ["emp id", "employee id", "empid", "emp_id", "id", "staff id"],
    "employee_name": ["employee name", "name", "emp name", "full name"],
    "department":    ["department", "dept", "department name", "division", "team"],
    "gender":        ["gender", "sex", "gender identity"],
    "salary":        ["salary", "salary (ctc) (yearly)", "ctc", "annual salary",
                      "salary ctc", "compensation", "pay", "wage"],
    "joining_date":  ["date of joining", "joining date", "join date", "doj",
                      "start date", "hire date", "onboard date"],
    "attrition":     ["attrition", "left", "resigned", "status", "active", "terminated"],
    "location":      ["location", "city", "state", "region", "branch"],
    "designation":   ["designation", "title", "job title", "role", "position"],
    "age":           ["age", "years"],
}

def find_col(df_cols: list, key: str) -> str | None:
    lower_cols = {c.lower().strip(): c for c in df_cols}
    for alias in COLUMN_ALIASES.get(key, []):
        if alias in lower_cols:
            return lower_cols[alias]
    return None


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────

def load_data(uploaded_file=None) -> pd.DataFrame | None:
    try:
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        elif os.path.exists("data.xlsx"):
            df = pd.read_excel("data.xlsx", engine="openpyxl")
        else:
            return None
        return df
    except Exception as e:
        st.error(f"❌ Could not load file: {e}")
        return None


# ─────────────────────────────────────────────
# PRE-PROCESSING
# ─────────────────────────────────────────────

def preprocess_data(df: pd.DataFrame) -> dict:
    cols = {}
    for key in COLUMN_ALIASES:
        cols[key] = find_col(df.columns.tolist(), key)

    # Joining date → datetime
    if cols["joining_date"]:
        df[cols["joining_date"]] = pd.to_datetime(df[cols["joining_date"]], errors="coerce")
        df["_year_month"] = df[cols["joining_date"]].dt.to_period("M").astype(str)
        df["_year"] = df[cols["joining_date"]].dt.year

    # Salary → numeric
    if cols["salary"]:
        df[cols["salary"]] = pd.to_numeric(df[cols["salary"]], errors="coerce")

    # Synthetic attrition if missing (random ~12% for demo)
    if not cols["attrition"]:
        rng = np.random.default_rng(42)
        df["_attrition"] = rng.choice(["Yes", "No"], size=len(df), p=[0.12, 0.88])
        cols["attrition"] = "_attrition"

    return df, cols


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────

def create_filters(df: pd.DataFrame, cols: dict):
    st.sidebar.markdown(
        "<div style='padding:1rem 0 0.5rem 0;'>"
        "<span style='font-size:1.2rem;font-weight:700;'>⚙️ Filters</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    filtered = df.copy()

    # Department
    if cols["department"]:
        st.sidebar.markdown("<div class='section-label'>Department</div>", unsafe_allow_html=True)
        dept_options = sorted(df[cols["department"]].dropna().unique().tolist())
        selected_dept = st.sidebar.multiselect(
            "Select departments", dept_options, default=dept_options,
            key="dept_filter", label_visibility="collapsed"
        )
        if selected_dept:
            filtered = filtered[filtered[cols["department"]].isin(selected_dept)]

    # Gender
    if cols["gender"]:
        st.sidebar.markdown("<div class='section-label'>Gender</div>", unsafe_allow_html=True)
        gender_options = sorted(df[cols["gender"]].dropna().unique().tolist())
        selected_gender = st.sidebar.multiselect(
            "Select gender", gender_options, default=gender_options,
            key="gender_filter", label_visibility="collapsed"
        )
        if selected_gender:
            filtered = filtered[filtered[cols["gender"]].isin(selected_gender)]

    # Joining date range
    if cols["joining_date"]:
        st.sidebar.markdown("<div class='section-label'>Date of Joining</div>", unsafe_allow_html=True)
        min_date = df[cols["joining_date"]].min().date()
        max_date = df[cols["joining_date"]].max().date()
        date_range = st.sidebar.date_input(
            "Date range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
            key="date_filter", label_visibility="collapsed"
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
            filtered = filtered[
                (filtered[cols["joining_date"]] >= start) &
                (filtered[cols["joining_date"]] <= end)
            ]

    # Location filter (bonus)
    if cols["location"]:
        st.sidebar.markdown("<div class='section-label'>Location</div>", unsafe_allow_html=True)
        loc_options = sorted(df[cols["location"]].dropna().unique().tolist())
        selected_loc = st.sidebar.multiselect(
            "Select locations", loc_options, default=loc_options,
            key="loc_filter", label_visibility="collapsed"
        )
        if selected_loc:
            filtered = filtered[filtered[cols["location"]].isin(selected_loc)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Showing **{len(filtered):,}** of **{len(df):,}** employees")

    return filtered


# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────

def create_kpis(filtered: pd.DataFrame, df_full: pd.DataFrame, cols: dict):
    total_emp = len(filtered)

    # Attrition rate
    if cols["attrition"]:
        attr_col = filtered[cols["attrition"]].astype(str).str.strip().str.lower()
        yes_vals = attr_col.isin(["yes", "1", "true", "left", "resigned", "terminated"])
        attrition_rate = (yes_vals.sum() / total_emp * 100) if total_emp else 0
    else:
        attrition_rate = 0.0

    # Avg salary
    avg_salary = (
        filtered[cols["salary"]].dropna().mean()
        if cols["salary"] else 0
    )

    # Departments
    num_depts = (
        filtered[cols["department"]].nunique()
        if cols["department"] else "N/A"
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    kpi_data = [
        (c1, "blue",   "👥 Total Employees",   f"{total_emp:,}",           "Active headcount"),
        (c2, "orange", "📉 Attrition Rate",     f"{attrition_rate:.1f}%",   "Of filtered workforce"),
        (c3, "green",  "💰 Avg. Annual Salary", f"₹{avg_salary:,.0f}",      "CTC (Yearly)"),
        (c4, "purple", "🏢 Departments",         str(num_depts),             "Active departments"),
    ]

    for col_obj, color, label, value, sub in kpi_data:
        with col_obj:
            st.markdown(
                f"""
                <div class="kpi-card {color}">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#374151"),
    margin=dict(l=20, r=20, t=30, b=20),
)
PALETTE = ["#1f4e79", "#2e75b6", "#4a90d9", "#6ab0e8", "#9dd0f5",
           "#c0e3f9", "#1a7a4a", "#2ea06a", "#6b3fa0", "#9b67d4"]


def _fig_defaults(fig):
    fig.update_layout(**CHART_THEME)
    fig.update_layout(legend=dict(bgcolor="rgba(0,0,0,0)"))
    return fig


def create_charts(filtered: pd.DataFrame, cols: dict):
    # ── Row 1: Headcount by Dept  |  Gender Distribution
    r1c1, r1c2 = st.columns([3, 2], gap="medium")

    with r1c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">👥 Headcount by Department</div>', unsafe_allow_html=True)
        if cols["department"]:
            dept_counts = (
                filtered[cols["department"]]
                .value_counts()
                .reset_index()
            )
            dept_counts.columns = ["Department", "Count"]
            dept_counts = dept_counts.sort_values("Count", ascending=True)
            fig = px.bar(
                dept_counts, x="Count", y="Department",
                orientation="h", color="Count",
                color_continuous_scale=["#4a90d9", "#1f4e79"],
                text="Count",
            )
            fig.update_traces(textposition="outside", textfont_size=12)
            fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
            fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Department column not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⚧ Gender Distribution</div>', unsafe_allow_html=True)
        if cols["gender"]:
            gender_counts = filtered[cols["gender"]].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            fig = px.pie(
                gender_counts, names="Gender", values="Count",
                color_discrete_sequence=["#1f4e79", "#4a90d9", "#9dd0f5"],
                hole=0.48,
            )
            fig.update_traces(
                textinfo="percent+label",
                textfont_size=13,
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
            fig.update_layout(**CHART_THEME, showlegend=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Gender column not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Monthly Hiring Trend  |  Attrition by Dept
    r2c1, r2c2 = st.columns([3, 2], gap="medium")

    with r2c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 Monthly Hiring Trend</div>', unsafe_allow_html=True)
        if cols["joining_date"] and "_year_month" in filtered.columns:
            monthly = (
                filtered.groupby("_year_month")
                .size()
                .reset_index(name="Hires")
                .sort_values("_year_month")
            )
            fig = px.line(
                monthly, x="_year_month", y="Hires",
                markers=True,
                color_discrete_sequence=["#1f4e79"],
                labels={"_year_month": "Month", "Hires": "New Hires"},
            )
            fig.update_traces(
                line=dict(width=2.5),
                marker=dict(size=6, color="#2e75b6"),
                fill="tozeroy",
                fillcolor="rgba(74,144,217,0.12)",
            )
            fig.update_xaxes(
                showgrid=False, tickangle=-45,
                tickfont=dict(size=10),
                nticks=14,
            )
            fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            fig.update_layout(**CHART_THEME)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Joining date column not found for hiring trend.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r2c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📉 Attrition by Department</div>', unsafe_allow_html=True)
        if cols["attrition"] and cols["department"]:
            attr_vals = filtered[cols["attrition"]].astype(str).str.strip().str.lower()
            attr_mask = attr_vals.isin(["yes", "1", "true", "left", "resigned", "terminated"])
            attr_df = filtered[attr_mask]

            if not attr_df.empty:
                attr_dept = attr_df[cols["department"]].value_counts().reset_index()
                attr_dept.columns = ["Department", "Attritions"]
                fig = px.bar(
                    attr_dept, x="Department", y="Attritions",
                    color="Attritions",
                    color_continuous_scale=["#f59e0b", "#dc2626"],
                    text="Attritions",
                )
                fig.update_traces(textposition="outside", textfont_size=12)
                fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No attrition records in filtered data.")
        else:
            st.warning("Attrition/Department column not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 3: Salary Distribution | Designation Breakdown
    r3c1, r3c2 = st.columns([2, 3], gap="medium")

    with r3c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💰 Salary Distribution</div>', unsafe_allow_html=True)
        if cols["salary"]:
            sal = filtered[cols["salary"]].dropna()
            fig = px.histogram(
                sal, nbins=18,
                color_discrete_sequence=["#2e75b6"],
                labels={"value": "Annual Salary (₹)", "count": "Employees"},
            )
            fig.update_traces(marker_line_color="#1f4e79", marker_line_width=0.8)
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            fig.update_layout(**CHART_THEME)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Salary column not found.")
        st.markdown("</div>", unsafe_allow_html=True)

    with r3c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🏷️ Top 10 Designations</div>', unsafe_allow_html=True)
        if cols["designation"]:
            desig = (
                filtered[cols["designation"]]
                .value_counts()
                .head(10)
                .reset_index()
            )
            desig.columns = ["Designation", "Count"]
            desig = desig.sort_values("Count", ascending=True)
            fig = px.bar(
                desig, x="Count", y="Designation",
                orientation="h",
                color="Count",
                color_continuous_scale=["#6ab0e8", "#1f4e79"],
                text="Count",
            )
            fig.update_traces(textposition="outside", textfont_size=11)
            fig.update_layout(coloraxis_showscale=False, **CHART_THEME)
            fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb", zeroline=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Designation column not found.")
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA TABLE
# ─────────────────────────────────────────────

def show_data_table(filtered: pd.DataFrame, cols: dict):
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📋 Employee Records</div>', unsafe_allow_html=True)

    # Drop sensitive/internal cols for display
    hide = ["Contact no.", "Email id", "Pan Card no.", "Aadhar Card no.",
            "_year_month", "_year", "_attrition"]
    display_cols = [c for c in filtered.columns if c not in hide]
    display_df = filtered[display_cols].copy()

    # Format salary
    if cols["salary"] and cols["salary"] in display_df.columns:
        display_df[cols["salary"]] = display_df[cols["salary"]].apply(
            lambda x: f"₹{x:,.0f}" if pd.notna(x) else ""
        )

    # Format joining date
    if cols["joining_date"] and cols["joining_date"] in display_df.columns:
        display_df[cols["joining_date"]] = pd.to_datetime(
            display_df[cols["joining_date"]], errors="coerce"
        ).dt.strftime("%d %b %Y")

    col_search, col_count = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search employee name", key="emp_search",
                               placeholder="Type a name…", label_visibility="collapsed")
    with col_count:
        st.caption(f"**{len(display_df):,}** records")

    if search:
        name_col = cols.get("employee_name")
        if name_col and name_col in display_df.columns:
            display_df = display_df[
                display_df[name_col].astype(str).str.lower().str.contains(search.lower())
            ]

    st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        height=380,
    )

    # Download button
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=csv,
        file_name="hr_filtered_data.csv",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    # ── Header ──
    st.markdown(
        """
        <div class="dashboard-header">
            <h1>HR Analytics Dashboard</h1>
            <p>Interactive workforce insights — filter, explore and download your HR data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar: file uploader ──
    st.sidebar.markdown(
        "<div style='padding:1.2rem 0 0.25rem 0;'>"
        "<span style='font-size:1.1rem;font-weight:700;'>📂 Data Source</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel file (.xlsx)",
        type=["xlsx", "xls"],
        key="file_uploader",
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.sidebar.success(f"✅ {uploaded_file.name}")
    elif os.path.exists("data.xlsx"):
        st.sidebar.info("📄 Using local: data.xlsx")
    else:
        st.sidebar.warning("No file loaded yet.")

    st.sidebar.markdown("---")

    # ── Load ──
    df_raw = load_data(uploaded_file)
    if df_raw is None or df_raw.empty:
        st.error("⚠️ No data available. Please upload an Excel file or place `data.xlsx` in the same folder.")
        st.stop()

    # ── Preprocess ──
    df, cols = preprocess_data(df_raw.copy())

    # ── Filters → returns filtered df ──
    filtered = create_filters(df, cols)

    if filtered.empty:
        st.warning("⚠️ No employees match the selected filters. Please adjust your filters.")
        st.stop()

    # ── KPIs ──
    create_kpis(filtered, df, cols)

    
    # ── Charts ──
    create_charts(filtered, cols)

    # ── Table ──
    show_data_table(filtered, cols)

    # ── Footer ──
    st.markdown(
        """
        <div style='text-align:center;padding:1.5rem 0 0.5rem 0;
                    color:#9ca3af;font-size:0.78rem;'>
            HR Analytics Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
