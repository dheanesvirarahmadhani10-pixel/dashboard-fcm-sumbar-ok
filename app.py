# ======================================================
# DASHBOARD SEGMENTASI MUTU PENDIDIKAN SUMATERA BARAT
# Metode: Fuzzy C-Means Clustering
# ======================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json

# ======================================================
# KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="Segmentasi Mutu Pendidikan Sumatera Barat",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# STYLE TAMBAHAN (PROFESIONAL)
# ======================================================
st.markdown("""
<style>
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
}
.metric-box {
    background-color: #f5f7fa;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.metric-title {
    font-size: 14px;
    color: #6c757d;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #0d6efd;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    return pd.read_csv("hasil_klaster_fcm_sumbar.csv")

df = load_data()

# ======================================================
# NORMALISASI NAMA WILAYAH (WAJIB UNTUK PETA)
# ======================================================
def normalisasi_nama(x):
    return (
        x.replace("Kabupaten ", "")
         .replace("Kota ", "")
         .strip()
    )

df["nama_peta"] = df["Kabupaten_Kota"].apply(normalisasi_nama)

# ======================================================
# LOAD GEOJSON
# ======================================================
with open("Kabupaten-Kota (Provinsi Sumatera Barat).geojson", encoding="utf-8") as f:
    geojson_sumbar = json.load(f)

# ======================================================
# VARIABEL INDIKATOR
# ======================================================
features = [
    "APM_SD",
    "APM_SMP",
    "APM_SMA",
    "HLS",
    "RLS",
    "Lulus_SMA_Plus"
]

# ======================================================
# HEADER
# ======================================================
st.title("📊 Dashboard Segmentasi Mutu Pendidikan")
st.markdown(
    """
    **Provinsi Sumatera Barat**  
    Metode **Fuzzy C-Means Clustering** untuk mendukung perumusan kebijakan
    pendidikan berbasis data
    """
)
st.markdown("---")

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.title("⚙️ Kontrol Dashboard")

cluster_option = st.sidebar.selectbox(
    "Pilih Klaster Wilayah",
    ["Semua Klaster", "Cluster 1", "Cluster 2", "Cluster 3"]
)

st.sidebar.info(
    "Setiap wilayah memiliki **derajat keanggotaan** pada masing-masing klaster "
    "sesuai karakteristik Fuzzy C-Means."
)

# ======================================================
# FILTER DATA
# ======================================================
if cluster_option != "Semua Klaster":
    cluster_num = int(cluster_option.split()[-1])
    df_filtered = df[df["Cluster"] == cluster_num]
else:
    df_filtered = df.copy()

# ======================================================
# KPI
# ======================================================
st.markdown('<div class="section-title">📌 Ringkasan Utama</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Jumlah Wilayah Terpilih</div>
        <div class="metric-value">{len(df_filtered)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Total Kabupaten/Kota</div>
        <div class="metric-value">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Jumlah Klaster</div>
        <div class="metric-value">{df['Cluster'].nunique()}</div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================
# PETA KLASTER (FIX & PROFESIONAL)
# ======================================================
st.markdown('<div class="section-title">🗺️ Peta Klaster Mutu Pendidikan</div>', unsafe_allow_html=True)

fig_map = px.choropleth(
    df,
    geojson=geojson_sumbar,
    locations="nama_peta",
    featureidkey="properties.NAME_2",
    color="Cluster",
    color_discrete_map={
        1: "#d73027",  # rendah
        2: "#fee08b",  # sedang
        3: "#1a9850"   # tinggi
    },
    hover_name="Kabupaten_Kota",
    hover_data={
        "Cluster": True,
        "APM_SD": ':.2f',
        "APM_SMP": ':.2f',
        "APM_SMA": ':.2f',
        "HLS": ':.2f',
        "RLS": ':.2f'
    },
    title="Segmentasi Mutu Pendidikan Kabupaten/Kota di Provinsi Sumatera Barat"
)

fig_map.update_geos(
    fitbounds="locations",
    visible=False
)

fig_map.update_layout(
    height=650,
    margin={"r":0,"t":50,"l":0,"b":0},
    legend_title_text="Klaster Mutu"
)

st.plotly_chart(fig_map, use_container_width=True)

# ======================================================
# TABEL DATA
# ======================================================
st.markdown('<div class="section-title">📋 Data Hasil Clustering</div>', unsafe_allow_html=True)
st.dataframe(df_filtered, use_container_width=True)

# ======================================================
# PROFIL KLASTER
# ======================================================
st.markdown('<div class="section-title">📈 Profil Rata-rata Indikator Pendidikan</div>', unsafe_allow_html=True)

cluster_profile = df_filtered.groupby("Cluster")[features].mean()
st.dataframe(cluster_profile.style.format("{:.2f}"), use_container_width=True)

# ======================================================
# RADAR CHART (FIX & PROFESIONAL)
# ======================================================
st.markdown('<div class="section-title">📊 Pola Indikator Pendidikan per Klaster</div>', unsafe_allow_html=True)

# Ubah ke format long
radar_long = (
    cluster_profile
    .reset_index()
    .melt(
        id_vars="Cluster",
        value_vars=features,
        var_name="Indikator",
        value_name="Nilai"
    )
)

fig_radar = px.line_polar(
    radar_long,
    r="Nilai",
    theta="Indikator",
    color="Cluster",
    line_close=True,
    color_discrete_map={
        1: "#d73027",
        2: "#fee08b",
        3: "#1a9850"
    }
)

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            tickfont_size=11
        )
    ),
    height=600,
    legend_title_text="Klaster Mutu"
)

st.plotly_chart(fig_radar, use_container_width=True)


# ======================================================
# INTERPRETASI
# ======================================================
st.markdown('<div class="section-title">🧠 Interpretasi Analitis</div>', unsafe_allow_html=True)

st.write(
    """
    Hasil segmentasi menunjukkan adanya perbedaan karakteristik mutu pendidikan
    antar kabupaten/kota di Provinsi Sumatera Barat. Klaster dengan nilai indikator
    pendidikan yang lebih tinggi mencerminkan wilayah dengan akses dan capaian
    pendidikan yang lebih baik, sedangkan klaster dengan nilai lebih rendah
    memerlukan perhatian dan intervensi kebijakan yang lebih prioritas.
    """
)

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.caption("© 2026 | Dashboard Segmentasi Mutu Pendidikan – Fuzzy C-Means")