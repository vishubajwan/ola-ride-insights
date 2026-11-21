"""Ola Ride Insights - Streamlit dashboard.  Run: py -m streamlit run app.py"""
import base64
import os
import re
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Ola Ride Insights", page_icon="🚕", layout="wide")
BASE = Path(__file__).parent
POWERBI_URL = ""  # paste your Power BI "Publish to web" / embed URL here

GREEN, BLUE, AMBER, RED, GREY, TEAL = "#A8D83F", "#2E86C1", "#F2A900", "#E5484D", "#9A9A9A", "#1ABC9C"
PALETTE = [GREEN, BLUE, AMBER, RED, TEAL, GREY, "#8E6CEF"]
ORDER = ["Prime Sedan", "Prime SUV", "Prime Plus", "Mini", "Auto", "Bike", "E-Bike"]

# ---------------------------------------------------------------- data
def _get_mysql_url() -> str:
    if os.environ.get("MYSQL_URL"):
        return os.environ["MYSQL_URL"]
    try:
        return st.secrets["MYSQL_URL"]
    except Exception:
        return ""


MYSQL_URL = _get_mysql_url()


def _query(sql: str, **kw) -> pd.DataFrame:
    if MYSQL_URL:
        from sqlalchemy import create_engine
        return pd.read_sql(sql, create_engine(MYSQL_URL), **kw)
    with sqlite3.connect(BASE / "ola.db") as con:
        return pd.read_sql(sql, con, **kw)


@st.cache_data
def load_data() -> pd.DataFrame:
    return _query("SELECT * FROM ola_rides", parse_dates=["date"])


@st.cache_data
def load_queries() -> dict:
    text = (BASE / "queries.sql").read_text()
    parts = re.split(r"^-- (Q\d+: .*)$", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def run_sql(sql: str) -> pd.DataFrame:
    return _query(sql)


def img64(name: str) -> str:
    p = BASE / "assets" / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


# ---------------------------------------------------------------- style
st.markdown(f"""
<style>
.block-container {{padding-top: 1.2rem; max-width: 1400px;}}
.hero {{display:flex; align-items:center; gap:22px; padding:22px 30px; border-radius:18px; margin-bottom:22px;
        background: linear-gradient(120deg,#0e0e0e 0%,#232323 55%,#33420f 100%); border:1px solid #333;}}
.hero img.i {{height:64px}} .hero img.t {{height:46px}}
.hero .sub {{color:#bdbdbd; font-size:0.95rem; margin-top:4px}}
.hero .tag {{margin-left:auto; background:{GREEN}; color:#111; font-weight:700; padding:6px 14px; border-radius:20px; font-size:0.8rem}}
.kpi {{background:#232323; border-radius:14px; padding:16px 18px; border-left:5px solid {GREEN}; height:100%;
       box-shadow:0 2px 10px rgba(0,0,0,.35)}}
.kpi .v {{font-size:1.85rem; font-weight:800; line-height:1.15}} .kpi .l {{color:#a5a5a5; font-size:.85rem; margin-top:4px}}
.kpi.amber {{border-left-color:{AMBER}}} .kpi.red {{border-left-color:{RED}}} .kpi.blue {{border-left-color:{BLUE}}}
.insight {{background:rgba(168,216,63,.10); border:1px solid rgba(168,216,63,.35); border-radius:12px; padding:12px 16px;
           margin:10px 0 4px 0; font-size:.95rem}}
.sect {{font-size:1.05rem; font-weight:700; margin:18px 0 4px 0; letter-spacing:.3px}}
div[data-testid="stSidebar"] {{background:#101010}}
</style>
""", unsafe_allow_html=True)


def kpi(col, value, label, tone=""):
    col.markdown(f'<div class="kpi {tone}"><div class="v">{value}</div><div class="l">{label}</div></div>', unsafe_allow_html=True)


def insight(text):
    st.markdown(f'<div class="insight">💡 <b>Insight:</b> {text}</div>', unsafe_allow_html=True)


def show(fig, title, height=340, legend=False):
    fig.update_layout(title=dict(text=title, font=dict(size=16)), height=height, template="plotly_dark",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      margin=dict(l=10, r=10, t=55, b=10), legend=dict(orientation="h", y=-0.15), font=dict(size=12))
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor="rgba(255,255,255,.08)")
    st.plotly_chart(fig, width="stretch")


inr = lambda v: f"₹{v:,.0f}"
crore = lambda v: f"₹{v / 1e7:.2f} Cr"

# ---------------------------------------------------------------- sidebar + filters
df = load_data()
st.sidebar.markdown(f'<img src="data:image/png;base64,{img64("ola_logo_dark.png")}" style="width:100%;border-radius:10px">', unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["📊 Overview", "🚗 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings",
                                     "🧮 SQL Insights", "🔎 Data Explorer", "📈 Power BI"], label_visibility="collapsed")
