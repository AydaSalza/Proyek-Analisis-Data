from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")


# ---------------------------------------------------------------- data
@st.cache_data
def load_data():
    hour_df = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    day_df = pd.read_csv(BASE_DIR / "day_clean.csv", parse_dates=["dteday"])
    return hour_df, day_df


hour_all, day_all = load_data()

SEASON_ORDER = ["Dingin", "Semi", "Panas", "Gugur"]
WEATHER_ORDER = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"]
TEMP_ORDER = ["Dingin (<10°C)", "Sejuk (10-20°C)", "Hangat (20-30°C)", "Panas (>30°C)"]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

# ------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🚲 Filter")
    min_date, max_date = day_all["dteday"].min().date(), day_all["dteday"].max().date()
    date_range = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    seasons = st.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
    weathers = st.multiselect("Kondisi cuaca", WEATHER_ORDER, default=WEATHER_ORDER)
    st.caption("Sumber data: Capital Bikeshare, Washington D.C. (2011-2012).")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    st.info("Pilih tanggal awal dan tanggal akhir pada filter.")
    st.stop()

day_f = day_all[
    day_all["dteday"].between(start, end)
    & day_all["season_label"].isin(seasons)
    & day_all["weather_label"].isin(weathers)
]
# data per jam: ikuti hari-hari yang lolos filter harian
hour_f = hour_all[hour_all["dteday"].isin(day_f["dteday"])]

# ---------------------------------------------------------------- header
st.title("Dashboard Analisis Penyewaan Sepeda (Bike Sharing)")
st.markdown("Pola penyewaan berdasarkan jam, cuaca/suhu, serta tren bulanan dan komposisi pengguna.")

if day_f.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Ubah filter pada sidebar.")
    st.stop()

# ------------------------------------------------------------------ KPI
total = int(day_f["cnt"].sum())
avg_day = day_f["cnt"].mean()
reg_share = day_f["registered"].sum() / total
peak_hour = hour_f.groupby("hr")["cnt"].mean().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{total:,}")
c2.metric("Rata-rata per hari", f"{avg_day:,.0f}")
c3.metric("Pengguna registered", f"{reg_share:.0%}")
c4.metric("Jam puncak (rata-rata)", f"{peak_hour:02d}:00")

st.divider()

# ------------------------------------------------------ pertanyaan 1
st.subheader("1. Pola penyewaan per jam: hari kerja vs akhir pekan/libur")
hourly = hour_f.groupby(["day_type", "hr"])["cnt"].mean().unstack(0)
colors = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}

fig, ax = plt.subplots(figsize=(11, 4.5))
for tipe in hourly.columns:
    ax.plot(hourly.index, hourly[tipe], marker="o", linewidth=2, label=tipe, color=colors[tipe])
    pk = hourly[tipe].idxmax()
    ax.annotate(
        f"{pk:02d}:00 ({hourly[tipe].max():.0f})",
        (pk, hourly[tipe].max()),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=9,
        color=colors[tipe],
    )
if "Hari Kerja" in hourly.columns:
    pagi = hourly.loc[6:10, "Hari Kerja"].dropna()
    if not pagi.empty:
        ax.annotate(
            f"{pagi.idxmax():02d}:00 ({pagi.max():.0f})",
            (pagi.idxmax(), pagi.max()),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9,
            color=colors["Hari Kerja"],
        )
ax.set_xticks(range(24))
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata penyewaan per jam")
ax.legend(title="Jenis hari")
sns.despine()
st.pyplot(fig)
st.caption(
    "Hari kerja memiliki dua puncak (pagi dan sore, pola komuter), sedangkan akhir pekan/libur "
    "memiliki satu puncak landai pada siang hari (pola rekreasi)."
)

# time-of-day grouping
def time_of_day(h):
    if h < 6:
        return "Dini Hari (00-05)"
    if h < 11:
        return "Pagi (06-10)"
    if h < 15:
        return "Siang (11-14)"
    if h < 19:
        return "Sore (15-18)"
    return "Malam (19-23)"


time_order = ["Dini Hari (00-05)", "Pagi (06-10)", "Siang (11-14)", "Sore (15-18)", "Malam (19-23)"]
tod = hour_f.assign(periode=hour_f["hr"].apply(time_of_day))
tod = tod.groupby(["periode", "day_type"])["cnt"].mean().unstack().reindex(time_order).round(0)
with st.expander("Rata-rata penyewaan per periode hari (manual grouping)"):
    st.dataframe(tod)

st.divider()

# ------------------------------------------------------ pertanyaan 2
st.subheader("2. Pengaruh cuaca dan suhu terhadap penyewaan harian")
left, right = st.columns(2)

