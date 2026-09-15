import math
import warnings
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="HC Analytics — Regretted Attrition",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# THEME / CSS  (dark, KPI-card style)
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500;700&display=swap');

:root {
  --bg:        #0b0f19;
  --surface:   #111827;
  --surface2:  #1a2235;
  --border:    rgba(255,255,255,0.07);
  --text:      #e8edf5;
  --muted:     #6b7a99;
  --accent:    #f59e0b;
  --accent2:   #3b82f6;
  --danger:    #f87171;
  --good:      #22d3a4;
  --warn:      #fbbf24;
  --purple:    #a78bfa;
}

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: var(--bg) !important; color: var(--text) !important; }
.stApp { background: var(--bg) !important; }
.main .block-container { padding: 1.1rem 1.8rem 2.5rem; max-width: 1480px; }

[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--text) !important; }

.hero {
    background: linear-gradient(135deg, #1a1206 0%, #2b1400 45%, #0d2147 100%);
    border: 1px solid var(--border); border-radius: 18px;
    padding: 24px 28px; margin-bottom: 16px; position: relative; overflow: hidden;
}
.hero::after {
    content:''; position: absolute; bottom: -50px; right: -50px;
    width: 220px; height: 220px; border-radius: 50%;
    background: radial-gradient(circle, rgba(245,158,11,.14), transparent 70%); pointer-events: none;
}
.hero h1 { font-size: 24px; font-weight: 700; margin: 0 0 4px; color: #fff; }
.hero p  { font-size: 13px; margin: 0; color: rgba(255,255,255,.6); }

.kpi-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 15px 16px 14px; position: relative; overflow: hidden; min-height: 92px;
    transition: transform .15s ease, border-color .15s ease;
}
.kpi-card:hover { transform: translateY(-2px); border-color: rgba(245,158,11,.35); }
.kpi-card::before {
    content:''; position: absolute; top:0; left:0; right:0; height:2px;
    background: var(--card-accent, var(--accent)); border-radius: 12px 12px 0 0;
}
.kpi-label { font-size: 10px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; color: var(--muted); margin-bottom: 9px; }
.kpi-value { font-size: 21px; font-weight: 700; line-height: 1; margin-bottom: 6px; color: var(--text); font-family: 'DM Mono', monospace; }
.kpi-sub { font-size: 11px; color: var(--muted); }

.sec-head { display:flex; align-items:center; gap:10px; margin: 6px 0 12px; }
.sec-head-bar { width:3px; height:18px; border-radius:3px; background: var(--accent); flex-shrink:0; }
.sec-head-text { font-size: 13px; font-weight: 700; color: var(--text); }
.sec-head-badge { margin-left:auto; font-size: 10px; color: var(--muted); font-family: 'DM Mono', monospace; }

.insight-box { background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 14px; padding: 13px 16px; margin: 6px 0 16px; }
.ins-title { font-size: 11px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
.ins-list { margin: 0; padding-left: 18px; color: var(--text); font-size: 13px; line-height: 1.55; }

.filter-bar { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; margin-bottom: 16px; }
.chip { display:inline-flex; align-items:center; gap:5px; background: var(--surface2); border:1px solid var(--border); border-radius:99px; padding:4px 12px; font-size:11px; color: var(--muted); margin: 2px 4px 8px 0; }

.reco-card { background: var(--surface); border: 1px solid var(--border); border-left: 5px solid var(--good); border-radius: 14px; padding: 18px 20px; line-height: 1.7; font-size: 14px; }

.sb-section { font-size: 10px; font-weight: 700; letter-spacing: 1.3px; text-transform: uppercase; color: var(--muted); margin: 16px 0 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
.sb-title { color: var(--text) !important; }
.sb-subtitle { color: var(--muted) !important; }

[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
[data-testid="stMetricLabel"] { font-size: 11px !important; color: var(--muted) !important; }
[data-testid="stMetricValue"] { font-size: 20px !important; font-family: 'DM Mono', monospace; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.js-plotly-plot .plotly { border-radius: 12px; overflow: hidden; }
::-webkit-scrollbar { width:5px; height:5px; } ::-webkit-scrollbar-thumb { background: var(--surface2); border-radius:4px; }
</style>
""",
    unsafe_allow_html=True,
)

PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(17,24,39,0)",
    plot_bgcolor="rgba(17,24,39,0)",
    font=dict(family="DM Sans", color="#9aa5be", size=11),
    margin=dict(t=16, b=16, l=8, r=8),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
    hoverlabel=dict(bgcolor="#1a2235", bordercolor="rgba(255,255,255,.12)", font=dict(family="DM Sans", size=12, color="#e8edf5")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(size=11)),
)

COLORS = {
    "amber": "#f59e0b", "blue": "#3b82f6", "red": "#f87171", "green": "#22d3a4",
    "purple": "#a78bfa", "warn": "#fbbf24", "muted": "#6b7a99",
}
REGIONAL_PALETTE = ["#f59e0b", "#3b82f6", "#22d3a4", "#a78bfa", "#f87171"]
KAT_COLOR = {"Regretted": "#f87171", "Non-Regretted": "#3b82f6", "Involuntary": "#6b7a99"}
PERF_COLOR = {"Istimewa": "#22d3a4", "Baik": "#3b82f6", "Cukup": "#fbbf24", "Kurang": "#f87171"}

DATA_PATH = "data/hc_data.xlsx"
PARQUET_DIR = Path("data/parquet")
WILAYAH_FOKUS = "Regional 5 - Wilayah Timur"


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_resource(show_spinner=False)
def _sheet_reader():
    """
    Returns a function that reads one sheet by name.

    Prefers the Parquet cache in data/parquet/ (dibuat oleh build_cache.py):
    membaca seluruh 8 sheet dari Parquet makan ~0,14 detik, sedangkan dari
    .xlsx ~3,4 detik — karena .xlsx harus unzip + parse XML per sel, dan
    sheet 'Data Kompensasi' saja berisi 34.916 baris.

    Kalau folder Parquet belum ada, otomatis jatuh balik ke .xlsx supaya
    aplikasi tetap jalan (hanya lebih lambat saat cold start).
    """
    if PARQUET_DIR.exists() and any(PARQUET_DIR.glob("*.parquet")):
        def read(sheet: str) -> pd.DataFrame:
            path = PARQUET_DIR / f"{sheet.lower().replace(' ', '_')}.parquet"
            return pd.read_parquet(path)
        return read, "parquet"

    xls = pd.ExcelFile(DATA_PATH)
    return (lambda sheet: xls.parse(sheet)), "xlsx"


@st.cache_data(show_spinner="Memuat data HC…")
def load_data():
    """
    Loads every sheet once, joins branch context onto each fact table, and
    derives the fields the dashboard needs (exit month, regretted flag, last
    compensation snapshot before exit).

    NOTE on data source: this is a fixed, anonymised case dataset (not a
    live public indicator), so there is no external API to poll — the
    correct approach is to read it from disk once and cache it. Swapping
    this for a database/API later only means replacing the reader below;
    every function downstream reads from the returned frames.
    """
    read, source = _sheet_reader()

    cabang = read("Data Cabang").rename(columns={"Branch Code": "kode_cabang", "Branch Name": "nama_cabang"})
    karyawan = read("Data Karyawan").rename(columns={"Branch Code": "kode_cabang"})
    reason = read("Reason Out")
    perf = read("Performance Data")
    komp = read("Data Kompensasi")
    perfcab = read("Performance Cabang")
    eng = read("Engagement Survey")

    # Parquet menyimpan kolom teks sebagai category; kembalikan ke string
    # supaya merge & .str accessor berperilaku sama seperti versi xlsx.
    for _df in (cabang, karyawan, reason, perf, komp, perfcab, eng):
        for _c in _df.columns:
            if isinstance(_df[_c].dtype, pd.CategoricalDtype):
                _df[_c] = _df[_c].astype(str)

    cabang["kode_cabang"] = cabang["kode_cabang"].astype(str).str.strip()
    branch_ctx = cabang[["kode_cabang", "nama_cabang", "Regional", "Kota"]]

    karyawan = karyawan.merge(branch_ctx, on="kode_cabang", how="left")
    reason = reason.merge(branch_ctx, on="kode_cabang", how="left")
    perfcab = perfcab.merge(branch_ctx, on="kode_cabang", how="left")
    eng = eng.merge(branch_ctx, on="kode_cabang", how="left")
    komp = komp.merge(branch_ctx, on="kode_cabang", how="left")

    reason["bulan_keluar"] = reason["tanggal_keluar"].dt.to_period("M").dt.to_timestamp()
    reason["tahun_keluar"] = reason["tanggal_keluar"].dt.year
    reason["is_regretted"] = reason["kategori_keluar"] == "Regretted"
    reason["kohort_masa_kerja"] = pd.cut(
        reason["masa_kerja_bulan"],
        bins=[-1, 12, 24, 48, 84, 10_000],
        labels=["<1 th", "1-2 th", "2-4 th", "4-7 th", ">7 th"],
    )

    komp_last = (
        komp.sort_values("periode")
        .groupby("nik", as_index=False)
        .last()[["nik", "gaji_pokok_juta", "tunjangan_tetap_juta", "insentif_target_juta", "insentif_realisasi_juta"]]
    )
    komp_last["rasio_insentif"] = (
        komp_last["insentif_realisasi_juta"] / komp_last["insentif_target_juta"].replace(0, np.nan)
    ) * 100
    reason = reason.merge(komp_last, on="nik", how="left")

    eng_latest_year = int(eng["periode_survey"].max())
    eng_latest = eng[eng["periode_survey"] == eng_latest_year].copy()

    return dict(
        cabang=cabang, karyawan=karyawan, reason=reason, perf=perf,
        komp=komp, perfcab=perfcab, eng=eng, eng_latest=eng_latest,
        eng_latest_year=eng_latest_year, source=source,
    )


# =========================================================
# HELPERS
# =========================================================
def sec(title: str, note: str = "", color: str = "var(--accent)") -> None:
    badge = f'<span class="sec-head-badge">{note}</span>' if note else ""
    st.markdown(
        f'<div class="sec-head"><div class="sec-head-bar" style="background:{color}"></div>'
        f'<div class="sec-head-text">{title}</div>{badge}</div>',
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str, sub: str = "", color: str = "var(--accent)") -> str:
    return f"""<div class="kpi-card" style="--card-accent:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""


def insight_callout(title: str, bullets: List[str], color: str = COLORS["amber"]) -> None:
    if not bullets:
        return
    items = "".join(f"<li style='margin-bottom:4px'>{b}</li>" for b in bullets)
    st.markdown(
        f"""<div class="insight-box" style="border-left-color:{color}">
        <div class="ins-title">💡 {title}</div><ul class="ins-list">{items}</ul></div>""",
        unsafe_allow_html=True,
    )


def apply_layout(fig, h: int = 320, legend_h: bool = False, **kwargs):
    layout = {**PLOT_LAYOUT, "height": h, **kwargs}
    if legend_h:
        layout["legend"] = {**layout.get("legend", {}), "orientation": "h", "y": -0.22, "x": 0}
    fig.update_layout(**layout)
    return fig


def fmt_pct(v, digits=1):
    return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{digits}f}%"


def fmt_n(v, digits=0):
    return "—" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:,.{digits}f}"


# =========================================================
# LOAD
# =========================================================
with st.spinner("Memuat data…"):
    D = load_data()

reason_all = D["reason"]
karyawan = D["karyawan"]
perfcab = D["perfcab"]
eng_latest = D["eng_latest"]
komp = D["komp"]

regional_list = sorted(reason_all["Regional"].dropna().unique().tolist())
min_date, max_date = reason_all["tanggal_keluar"].min(), reason_all["tanggal_keluar"].max()

# =========================================================
# SESSION DEFAULTS
# =========================================================
if "panel_open" not in st.session_state:
    st.session_state.panel_open = True

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        """
    <div style="padding:16px 4px 6px;text-align:center;">
      <div style="font-size:34px;line-height:1">🧭</div>
      <div class="sb-title" style="font-weight:700;font-size:15px;margin-top:8px;">HC Analytics — Case #1</div>
      <div class="sb-subtitle" style="font-size:11px;margin-top:2px;">Regretted Attrition · Adira Finance</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-section">Filter Utama</div>', unsafe_allow_html=True)

    default_regional = [WILAYAH_FOKUS] if WILAYAH_FOKUS in regional_list else regional_list
    sel_regional = st.multiselect("🏢 Regional", regional_list, default=default_regional, key="f_regional")

    default_end = max_date.date()
    default_start = (max_date - pd.DateOffset(months=9)).date()
    date_range = st.date_input(
        "📅 Periode keluar",
        value=(default_start, default_end),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="f_dates",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d_start, d_end = date_range
    else:
        d_start, d_end = default_start, default_end

    st.caption("Default: 9 bulan terakhir · Regional 5 - Wilayah Timur (sesuai konteks kasus)")

    st.markdown('<div class="sb-section">Workspace</div>', unsafe_allow_html=True)
    st.toggle("Tampilkan panel insight", key="panel_open")

    st.markdown('<div class="sb-section">Sumber Data</div>', unsafe_allow_html=True)
    st.markdown(
        """<div style='font-size:11px;color:#6b7a99;line-height:1.75;'>
        📁 Master Karyawan · Log Attrition 24 bulan<br>
        💰 Kompensasi & Insentif · 📈 Performa 3 periode<br>
        🏢 Data bisnis cabang · 🙂 Engagement Survey<br><br>
        <i>Dataset dummy, telah dianonimkan.</i>
        </div>""",
        unsafe_allow_html=True,
    )

# apply filters
mask = (
    reason_all["Regional"].isin(sel_regional)
    & (reason_all["tanggal_keluar"].dt.date >= d_start)
    & (reason_all["tanggal_keluar"].dt.date <= d_end)
)
df = reason_all[mask].copy()
reg = df[df["is_regretted"]].copy()

scope_chip = f"{len(sel_regional)} regional dipilih" if len(sel_regional) != 1 else sel_regional[0]

# =========================================================
# HERO
# =========================================================
st.markdown(
    f"""
<div class="hero">
  <h1>🧭 Regretted Attrition Dashboard — Wilayah Timur</h1>
  <p>HC Analytics Case #1 · {scope_chip} · {pd.Timestamp(d_start):%b %Y} – {pd.Timestamp(d_end):%b %Y} ·
  Argumen data untuk forum Opscomm</p>
</div>
""",
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("Tidak ada data keluar pada kombinasi filter ini. Perluas regional atau periode di sidebar.")
    st.stop()

# =========================================================
# TABS
# =========================================================
tab_summary, tab_regional, tab_cohort, tab_comp, tab_reco = st.tabs(
    ["📊 Ringkasan", "🏢 Regional & Cabang", "🧬 Kohort & Alasan", "💰 Kompensasi & Engagement", "✅ Rekomendasi"]
)

# =========================================================
# TAB 1 — RINGKASAN  (≤6 visuals, satu layar — sesuai deliverable kasus)
# =========================================================
with tab_summary:
    total_keluar = len(df)
    total_regretted = int(df["is_regretted"].sum())
    regretted_rate = total_regretted / total_keluar * 100 if total_keluar else np.nan
    avg_tenure_reg = reg["masa_kerja_bulan"].mean()
    flag_df = reg[reg["kategori_performa_terakhir"].isin(["Baik", "Istimewa"]) & reg["masa_kerja_bulan"].between(24, 48)]
    pct_flag = len(flag_df) / total_regretted * 100 if total_regretted else np.nan

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi("Total Keluar", fmt_n(total_keluar), "periode & regional terpilih", COLORS["blue"]), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Regretted", fmt_n(total_regretted), f"{fmt_pct(regretted_rate)} dari total keluar", COLORS["red"]), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("Avg. Masa Kerja Regretted", f"{fmt_n(avg_tenure_reg,1)} bln", "saat keluar", COLORS["amber"]), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("Performa Baik+, 2–4 th", f"{fmt_n(len(flag_df))} orang", f"{fmt_pct(pct_flag)} dari regretted", COLORS["purple"]), unsafe_allow_html=True)
    with c5:
        eng_scope = eng_latest[eng_latest["Regional"].isin(sel_regional)]
        st.markdown(kpi("Engagement Index", fmt_n(eng_scope["engagement_index"].mean(), 1), f"rata-rata {D['eng_latest_year']}", COLORS["green"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        sec("Tren Bulanan Karyawan Keluar", "berdasarkan kategori")
        trend = df.groupby([pd.Grouper(key="bulan_keluar", freq="MS"), "kategori_keluar"]).size().reset_index(name="n")
        fig1 = px.area(trend, x="bulan_keluar", y="n", color="kategori_keluar",
                        color_discrete_map=KAT_COLOR, labels={"bulan_keluar": "", "n": "Jumlah keluar", "kategori_keluar": ""})
        fig1.update_traces(hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: <b>%{y}</b> orang<extra></extra>")
        apply_layout(fig1, h=300, legend_h=True)
        st.plotly_chart(fig1, use_container_width=True, key="c1")

    with col_r:
        sec("Top Cabang — Jumlah Regretted", f"{pd.Timestamp(d_start):%b %Y}–{pd.Timestamp(d_end):%b %Y}", COLORS["red"])
        top_cab = reg.groupby(["nama_cabang", "Regional"]).size().reset_index(name="n").nlargest(10, "n")
        top_cab["is_focus"] = top_cab["Regional"] == WILAYAH_FOKUS
        fig2 = go.Figure(go.Bar(
            x=top_cab["n"], y=top_cab["nama_cabang"], orientation="h",
            marker_color=np.where(top_cab["is_focus"], COLORS["red"], "rgba(255,255,255,0.18)"),
            hovertemplate="<b>%{y}</b><br>Regretted: <b>%{x}</b><extra></extra>",
            text=top_cab["n"], textposition="outside", textfont=dict(size=10, color="#9aa5be"),
        ))
        fig2.update_yaxes(categoryorder="total ascending")
        apply_layout(fig2, h=300, xaxis=dict(title="Jumlah regretted", gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(title=""))
        st.plotly_chart(fig2, use_container_width=True, key="c2")

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        sec("Kategori Performa Terakhir — Regretted", "sebelum keluar", COLORS["purple"])
        perf_dist = reg["kategori_performa_terakhir"].value_counts().reset_index()
        perf_dist.columns = ["kategori", "n"]
        fig3 = go.Figure(go.Pie(
            labels=perf_dist["kategori"], values=perf_dist["n"], hole=0.55,
            marker=dict(colors=[PERF_COLOR.get(k, "#6b7a99") for k in perf_dist["kategori"]]),
            hovertemplate="<b>%{label}</b><br>%{value} orang (%{percent})<extra></extra>",
            textinfo="percent+label", textfont=dict(size=11),
        ))
        fig3.update_layout(height=290, **{k: v for k, v in PLOT_LAYOUT.items() if k not in ["xaxis", "yaxis", "margin"]}, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig3, use_container_width=True, key="c3")

    with col_r2:
        sec("Alasan Keluar Teratas — Regretted", "exit interview", COLORS["blue"])
        reason_top = reg["alasan_keluar_exit_interview"].value_counts().nlargest(8).reset_index()
        reason_top.columns = ["alasan", "n"]
        fig4 = go.Figure(go.Bar(
            x=reason_top["n"], y=reason_top["alasan"], orientation="h",
            marker_color=COLORS["blue"],
            hovertemplate="<b>%{y}</b><br>%{x} orang<extra></extra>",
            text=reason_top["n"], textposition="outside", textfont=dict(size=10, color="#9aa5be"),
        ))
        fig4.update_yaxes(categoryorder="total ascending")
        apply_layout(fig4, h=290, xaxis=dict(title="Jumlah", gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(title=""))
        st.plotly_chart(fig4, use_container_width=True, key="c4")

    col_l3, col_r3 = st.columns(2)
    with col_l3:
        sec("Distribusi Masa Kerja Saat Keluar", "regretted vs non-regretted", COLORS["amber"])
        fig5 = go.Figure()
        for kat, color in [("Regretted", COLORS["red"]), ("Non-Regretted", COLORS["blue"])]:
            sub = df[df["kategori_keluar"] == kat]["masa_kerja_bulan"]
            if not sub.empty:
                fig5.add_trace(go.Histogram(x=sub, name=kat, marker_color=color, opacity=0.65, nbinsx=24,
                                             hovertemplate=f"<b>{kat}</b><br>Masa kerja: %{{x}} bln<extra></extra>"))
        fig5.update_layout(barmode="overlay")
        apply_layout(fig5, h=300, legend_h=True, xaxis=dict(title="Masa kerja (bulan)"), yaxis=dict(title="Jumlah orang"))
        st.plotly_chart(fig5, use_container_width=True, key="c5")

    with col_r3:
        sec("Engagement vs Tingkat Regretted per Cabang", "bubble = jumlah MP", COLORS["green"])
        exit_by_cab = reg.groupby("kode_cabang").size().rename("regretted_n")
        hc_by_cab = karyawan[karyawan["Status Kekaryawan"] == "Aktif"].groupby("kode_cabang").size().rename("hc_aktif")
        cab_stats = pd.concat([exit_by_cab, hc_by_cab], axis=1).fillna(0)
        cab_stats["regretted_rate"] = np.where(cab_stats["hc_aktif"] > 0, cab_stats["regretted_n"] / cab_stats["hc_aktif"] * 100, np.nan)
        cab_stats = cab_stats.merge(eng_latest[["kode_cabang", "nama_cabang", "Regional", "engagement_index", "jumlah_responden"]], on="kode_cabang", how="inner")
        cab_stats = cab_stats[cab_stats["Regional"].isin(sel_regional)].dropna(subset=["regretted_rate", "engagement_index"])
        if not cab_stats.empty:
            fig6 = px.scatter(
                cab_stats, x="engagement_index", y="regretted_rate", size="jumlah_responden",
                hover_name="nama_cabang", color="Regional", color_discrete_sequence=REGIONAL_PALETTE, size_max=32,
                labels={"engagement_index": "Engagement Index", "regretted_rate": "Regretted / HC aktif (%)"},
            )
            fig6.update_traces(hovertemplate="<b>%{hovertext}</b><br>Engagement: %{x:.1f}<br>Regretted rate: %{y:.1f}%<extra></extra>")
            apply_layout(fig6, h=300, legend_h=True)
            st.plotly_chart(fig6, use_container_width=True, key="c6")
        else:
            st.info("Data engagement tidak tersedia untuk kombinasi filter ini.")

    if st.session_state.panel_open:
        bullets = [
            f"<b>{total_regretted}</b> dari {total_keluar} karyawan yang keluar ({fmt_pct(regretted_rate)}) tergolong <b>regretted</b>.",
            f"<b>{len(flag_df)} orang ({fmt_pct(pct_flag)})</b> dari regretted adalah performer <b>Baik/Istimewa</b> dengan masa kerja <b>2–4 tahun</b> — segmen paling mahal untuk diganti.",
            f"Rata-rata masa kerja saat keluar (regretted): <b>{fmt_n(avg_tenure_reg,1)} bulan</b>.",
        ]
        if not reason_top.empty:
            bullets.append(f"Alasan keluar #1: <b>{reason_top.iloc[0]['alasan']}</b> ({reason_top.iloc[0]['n']} orang).")
        insight_callout("Ringkasan Cepat", bullets)

# =========================================================
# TAB 2 — REGIONAL & CABANG
# =========================================================
with tab_regional:
    sec("Perbandingan Antar Regional", "seluruh regional, periode terpilih (mengabaikan filter regional di sidebar)")
    df_allreg = reason_all[(reason_all["tanggal_keluar"].dt.date >= d_start) & (reason_all["tanggal_keluar"].dt.date <= d_end)]
    reg_stats = df_allreg.groupby("Regional").agg(
        total_keluar=("nik", "count"),
        regretted=("is_regretted", "sum"),
    ).reset_index()
    reg_stats["regretted_rate"] = reg_stats["regretted"] / reg_stats["total_keluar"] * 100
    reg_stats["is_focus"] = reg_stats["Regional"] == WILAYAH_FOKUS
    reg_stats = reg_stats.sort_values("regretted_rate", ascending=False)

    col_a, col_b = st.columns([1.3, 1])
    with col_a:
        fig_r1 = go.Figure(go.Bar(
            x=reg_stats["Regional"], y=reg_stats["regretted_rate"],
            marker_color=np.where(reg_stats["is_focus"], COLORS["red"], "rgba(255,255,255,0.18)"),
            text=reg_stats["regretted_rate"].round(1).astype(str) + "%", textposition="outside",
            hovertemplate="<b>%{x}</b><br>Regretted rate: %{y:.1f}%<br>Total keluar: %{customdata[0]}<extra></extra>",
            customdata=reg_stats[["total_keluar"]],
        ))
        apply_layout(fig_r1, h=330, xaxis=dict(tickangle=-15, title=""), yaxis=dict(title="Regretted / total keluar (%)"))
        st.plotly_chart(fig_r1, use_container_width=True, key="r1")
    with col_b:
        st.dataframe(
            reg_stats[["Regional", "total_keluar", "regretted", "regretted_rate"]]
            .rename(columns={"total_keluar": "Total Keluar", "regretted": "Regretted", "regretted_rate": "Rate (%)"})
            .style.format({"Rate (%)": "{:.1f}"})
            .background_gradient(cmap="Reds", subset=["Rate (%)"]),
            use_container_width=True, height=330,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    sec(f"Ranking Cabang — {scope_chip}", "diurutkan berdasarkan jumlah regretted", COLORS["red"])
    cab_rank = df[df["is_regretted"]].groupby(["nama_cabang", "Regional", "Kota"]).agg(
        regretted=("nik", "count"),
        avg_tenure=("masa_kerja_bulan", "mean"),
        avg_performa=("nilai_performa_terakhir", "mean"),
    ).reset_index().sort_values("regretted", ascending=False)
    st.dataframe(
        cab_rank.rename(columns={"nama_cabang": "Cabang", "regretted": "Regretted", "avg_tenure": "Avg Masa Kerja (bln)", "avg_performa": "Avg Nilai Performa"})
        .style.format({"Avg Masa Kerja (bln)": "{:.1f}", "Avg Nilai Performa": "{:.2f}"})
        .background_gradient(cmap="Reds", subset=["Regretted"]),
        use_container_width=True, height=320,
    )

    sec("Operasional Cabang — Fokus Wilayah Timur", "portofolio, pencapaian target & NPL", COLORS["blue"])
    pc = perfcab[perfcab["Regional"].isin(sel_regional)].copy()
    if not pc.empty:
        pc_trend = pc.groupby(pd.PeriodIndex(pc["periode"], freq="M").to_timestamp()).agg(
            pencapaian=("pencapaian_target_persen", "mean"), npl=("npl_persen", "mean")
        ).reset_index().rename(columns={"index": "periode"})
        fig_r2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_r2.add_trace(go.Scatter(x=pc_trend["periode"], y=pc_trend["pencapaian"], name="Pencapaian Target (%)",
                                     line=dict(color=COLORS["blue"], width=2.6), mode="lines+markers"), secondary_y=False)
        fig_r2.add_trace(go.Scatter(x=pc_trend["periode"], y=pc_trend["npl"], name="NPL (%)",
                                     line=dict(color=COLORS["red"], width=2.6, dash="dot"), mode="lines+markers"), secondary_y=True)
        fig_r2.update_yaxes(title_text="Pencapaian Target (%)", secondary_y=False)
        fig_r2.update_yaxes(title_text="NPL (%)", secondary_y=True)
        apply_layout(fig_r2, h=300, legend_h=True)
        st.plotly_chart(fig_r2, use_container_width=True, key="r3")
        insight_callout("Insight Operasional", [
            "Cabang tetap mencatat pencapaian target yang relatif sehat meskipun attrition tinggi — mengindikasikan <b>beban kerja tertumpu pada karyawan yang bertahan</b>, bukan turunnya bisnis.",
            "Ini konsisten dengan alasan keluar teratas: <b>beban kerja terlalu berat</b> dan <b>jenjang karir tidak jelas</b>.",
        ])

# =========================================================
# TAB 3 — KOHORT & ALASAN
# =========================================================
with tab_cohort:
    col_l, col_r = st.columns(2)
    with col_l:
        sec("Regretted per Kohort Masa Kerja", scope_chip)
        cohort = reg["kohort_masa_kerja"].value_counts().reindex(["<1 th", "1-2 th", "2-4 th", "4-7 th", ">7 th"]).reset_index()
        cohort.columns = ["kohort", "n"]
        fig_k1 = go.Figure(go.Bar(
            x=cohort["kohort"], y=cohort["n"],
            marker_color=np.where(cohort["kohort"] == "2-4 th", COLORS["red"], "rgba(255,255,255,0.18)"),
            text=cohort["n"], textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y} orang regretted<extra></extra>",
        ))
        apply_layout(fig_k1, h=300, yaxis=dict(title="Jumlah"), xaxis=dict(title=""))
        st.plotly_chart(fig_k1, use_container_width=True, key="k1")

    with col_r:
        sec("Regretted per Fungsi & Level", "heatmap", COLORS["purple"])
        heat = reg.groupby(["Function" if "Function" in reg.columns else "fungsi", "level"]).size().unstack(fill_value=0) if "fungsi" in reg.columns else pd.DataFrame()
        fungsi_col = "fungsi" if "fungsi" in reg.columns else "Function"
        heat = reg.groupby([fungsi_col, "level"]).size().unstack(fill_value=0)
        if not heat.empty:
            fig_k2 = px.imshow(heat, text_auto=True, color_continuous_scale="OrRd", aspect="auto",
                                labels=dict(color="Regretted"))
            fig_k2.update_traces(hovertemplate="<b>%{y}</b> · %{x}<br>Regretted: %{z}<extra></extra>")
            apply_layout(fig_k2, h=300)
            st.plotly_chart(fig_k2, use_container_width=True, key="k2")

    sec("Alasan Keluar per Fungsi", "regretted only, top 6 alasan", COLORS["blue"])
    fungsi_col = "fungsi" if "fungsi" in reg.columns else "Function"
    top_alasan = reg["alasan_keluar_exit_interview"].value_counts().nlargest(6).index.tolist()
    heat2_df = reg[reg["alasan_keluar_exit_interview"].isin(top_alasan)]
    heat2 = heat2_df.groupby([fungsi_col, "alasan_keluar_exit_interview"]).size().unstack(fill_value=0)
    if not heat2.empty:
        fig_k3 = px.imshow(heat2, text_auto=True, color_continuous_scale="Blues", aspect="auto", labels=dict(color="Jumlah"))
        fig_k3.update_traces(hovertemplate="<b>%{y}</b><br>%{x}: %{z} orang<extra></extra>")
        apply_layout(fig_k3, h=320, xaxis=dict(tickangle=-25))
        st.plotly_chart(fig_k3, use_container_width=True, key="k3")

    insight_callout("Insight Kohort", [
        "Kohort <b>2–4 tahun</b> masa kerja adalah titik rawan terbesar — karyawan sudah cukup terlatih (biaya ramp-up sudah 'terbayar') namun belum mendapat kejelasan jenjang karir berikutnya.",
        "Fungsi <b>Sales</b> dan <b>Collection</b> biasanya paling sensitif terhadap beban kerja dan struktur insentif — perhatikan pola pada heatmap di atas untuk cabang di lingkup filter Anda.",
    ], color=COLORS["purple"])

# =========================================================
# TAB 4 — KOMPENSASI & ENGAGEMENT
# =========================================================
with tab_comp:
    col_l, col_r = st.columns(2)
    with col_l:
        sec("Rasio Realisasi Insentif Sebelum Keluar", "regretted vs non-regretted", COLORS["amber"])
        fig_m1 = go.Figure()
        for kat, color in [("Regretted", COLORS["red"]), ("Non-Regretted", COLORS["blue"])]:
            sub = df[(df["kategori_keluar"] == kat)]["rasio_insentif"].dropna()
            if not sub.empty:
                fig_m1.add_trace(go.Box(y=sub, name=kat, marker_color=color, boxmean=True))
        apply_layout(fig_m1, h=320, yaxis=dict(title="Realisasi / Target Insentif (%)"), showlegend=False)
        st.plotly_chart(fig_m1, use_container_width=True, key="m1")

    with col_r:
        sec("Komponen Engagement — Wilayah Timur vs Regional Lain", f"survei {D['eng_latest_year']}", COLORS["green"])
        comp_cols = ["skor_atasan_langsung", "skor_jenjang_karir", "skor_kompensasi", "skor_beban_kerja", "skor_lingkungan_kerja"]
        comp_labels = ["Atasan Langsung", "Jenjang Karir", "Kompensasi", "Beban Kerja", "Lingkungan Kerja"]
        wt = eng_latest[eng_latest["Regional"] == WILAYAH_FOKUS][comp_cols].mean()
        other = eng_latest[eng_latest["Regional"] != WILAYAH_FOKUS][comp_cols].mean()
        fig_m2 = go.Figure()
        fig_m2.add_trace(go.Scatterpolar(r=wt.tolist() + [wt.tolist()[0]], theta=comp_labels + [comp_labels[0]],
                                          fill="toself", name="Wilayah Timur", line=dict(color=COLORS["red"], width=2.4)))
        fig_m2.add_trace(go.Scatterpolar(r=other.tolist() + [other.tolist()[0]], theta=comp_labels + [comp_labels[0]],
                                          fill="toself", name="Regional Lain", line=dict(color=COLORS["blue"], width=2.4)))
        fig_m2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                              polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                              legend=dict(orientation="h", y=-0.15), height=320, margin=dict(t=20, b=30, l=20, r=20))
        st.plotly_chart(fig_m2, use_container_width=True, key="m2")

    sec("Tren Engagement Index per Cabang — Wilayah Timur", "2024 vs 2025", COLORS["purple"])
    eng_wt = D["eng"][D["eng"]["Regional"] == WILAYAH_FOKUS]
    if not eng_wt.empty:
        fig_m3 = px.line(eng_wt.sort_values("periode_survey"), x="periode_survey", y="engagement_index", color="nama_cabang",
                          markers=True, color_discrete_sequence=REGIONAL_PALETTE + px.colors.qualitative.Set3,
                          labels={"periode_survey": "Tahun survei", "engagement_index": "Engagement Index", "nama_cabang": ""})
        fig_m3.update_xaxes(dtick=1)
        apply_layout(fig_m3, h=300, legend_h=True)
        st.plotly_chart(fig_m3, use_container_width=True, key="m3")

    insight_callout("Insight Kompensasi & Engagement", [
        "Skor <b>jenjang karir</b> dan <b>beban kerja</b> di Wilayah Timur cenderung tertinggal dibanding regional lain — sejalan dengan alasan keluar teratas pada tab Ringkasan.",
        "Realisasi insentif yang lebih rendah pada karyawan regretted memperkuat sinyal bahwa <b>struktur insentif saat ini kurang kompetitif</b> untuk menahan talent terbaik.",
    ], color=COLORS["green"])

# =========================================================
# TAB 5 — REKOMENDASI
# =========================================================
with tab_reco:
    sec("Ringkasan Argumen", "berbasis data pada filter aktif")
    top_alasan_name = reg["alasan_keluar_exit_interview"].value_counts().idxmax() if not reg.empty else "—"
    st.markdown(
        f"""
<div class="reco-card">

**Apa yang terjadi.** Dalam periode {pd.Timestamp(d_start):%b %Y}–{pd.Timestamp(d_end):%b %Y} di {scope_chip},
tercatat <b>{total_keluar} karyawan keluar</b>, di mana <b>{total_regretted} orang ({fmt_pct(regretted_rate)})</b>
tergolong <i>regretted attrition</i>. Yang paling mengkhawatirkan: <b>{len(flag_df)} orang ({fmt_pct(pct_flag)})</b>
dari kelompok regretted adalah performer <b>Baik/Istimewa</b> dengan masa kerja <b>2–4 tahun</b> — segmen yang
sudah melewati fase ramp-up dan paling mahal untuk digantikan.

**Mengapa ini terjadi.** Alasan keluar paling dominan adalah <b>{top_alasan_name}</b>. Ini diperkuat oleh skor
engagement <b>jenjang karir</b> dan <b>beban kerja</b> di Wilayah Timur yang tertinggal dibanding regional lain,
serta realisasi insentif yang secara konsisten lebih rendah pada kelompok regretted dibanding yang bertahan.
Pada saat yang sama, cabang-cabang ini tetap mengejar pencapaian target — indikasi bahwa beban kerja kini
bertumpu pada tim yang semakin menyusut.

**Rekomendasi kebijakan (satu keputusan untuk forum Opscomm).**
Luncurkan **program retensi bertarget untuk kohort masa-kerja 2–4 tahun berperforma Baik/Istimewa** di
cabang-cabang Wilayah Timur dengan regretted rate tertinggi, berupa: (1) jalur promosi/rotasi lintas cabang yang
dipercepat dan dikomunikasikan eksplisit dalam 90 hari, (2) penyesuaian struktur insentif agar realisasi lebih
kompetitif terhadap target, dan (3) peninjauan span-of-control/beban kerja di cabang dengan pencapaian target
tinggi namun NPL & attrition ikut naik. Ukur keberhasilannya lewat penurunan regretted rate pada kohort ini di
2 siklus survei engagement berikutnya.

</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    sec("Estimasi Dampak Biaya Tidak Langsung", "ilustratif, berbasis kompensasi terakhir kelompok regretted", COLORS["amber"])
    reg_comp = reg.dropna(subset=["gaji_pokok_juta"])
    if not reg_comp.empty:
        est_monthly_comp = (reg_comp["gaji_pokok_juta"] + reg_comp["tunjangan_tetap_juta"]).sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Jumlah Regretted (Baik+, 2–4 th)", fmt_n(len(flag_df)))
        c2.metric("Total Komp. Bulanan Terakhir — Regretted", f"Rp {est_monthly_comp:,.0f} Jt")
        c3.metric("Rata-rata Nilai Performa Terakhir", f"{reg['nilai_performa_terakhir'].mean():.2f}" if not reg.empty else "—")
        st.caption("Angka komponen biaya rekrutmen/ramp-up tidak tersedia di dataset ini; nilai di atas hanya menggambarkan skala kompensasi bulanan yang hilang dari kelompok regretted, sebagai proksi kasar dampak finansial.")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "<div style='margin-top:24px;font-size:11px;color:#6b7a99;text-align:center;'>"
    "HC Analytics Case #1 · Data dummy dan telah dianonimkan · Dibuat dengan Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True,
)