st.sidebar.markdown("---\n**Filters**")
vt = st.sidebar.multiselect("Vehicle type", [v for v in ORDER if v in set(df["vehicle_type"])])
status = st.sidebar.multiselect("Booking status", sorted(df["booking_status"].dropna().unique()))
dmin, dmax = df["date"].min().date(), df["date"].max().date()
dr = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
f = df.copy()
if vt: f = f[f["vehicle_type"].isin(vt)]
if status: f = f[f["booking_status"].isin(status)]
if isinstance(dr, tuple) and len(dr) == 2:
    f = f[(f["date"].dt.date >= dr[0]) & (f["date"].dt.date <= dr[1])]
S = f[f["booking_status"] == "Success"]
st.sidebar.caption(f"{len(f):,} of {len(df):,} bookings selected")
st.sidebar.caption("Data source: " + ("MySQL" if MYSQL_URL else "SQLite (ola.db)"))

icon, text = img64("ola_icon.png"), img64("ola_text.png")
st.markdown(f"""<div class="hero"><img class="i" src="data:image/png;base64,{icon}"><div>
<img class="t" src="data:image/png;base64,{text}"><div class="sub">Ride Insights Dashboard · July 2024 · {len(df):,} bookings</div></div>
<div class="tag">{page.split(' ', 1)[1]}</div></div>""", unsafe_allow_html=True)

if f.empty and page in ("📊 Overview", "🚗 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings"):
    st.warning("No rides match the selected filters."); st.stop()

# ---------------------------------------------------------------- pages
if page == "📊 Overview":
    c = st.columns(4)
    kpi(c[0], f"{len(f):,}", "Total bookings")
    kpi(c[1], f"{f['is_success'].mean() * 100:.1f}%", "Success rate", "blue")
    kpi(c[2], crore(S["booking_value"].sum()), "Revenue (completed rides)")
    kpi(c[3], f"{(1 - f['is_success'].mean()) * 100:.1f}%", "Cancelled / not found", "red")
    st.write("")
    a, b = st.columns([3, 2])
    daily = f.groupby(f["date"].dt.date).size().reset_index(name="rides")
    fig = px.area(daily, x="date", y="rides", color_discrete_sequence=[GREEN]); fig.update_yaxes(rangemode="tozero")
    with a: show(fig, "Daily ride volume")
    st_ = f["booking_status"].value_counts().reset_index(); st_.columns = ["status", "rides"]
    fig = px.pie(st_, names="status", values="rides", hole=0.55, color="status",
                 color_discrete_map={"Success": GREEN, "Canceled by Driver": AMBER, "Canceled by Customer": RED, "Driver Not Found": GREY})
    fig.update_traces(textinfo="percent")
    with b: show(fig, "Booking status", legend=True)
    a, b = st.columns([3, 2])
    hr = f.groupby("hour").size().reset_index(name="rides")
    with a: show(px.bar(hr, x="hour", y="rides", color_discrete_sequence=[BLUE]), "Bookings by hour of day")
    loc = f["pickup_location"].value_counts().head(8).reset_index(); loc.columns = ["location", "rides"]
    with b: show(px.bar(loc.iloc[::-1], x="rides", y="location", orientation="h", color_discrete_sequence=[TEAL]), "Top pickup locations")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    n_days = f.groupby("day_of_week")["date"].nunique()  # July 2024 has 5 Mon/Tue/Wed but 4 of the other days
    hm = (pd.crosstab(f["day_of_week"], f["hour"]).div(n_days, axis=0)).reindex(days)
    show(px.imshow(hm.round(0), aspect="auto", color_continuous_scale="YlGn", labels=dict(x="Hour", y="", color="Avg rides")),
         "When do people book? (average rides per day × hour)", 320)
    insight(f"Only {f['is_success'].mean() * 100:.1f}% of bookings were completed. Demand is almost flat across hours and days, "
            "so the real opportunity is converting more bookings, not finding a peak hour.")

