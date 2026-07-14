import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import base64

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(page_title="Dashboard Eksekutif BMKG", layout="wide", page_icon="🏢")

# --- CUSTOM CSS ADAPTIF (Bisa Light / Dark Mode) ---
st.markdown("""
<style>
    /* Styling untuk Kartu Besar (Global) */
    .big-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(150, 150, 150, 0.2);
        border-radius: 12px;
        padding: 24px;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .big-card-icon {
        background-color: var(--background-color);
        padding: 16px;
        border-radius: 12px;
        margin-right: 20px;
        font-size: 24px;
    }
    .big-card-title {
        color: #6b7280;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .big-card-value {
        color: var(--text-color);
        font-size: 32px;
        font-weight: bold;
        margin: 0;
    }
    .big-card-value.green { color: #10b981; }

    /* Styling untuk Kartu Info (Detail) */
    .info-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(150, 150, 150, 0.2);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .info-card h4 {
        color: var(--text-color);
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .info-card p {
        color: #6b7280;
        font-size: 14px;
        margin: 4px 0;
    }
    .info-card strong { color: var(--text-color); }
    .info-card .money {
        color: #10b981;
        font-weight: bold;
        font-size: 16px;
        margin-top: 8px;
        display: inline-block;
    }
    .info-card .badge {
        background-color: #3b82f6;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }

    /* Styling untuk Kartu Metrik Kecil */
    .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(150, 150, 150, 0.2);
        border-radius: 12px;
        padding: 20px;
    }
    .metric-title {
        color: #6b7280;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-value.blue { color: #3b82f6; }
    .metric-value.green { color: #10b981; }
    .metric-value.orange { color: #f59e0b; }

    /* Styling Gallery Foto */
    .gallery-container {
        display: flex;
        gap: 20px;
        overflow-x: auto;
        padding-bottom: 10px;
    }
    .gallery-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(150, 150, 150, 0.2);
        border-radius: 12px;
        min-width: 250px;
        overflow: hidden;
    }
    .gallery-img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        background-color: var(--background-color);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6b7280;
        font-size: 12px;
        transition: 0.3s;
    }
    .gallery-img:hover { opacity: 0.8; }
    .gallery-info { padding: 15px; }
    .gallery-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .gallery-jenis {
        color: #3b82f6;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .gallery-date { color: #6b7280; font-size: 12px; }
    .gallery-caption {
        color: var(--text-color);
        font-size: 14px;
        font-weight: 500;
        margin: 0;
    }

    /* Lightbox Fullscreen */
    .lightbox {
        display: none;
        position: fixed;
        z-index: 999999;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, 0.9);
    }
    .lightbox:target {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .lightbox img {
        max-width: 90vw;
        max-height: 90vh;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
        position: relative;
        z-index: 2;
    }
    .lightbox-close {
        position: absolute;
        top: 20px;
        right: 40px;
        color: #ffffff;
        font-size: 50px;
        font-weight: bold;
        text-decoration: none;
        transition: 0.3s;
        z-index: 3;
    }
    .lightbox-close:hover { color: #ef4444; }
    .lightbox-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: default;
        z-index: 1;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. FUNGSI TARIK DATA
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    url_master    = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1368943818&single=true&output=csv"
    url_progress  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1227147818&single=true&output=csv"
    url_foto      = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=2011219797&single=true&output=csv"
    url_kendala   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1062397856&single=true&output=csv"

    df_master    = pd.read_csv(url_master)
    df_progress  = pd.read_csv(url_progress)
    df_foto      = pd.read_csv(url_foto)
    df_kendala   = pd.read_csv(url_kendala)
    
    return df_master, df_progress, df_foto, df_kendala

@st.cache_data(ttl=3600)
def download_gambar_gdrive(url):
    try:
        respon = requests.get(url)
        if respon.status_code == 200:
            return base64.b64encode(respon.content).decode("utf-8")
    except:
        return None
    return None

try:
    df_master, df_progress, df_foto, df_kendala = load_data()
except Exception as e:
    st.error(f"Gagal menarik data. Detail: {e}")
    st.stop()

# Bersihkan spasi
for df in [df_master, df_progress, df_foto, df_kendala]:
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()


# ==========================================
# 3. CUSTOM HEADER & NAVIGASI TAB
# ==========================================
col_title, col_nav = st.columns([2, 1])
with col_title:
    st.markdown("""
        <h1 style='margin-bottom: 0; padding-bottom: 0; font-size: 28px; display: flex; align-items: center; gap: 10px;'>
            <span style='color: #3b82f6;'>🏢</span> Dashboard Eksekutif BMKG
        </h1>
        <p style='color: #6b7280; margin-top: 5px;'>Monitoring Pembangunan Gedung • Data Terintegrasi Google Sheets.</p>
    """, unsafe_allow_html=True)

with col_nav:
    st.write("") 
    pilihan_tab = st.radio(
        "Navigasi", 
        ["Ringkasan Global", "Detail Per Gedung"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

st.write("<br>", unsafe_allow_html=True)

# ==========================================
# HALAMAN 1: RINGKASAN GLOBAL
# ==========================================
if pilihan_tab == "Ringkasan Global":
    if not df_master.empty:
        summary_row = df_master[df_master['ID Proyek'] == 'GLOBAL']
        tabel_gedung = df_master[df_master['ID Proyek'] != 'GLOBAL'].copy()

        if not summary_row.empty:
            summary = summary_row.iloc[0]
            
            val_status = summary.get('Status', '')
            val_nama = summary.get('Nama Gedung', '')
            
            if pd.notna(val_status) and str(val_status).strip().lower() != 'nan' and str(val_status).strip() != '':
                total_proyek = str(val_status)
            elif pd.notna(val_nama) and str(val_nama).strip().lower() != 'nan' and str(val_nama).strip() != '':
                total_proyek = str(val_nama)
            else:
                total_proyek = "9 Gedung"
                
            val_anggaran = summary.get('Nilai Kontrak', 0)
            try:
                val_clean = str(val_anggaran).replace(',', '').replace(' ', '')
                if val_clean.lower() == 'nan' or val_clean == '': val_clean = '0'
                anggaran_rp = f"Rp {float(val_clean):,.0f}".replace(',', '.')
            except:
                anggaran_rp = "Rp 0"

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="big-card">
                    <div class="big-card-icon">🏢</div>
                    <div>
                        <p class="big-card-title">TOTAL PROYEK</p>
                        <h2 class="big-card-value">{total_proyek}</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="big-card">
                    <div class="big-card-icon" style="color: #10b981;">💰</div>
                    <div>
                        <p class="big-card-title">TOTAL ANGGARAN KONTRAK</p>
                        <h2 class="big-card-value green">{anggaran_rp}</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>📄 Tabel Informasi Proyek Pembangunan</h4>", unsafe_allow_html=True)
    
    if 'tabel_gedung' in locals() and not tabel_gedung.empty:
        df_tampil = tabel_gedung[['ID Proyek', 'Nama Gedung', 'Provinsi', 'Kabupaten', 'Nilai Kontrak', 'Kontraktor', 'Status']].copy()
        df_tampil['LOKASI'] = df_tampil['Kabupaten'] + ", " + df_tampil['Provinsi']
        
        df_tampil['Nilai Kontrak'] = pd.to_numeric(df_tampil['Nilai Kontrak'], errors='coerce')
        df_tampil['ANGGARAN'] = df_tampil['Nilai Kontrak'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.') if pd.notnull(x) else "Rp 0")
        
        df_tampil = df_tampil.rename(columns={'ID Proyek': 'ID PROYEK', 'Nama Gedung': 'NAMA GEDUNG', 'Kontraktor': 'KONTRAKTOR', 'Status': 'STATUS'})
        df_tampil = df_tampil[['ID PROYEK', 'NAMA GEDUNG', 'LOKASI', 'ANGGARAN', 'KONTRAKTOR', 'STATUS']]
        
        st.dataframe(df_tampil, use_container_width=True, hide_index=True)


# ==========================================
# HALAMAN 2: DETAIL PER GEDUNG
# ==========================================
elif pilihan_tab == "Detail Per Gedung":
    
    st.sidebar.markdown("<h3 style='color: var(--text-color);'>PILIH GEDUNG</h3>", unsafe_allow_html=True)
    daftar_gedung = df_master[df_master['ID Proyek'] != 'GLOBAL']['Nama Gedung'].unique()
    
    if len(daftar_gedung) > 0:
        pilihan_gedung = st.sidebar.selectbox("", daftar_gedung, label_visibility="collapsed")
        
        info_gedung = df_master[df_master['Nama Gedung'] == pilihan_gedung].iloc[0]
        id_proyek_aktif = info_gedung['ID Proyek']
        
        st.sidebar.markdown(f"""
        <div style='margin-top: 20px;'>
            <p style='color: #3b82f6; font-size:12px; font-weight:bold; margin-bottom:2px;'>ID PROYEK</p>
            <p style='color: var(--text-color); font-weight:bold;'>{id_proyek_aktif}</p>
            <p style='color: #3b82f6; font-size:12px; font-weight:bold; margin-bottom:2px; margin-top:15px;'>NAMA LENGKAP</p>
            <p style='color: var(--text-color); font-weight:bold;'>{pilihan_gedung}</p>
        </div>
        """, unsafe_allow_html=True)

        df_prog_filter = df_progress[df_progress['ID Proyek'] == id_proyek_aktif].copy()
        df_foto_filter = df_foto[df_foto['ID Proyek'] == id_proyek_aktif].copy()
        df_kend_filter = df_kendala[df_kendala['ID Proyek'] == id_proyek_aktif].copy()

        # --- 1. KARTU INFORMASI UMUM ---
        st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>🔵 Informasi Umum Proyek</h4>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        
        try:
            nilai_k = float(str(info_gedung.get('Nilai Kontrak', 0)).replace(',', ''))
            kontrak_rp = f"Rp {nilai_k:,.0f}".replace(',', '.')
        except:
            kontrak_rp = "Rp 0"
            
        with m1:
            st.markdown(f"""
            <div class="info-card">
                <h4>📍 LOKASI WILAYAH</h4>
                <p><strong>{info_gedung.get('Provinsi', '-')}</strong></p>
                <p>{info_gedung.get('Kabupaten', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="info-card">
                <h4>👥 TIM PELAKSANA / NILAI</h4>
                <p>Kontraktor: <strong>{info_gedung.get('Kontraktor', '-')}</strong></p>
                <p>Pengawas: {info_gedung.get('Pengawas', '-')}</p>
                <span class="money">{kontrak_rp}</span>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="info-card">
                <h4>📅 WAKTU & STATUS</h4>
                <p>Mulai: <strong>{info_gedung.get('Tgl Mulai', '-')}</strong></p>
                <p>Target Selesai: <strong>{info_gedung.get('Target Selesai', '-')}</strong></p>
                <span class="badge">{str(info_gedung.get('Status', '-')).upper()}</span>
            </div>
            """, unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

        # --- 2. KARTU METRIK MINGGUAN TERBARU ---
        st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>📊 Indikator Progres Mingguan Terbaru</h4>", unsafe_allow_html=True)
        
        if not df_prog_filter.empty:
            baris_terakhir = df_prog_filter.iloc[-1]
            minggu_ke = baris_terakhir.get('Minggu', 'Terakhir')
            
            try:
                rencana_rp = f"Rp {float(str(baris_terakhir.get('Rencana Keuangan', 0)).replace(',', '').replace(' ', '')):,.0f}".replace(',', '.')
                realisasi_rp = f"Rp {float(str(baris_terakhir.get('Realisasi Keuangan', 0)).replace(',', '').replace(' ', '')):,.0f}".replace(',', '.')
            except:
                rencana_rp = "Rp 0"
                realisasi_rp = "Rp 0"
                
            tahapan = str(baris_terakhir.get('Tahapan', '-'))

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-title">RENCANA KEUANGAN (MINGGU {minggu_ke})</p>
                    <p class="metric-value blue">{rencana_rp}</p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-title">REALISASI KEUANGAN (MINGGU {minggu_ke})</p>
                    <p class="metric-value green">{realisasi_rp}</p>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-title">TAHAPAN PEKERJAAN SAAT INI</p>
                    <p class="metric-value orange">{tahapan}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Belum ada data progres mingguan.")

        st.write("<br>", unsafe_allow_html=True)

        # --- 3. GRAFIK KURVA S ADAPTIF ---
        st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>📈 Tren Kurva S (Rencana vs Realisasi Fisik)</h4>", unsafe_allow_html=True)
        if not df_prog_filter.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_prog_filter['Tanggal'], y=df_prog_filter['Rencana %'], 
                mode='lines+markers', name='Rencana Fisik (%)', 
                line=dict(color='#3b82f6', width=3, dash='dash'),
                marker=dict(size=8, color='#3b82f6')
            ))
            fig.add_trace(go.Scatter(
                x=df_prog_filter['Tanggal'], y=df_prog_filter['Realisasi %'], 
                mode='lines+markers', name='Realisasi Fisik (%)', 
                line=dict(color='#10b981', width=4),
                marker=dict(size=8, color='#10b981')
            ))
            
            # Konfigurasi diatur agar mengikuti tema Streamlit secara otomatis
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                hovermode="x unified",
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, zeroline=False, range=[0, 105], ticksuffix="%")
            )
            
            st.markdown('<div style="border: 1px solid rgba(150,150,150,0.2); border-radius: 12px; padding: 10px; background-color: var(--secondary-background-color);">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, theme="streamlit")
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)

        # --- 4. TABEL KENDALA ---
        st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>⚠️ Kendala & Tindak Lanjut Lapangan</h4>", unsafe_allow_html=True)
        if not df_kend_filter.empty:
            df_k_tampil = df_kend_filter[['Tanggal', 'Kategori', 'Uraian', 'Tindak Lanjut', 'Status']].rename(
                columns={'Tanggal':'TANGGAL', 'Kategori':'KATEGORI', 'Uraian':'URAIAN KENDALA', 'Tindak Lanjut':'TINDAK LANJUT', 'Status':'STATUS'}
            )
            st.dataframe(df_k_tampil, use_container_width=True, hide_index=True)
        else:
            st.info("Tidak ada data kendala.")

        st.write("<br>", unsafe_allow_html=True)

        # --- 5. GALERI FOTO CUSTOM HTML + FULLSCREEN ---
        st.markdown("<h4 style='color: var(--text-color); margin-bottom:15px;'>📸 Dokumentasi Pekerjaan Lapangan</h4>", unsafe_allow_html=True)
        
        if not df_foto_filter.empty:
            html_gallery = '<div class="gallery-container" id="foto-gallery">'
            lightbox_html = ''
            
            for index, row in df_foto_filter.iterrows():
                link_gambar = str(row.get('Nama File', '')).strip()
                keterangan = str(row.get('Caption', 'Dokumentasi'))
                jenis_pekerjaan = str(row.get('Jenis', '-'))
                tgl_foto = str(row.get('Tanggal', '-'))
                
                img_src = ""
                unique_id = f"foto_{index}"
                
                if "http" in link_gambar:
                    if "drive.google.com/uc?id=" in link_gambar:
                        link_gambar = link_gambar.replace("uc?id=", "thumbnail?id=") + "&sz=w400"
                    
                    foto_b64 = download_gambar_gdrive(link_gambar)
                    if foto_b64:
                        img_src = f"data:image/jpeg;base64,{foto_b64}"
                
                if img_src:
                    img_html = f'<a href="#{unique_id}"><img src="{img_src}" class="gallery-img" style="cursor: zoom-in;" title="Klik untuk perbesar"></a>'
                    # PERBAIKAN: Format HTML lightbox digabung jadi 1 baris lurus tanpa spasi awal
                    lightbox_html += f'<div id="{unique_id}" class="lightbox"><a href="#foto-gallery" class="lightbox-bg"></a><img src="{img_src}"><a href="#foto-gallery" class="lightbox-close" title="Tutup">&times;</a></div>'
                else:
                    img_html = '<div class="gallery-img" style="text-align:center; padding:20px;">Link gambar tidak tersedia</div>'
                
                html_gallery += f'<div class="gallery-card">{img_html}<div class="gallery-info"><div class="gallery-header"><span class="gallery-jenis">{jenis_pekerjaan}</span><span class="gallery-date">{tgl_foto}</span></div><p class="gallery-caption">{keterangan}</p></div></div>'
                
            html_gallery += '</div>'
            html_gallery += lightbox_html
            st.markdown(html_gallery, unsafe_allow_html=True)
        else:
            st.info("Belum ada foto yang diunggah untuk lokasi ini.")
