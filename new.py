import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.express as px
import os
import gspread

# --------------------------- CONFIG ---------------------------
PRODUCTIVE_THRESHOLD_HOURS = 6
GOOGLE_SHEET_NAME = "Productivity Tracker"
LOCAL_CSV_FILE = "stopwatch_sessions.csv"

def get_gsheet():
    client = gspread.service_account(filename="credentials.json")
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet

# ---------------------- COUNTDOWN DISPLAY ---------------------
today = datetime.now()
end_date = datetime(2025, 11, 30)

if today.month == 12:
    next_month = date(today.year + 1, 1, 1)
else:
    next_month = date(today.year, today.month + 1, 1)
days_left_month = (next_month - today.date()).days

week_end = today + timedelta(days=(6 - today.weekday()))
days_left_week = (week_end.date() - today.date()).days
hours_left_day = 24 - today.hour - today.minute / 60

st.title("⏱️ Productivity Tracker")

day_metrics = st.columns(4)
day_metrics[0].metric("Days to 30 Nov", (end_date - today).days)
day_metrics[1].metric("Days Left in Month", days_left_month)
day_metrics[2].metric("Days Left in Week", days_left_week)
day_metrics[3].metric("Hours Left Today", f"{hours_left_day:.1f}h")

# ---------------------- LOAD DATA FUNCTION --------------------
def load_sessions():
    if os.path.exists(LOCAL_CSV_FILE):
        df = pd.read_csv(LOCAL_CSV_FILE)

        if "session_start" in df.columns and "session_end" in df.columns:
            df["session_start"] = pd.to_datetime(df["session_start"], errors='coerce')
            df["session_end"] = pd.to_datetime(df["session_end"], errors='coerce')
            df["duration_min"] = (df["session_end"] - df["session_start"]).dt.total_seconds() / 60
        else:
            st.error("CSV must contain 'session_start' and 'session_end' columns.")
            df = pd.DataFrame(columns=["session_start", "session_end", "duration_min"])
        return df
    else:
        return pd.DataFrame(columns=["session_start", "session_end", "duration_min"])

# ------------------------ UI & MAIN LOGIC ---------------------
# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["session_start", "session_end", "duration_min"])

# Reload button
if st.button("Reload Data"):
    st.session_state.data = load_sessions()
    st.session_state.last_reload = datetime.now().strftime("%H:%M:%S")
    st.success("Data reloaded from local stopwatch app!")

if "last_reload" in st.session_state:
    st.caption(f"Last Reload: {st.session_state.last_reload}")

data = st.session_state.data

if data.empty:
    st.info("No session data found yet. Use the local stopwatch app to add sessions and click Reload.")
else:
    data["date"] = data["session_start"].dt.date
    summary = data.groupby("date")["duration_min"].sum().reset_index()
    summary["productive"] = summary["duration_min"] >= PRODUCTIVE_THRESHOLD_HOURS * 60
    summary["duration_hr"] = summary["duration_min"] / 60

    # -------- PIE CHART: Focus Distribution for Today --------
    today_str = date.today()
    today_sessions = data[data["date"] == today_str]

    if not today_sessions.empty:
        productive_minutes = today_sessions["duration_min"].sum()
        now = datetime.now()
        minutes_passed_today = (now - datetime.combine(now.date(), datetime.min.time())).total_seconds() / 60
        expected_minutes_by_now = minutes_passed_today
        unproductive_minutes = expected_minutes_by_now - productive_minutes
        unproductive_minutes = max(unproductive_minutes, 0)

        pie_df = pd.DataFrame({
            "Category": ["Focused", "Unfocused"],
            "Minutes": [productive_minutes, unproductive_minutes]
        })

        fig = px.pie(pie_df, names="Category", values="Minutes", title="Today's Focus Distribution")
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data logged for today yet.")

    # ---------------------- Daily Goal-Based Progress Bar --------------------
    selected_goal = st.selectbox("🎯 Select your focus goal for today (hours):", options=[2, 4, 6, 8, 10, 12], index=3)

    today_data = summary[summary["date"] == today_str]

    if not today_data.empty:
        focused_hours_today = today_data["duration_min"].values[0] / 60
    else:
        focused_hours_today = 0

    progress = min(focused_hours_today / selected_goal, 1.0)

    st.markdown(f"### ✅ **Daily Progress Toward Target**")
    st.progress(progress)
    st.markdown(f"**Focused today:** {focused_hours_today:.2f}h / {selected_goal}h ({progress*100:.1f}%)")

    # ---------------------- Line Chart: Last 7 Days --------------------
    df = load_sessions()
    df["session_start"] = pd.to_datetime(df["session_start"])
    df["session_end"] = pd.to_datetime(df["session_end"])
    df["date"] = df["session_start"].dt.date
    df["duration_min"] = (df["session_end"] - df["session_start"]).dt.total_seconds() / 60

    daily_focus = df.groupby("date")["duration_min"].sum().reset_index()
    daily_focus["duration_hr"] = daily_focus["duration_min"] / 60

    last_7_days = [today.date() - timedelta(days=i) for i in range(6, -1, -1)]
    last_7_df = pd.DataFrame({"date": last_7_days})
    week_data = pd.merge(last_7_df, daily_focus[["date", "duration_hr"]], on="date", how="left").fillna(0)

    week_data["date"] = pd.to_datetime(week_data["date"])
    week_data["day_label"] = week_data["date"].dt.strftime("%a %d-%b")

    fig = px.line(
        week_data,
        x="day_label",
        y="duration_hr",
        title="Focus Hours in Last 7 Days",
        markers=True,
        labels={"day_label": "Day", "duration_hr": "Focused Hours"},
    )

    fig.update_layout(
        yaxis=dict(range=[0, max(12, week_data["duration_hr"].max() + 1)]),
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True)