elif page == "🚗 Vehicle Type":
    g = f.groupby("vehicle_type").agg(bookings=("booking_id", "count"), total_value=("booking_value", "sum"),
                                      total_dist=("ride_distance", "sum"), avg_dist=("ride_distance", "mean"),
                                      success_rate=("is_success", "mean"))
    g["success_value"] = S.groupby("vehicle_type")["booking_value"].sum()
    g = g.reindex([v for v in ORDER if v in g.index]).reset_index()
    best = g.loc[g["success_value"].idxmax()]
    c = st.columns(3)
    kpi(c[0], best["vehicle_type"], "Highest revenue vehicle")
    kpi(c[1], f"{g['success_rate'].max() * 100:.1f}%", f"Best success rate ({g.loc[g['success_rate'].idxmax(), 'vehicle_type']})", "blue")
    kpi(c[2], f"{g.loc[g['avg_dist'].idxmin(), 'vehicle_type']}", f"Shortest trips ({g['avg_dist'].min():.1f} km avg)", "amber")
    st.markdown('<div class="sect">Vehicle summary</div>', unsafe_allow_html=True)
    t = g.assign(total_value=g.total_value.map(inr), success_value=g.success_value.map(inr),
                 avg_dist=g.avg_dist.map("{:.2f} km".format), total_dist=g.total_dist.map("{:,.0f} km".format),
                 success_rate=(g.success_rate * 100).map("{:.1f}%".format), bookings=g.bookings.map("{:,}".format))
    t.columns = ["Vehicle Type", "Bookings", "Total Booking Value", "Total Distance", "Avg Distance", "Success Rate", "Success Booking Value"]
    st.dataframe(t[["Vehicle Type", "Bookings", "Total Booking Value", "Success Booking Value", "Avg Distance", "Total Distance", "Success Rate"]],
                 hide_index=True, width="stretch")
    a, b = st.columns(2)
    with a: show(px.bar(g, x="vehicle_type", y="success_value", color="vehicle_type", color_discrete_sequence=PALETTE, text_auto=".3s"), "Revenue from completed rides")
    with b: show(px.bar(g, x="vehicle_type", y="avg_dist", color="vehicle_type", color_discrete_sequence=PALETTE, text_auto=".1f"), "Average distance per booking (km)")
    insight("Auto trips are far shorter (about 6 km) than every other vehicle (about 15 km), yet Auto earns as much revenue as the bigger cars.")

elif page == "💰 Revenue":
    lost = f["booking_value"].sum() - S["booking_value"].sum()
    c = st.columns(4)
    kpi(c[0], crore(f["booking_value"].sum()), "Total booking value")
    kpi(c[1], crore(S["booking_value"].sum()), "Success booking value", "blue")
    kpi(c[2], inr(S["booking_value"].mean()), "Avg value per completed ride")
    kpi(c[3], crore(lost), "Value lost to cancellations", "red")
    st.write("")
    a, b = st.columns(2)
    pay = S.groupby("payment_method")["booking_value"].sum().reset_index().sort_values("booking_value", ascending=False)
    fig = px.pie(pay, names="payment_method", values="booking_value", hole=0.55, color_discrete_sequence=PALETTE)
    with a: show(fig, "Revenue by payment method", legend=True)
    v = S.groupby("vehicle_type")["booking_value"].mean().reindex(ORDER).reset_index()
    with b: show(px.bar(v, x="vehicle_type", y="booking_value", color="vehicle_type", color_discrete_sequence=PALETTE, text_auto=".0f"), "Average booking value by vehicle (₹)")
    dd = S.groupby(S["date"].dt.date)["booking_value"].sum().reset_index()
    fig = px.area(dd, x="date", y="booking_value", color_discrete_sequence=[AMBER]); fig.update_yaxes(rangemode="tozero")
    show(fig, "Daily revenue from completed rides", 320)
    top = S.groupby("customer_id")["booking_value"].sum().nlargest(5).reset_index()
    st.markdown('<div class="sect">Top 5 customers by booking value</div>', unsafe_allow_html=True)
    top["booking_value"] = top["booking_value"].map(inr); top.columns = ["Customer ID", "Total Booking Value"]
    st.dataframe(top, hide_index=True, width="stretch")
    share = pay.set_index("payment_method")["booking_value"]; share = share / share.sum() * 100
    insight(f"Cash still brings {share.get('Cash', 0):.0f}% of revenue and UPI {share.get('UPI', 0):.0f}%; cards are small. "
            f"Cancellations cost about {crore(lost)}.")