with left:
    weather_avg = day_f.groupby("weather_label")["cnt"].mean().reindex(WEATHER_ORDER).dropna()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    palette = {"Cerah": "#2ca02c", "Berkabut/Berawan": "#bdbdbd", "Hujan/Salju Ringan": "#d62728"}
    bars = ax.bar(weather_avg.index, weather_avg.values, color=[palette[w] for w in weather_avg.index])
    base = weather_avg.get("Cerah", np.nan)
    for b, v, name in zip(bars, weather_avg.values, weather_avg.index):
        txt = f"{v:,.0f}"
        if name != "Cerah" and not np.isnan(base):
            txt += f"\n({(v - base) / base:+.0%})"
        ax.text(b.get_x() + b.get_width() / 2, v + weather_avg.max() * 0.01, txt, ha="center", fontsize=9)
    ax.set_ylim(0, weather_avg.max() * 1.2)
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_title("Berdasarkan kondisi cuaca", fontweight="bold")
    plt.xticks(rotation=10)
    sns.despine()
    st.pyplot(fig)

with right:
    temp_bins = [-np.inf, 10, 20, 30, np.inf]
    d = day_f.assign(temp_cat=pd.cut(day_f["temp_c"], bins=temp_bins, labels=TEMP_ORDER, right=False))
    temp_avg = d.groupby("temp_cat", observed=True)["cnt"].agg(["mean", "count"]).reindex(TEMP_ORDER).dropna()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    cols = ["#bdbdbd"] * len(temp_avg)
    cols[int(np.argmax(temp_avg["mean"].values))] = "#2ca02c"
    bars = ax.bar(temp_avg.index.astype(str), temp_avg["mean"], color=cols)
    for b, v, n in zip(bars, temp_avg["mean"], temp_avg["count"]):
        ax.text(b.get_x() + b.get_width() / 2, v + temp_avg["mean"].max() * 0.01,
                f"{v:,.0f}\n(n={int(n)})", ha="center", fontsize=9)
    ax.set_ylim(0, temp_avg["mean"].max() * 1.2)
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_title("Berdasarkan kategori suhu (binning)", fontweight="bold")
    plt.xticks(rotation=10)
    sns.despine()
    st.pyplot(fig)

st.caption(
    "Hujan/salju ringan menekan penyewaan paling besar dibanding cuaca cerah, dan penyewaan "
    "tertinggi terjadi pada suhu hangat (20-30°C). Perhatikan jumlah hari (n) pada tiap kelompok."
)

st.divider()

# ------------------------------------------------------ pertanyaan 3
st.subheader("3. Tren bulanan, pertumbuhan tahunan, dan komposisi pengguna")
left, right = st.columns([2, 1])

with left:
    monthly = day_f.groupby(["year", "mnth"])["cnt"].mean().unstack(0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for yr, col in zip([2011, 2012], ["#9ecae1", "#08519c"]):
        if yr in monthly.columns:
            ax.plot(monthly.index, monthly[yr], marker="o", linewidth=2, label=str(yr), color=col)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_NAMES)
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_title("Tren rata-rata penyewaan harian per bulan", fontweight="bold")
    ax.legend(title="Tahun")
    sns.despine()
    st.pyplot(fig)

with right:
    yearly = day_f.groupby("year")[["cnt", "casual", "registered"]].sum()
    comp = yearly[["registered", "casual"]].div(yearly["cnt"], axis=0) * 100
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    comp.plot(kind="bar", stacked=True, ax=ax, color=["#08519c", "#fd8d3c"], rot=0)
    for c in ax.containers:
        ax.bar_label(c, fmt="%.0f%%", label_type="center", color="white", fontsize=10)
    ax.set_xlabel("")
    ax.set_ylabel("% dari total penyewaan")
    ax.set_title("Komposisi pengguna", fontweight="bold")
    ax.legend(title="Tipe", loc="lower right")
    sns.despine()
    st.pyplot(fig)

if {2011, 2012}.issubset(yearly.index):
    growth = yearly.loc[2012, "cnt"] / yearly.loc[2011, "cnt"] - 1
    st.info(
        f"Total penyewaan pada rentang terpilih: {yearly.loc[2012, 'cnt']:,} (2012) vs "
        f"{yearly.loc[2011, 'cnt']:,} (2011), pertumbuhan {growth:+.1%}. "
        "Bandingkan dengan filter penuh (2011-2012) untuk gambaran tahunan yang adil."
    )
else:
    st.info("Pertumbuhan tahunan hanya dapat dihitung bila rentang tanggal mencakup 2011 dan 2012.")

st.divider()
st.caption("Proyek Analisis Data - Bike Sharing Dataset (Fanaee-T & Gama, 2013).")