elif page == "❌ Cancellation":
    cc, dc = f[f["booking_status"] == "Canceled by Customer"], f[f["booking_status"] == "Canceled by Driver"]
    nf = (f["booking_status"] == "Driver Not Found").sum(); inc = (f["incomplete_rides"] == "Yes").sum()
    c = st.columns(4)
    kpi(c[0], f"{len(cc):,}", f"Cancelled by customer ({len(cc) / len(f) * 100:.1f}%)", "amber")
    kpi(c[1], f"{len(dc):,}", f"Cancelled by driver ({len(dc) / len(f) * 100:.1f}%)", "red")
    kpi(c[2], f"{nf:,}", f"Driver not found ({nf / len(f) * 100:.1f}%)", "blue")
    kpi(c[3], f"{inc:,}", "Incomplete rides")
    st.write("")
    a, b = st.columns(2)
    x = cc["canceled_rides_by_customer"].value_counts().reset_index(); x.columns = ["reason", "count"]
    with a: show(px.bar(x.iloc[::-1], x="count", y="reason", orientation="h", color_discrete_sequence=[AMBER], text_auto=True), "Why customers cancel")
    y = dc["canceled_rides_by_driver"].value_counts().reset_index(); y.columns = ["reason", "count"]
    with b: show(px.bar(y.iloc[::-1], x="count", y="reason", orientation="h", color_discrete_sequence=[RED], text_auto=True), "Why drivers cancel")
    a, b = st.columns(2)
    z = f[f["incomplete_rides"] == "Yes"]["incomplete_rides_reason"].value_counts().reset_index(); z.columns = ["reason", "count"]
    with a: show(px.pie(z, names="reason", values="count", hole=0.55, color_discrete_sequence=PALETTE), "Incomplete ride reasons", legend=True)
    cv = pd.concat([cc.assign(by="Customer"), dc.assign(by="Driver")]).groupby(["vehicle_type", "by"]).size().reset_index(name="count")
    with b: show(px.bar(cv, x="vehicle_type", y="count", color="by", barmode="group", color_discrete_map={"Customer": AMBER, "Driver": RED},
                        category_orders={"vehicle_type": ORDER}), "Cancellations by vehicle type", legend=True)
    if len(cc):
        drv = cc["canceled_rides_by_customer"].isin(["Driver is not moving towards pickup location", "Driver asked to cancel"]).mean() * 100
        insight(f"Drivers cancel more than customers, and about {drv:.0f}% of customer cancellations are caused by driver behaviour "
                "(not coming to the pickup or asking to cancel). Fixing driver reliability is the biggest lever.")

elif page == "⭐ Ratings":
    c = st.columns(3)
    kpi(c[0], f"{S['driver_ratings'].mean():.2f} ★", "Average driver rating")
    kpi(c[1], f"{S['customer_rating'].mean():.2f} ★", "Average customer rating", "blue")
    kpi(c[2], f"{len(S):,}", "Rated (completed) rides", "amber")
    st.write("")
    r = S.groupby("vehicle_type").agg(Driver=("driver_ratings", "mean"), Customer=("customer_rating", "mean")).reindex(ORDER).reset_index().melt("vehicle_type", var_name="who", value_name="rating")
    fig = px.bar(r, x="vehicle_type", y="rating", color="who", barmode="group", text_auto=".2f", color_discrete_map={"Driver": GREEN, "Customer": BLUE})
    fig.update_yaxes(range=[0, 5]); show(fig, "Average rating by vehicle type", legend=True)
    a, b = st.columns(2)
    with a: show(px.histogram(S, x="driver_ratings", nbins=20, color_discrete_sequence=[GREEN]), "Driver rating distribution")
    with b: show(px.histogram(S, x="customer_rating", nbins=20, color_discrete_sequence=[BLUE]), "Customer rating distribution")
    insight("Ratings are almost identical across vehicle types (about 4.0 for both drivers and customers), so rating alone does not explain cancellations.")

elif page == "🧮 SQL Insights":
    queries = load_queries()
    choice = st.selectbox("Choose a question", list(queries))
    st.code(queries[choice], language="sql")
    res = run_sql(queries[choice])
    st.caption(f"{len(res):,} row(s) returned")
    st.dataframe(res.head(1000), width="stretch", hide_index=True)
    st.download_button("⬇ Download result as CSV", res.to_csv(index=False), "result.csv")
    with st.expander("Run your own SQL (SELECT only)"):
        custom = st.text_area("Query", "SELECT vehicle_type, COUNT(*) AS rides FROM ola_rides GROUP BY vehicle_type")
        if st.button("Run"):
            if custom.strip().lower().startswith("select"):
                try: st.dataframe(run_sql(custom), width="stretch")
                except Exception as e: st.error(e)
            else:
                st.warning("Only SELECT statements are allowed.")

elif page == "🔎 Data Explorer":
    q = st.text_input("Search (Booking ID / Customer ID / location)")
    out = f
    if q:
        mask = pd.Series(False, index=f.index)
        for col in ["booking_id", "customer_id", "pickup_location", "drop_location"]:
            mask |= f[col].astype(str).str.contains(q, case=False, na=False)
        out = f[mask]
    st.caption(f"{len(out):,} rows")
    st.dataframe(out.head(2000), width="stretch", hide_index=True)

else:
    if POWERBI_URL:
        st.components.v1.iframe(POWERBI_URL, height=700, scrolling=True)
    else:
        st.info("Publish your report (Power BI Service → File → Embed report → Publish to web) and paste the URL into POWERBI_URL at the top of app.py.")
