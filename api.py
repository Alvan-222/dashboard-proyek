import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# ==========================================
# 1. KONFIGURASI HALAMAN & THEME
# ==========================================
st.set_page_config(page_title="Dashboard Proyek Eksekutif BMKG", layout="wide")
st.title("🏗️ Dashboard Monitoring Pembangunan 9 Gedung")
st.markdown("Sistem Informasi Manajerial Progres Fisik, Keuangan, dan Dokumentasi Lapangan.")

# ==========================================
# 2. FUNGSI TARIK DATA DARI G-DRIVE (CSV)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    # Link Google Sheets (Dashboard_Data Dihapus)
    url_master    = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1368943818&single=true&output=csv"
    url_progress  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1227147818&single=true&output=csv"
    url_foto      = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=2011219797&single=true&output=csv"
    url_kendala   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjneCylp3F85952ugWGbEatlqy8F7ZEcSbSuSMdL_yWvS3_rh-QLIgKfrTbEmZfQ/pub?gid=1062397856&single=true&output=csv"

    df_master    = pd.read_csv(url_master)
    df_progress  = pd.read_csv(url_progress)
    df_foto      = pd.read_csv(url_foto)
    df_kendala   = pd.read_csv(url_kendala)
    
    return df_master, df_progress, df_foto, df_kendala

# Cache khusus download gambar biar ga bikin lemot
@st.cache_data(ttl=3600)
def download_gambar_gdrive(url):
    try:
        respon = requests.get(url)
        if respon.status_code == 200:
            return respon.content
    except:
        return None
    return None

try:
    df_master, df_progress, df_foto, df_kendala = load_data()
except Exception as e:
    st.error(f"Gagal menarik data. Pastikan nama file/link CSV benar. Detail Error: {e}")
    st.stop()

# Bersihkan spasi gaib di kolom dan sel data
for df in [df_master, df_progress, df_foto, df_kendala]:
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()


# ==========================================
# 3. MEMBUAT MENU TAB HALAMAN
# ==========================================
tab_global, tab_detail = st.tabs(["📊 Ringkasan Global (Semua Gedung)", "🏢 Detail Laporan Per Gedung"])


# ==========================================
# HALAMAN 1: RINGKASAN GLOBAL
# ==========================================
with tab_global:
    st.subheader("📈 Status Portofolio Proyek Nasional")
    
    if not df_master.empty:
        # 1. Cari baris yang ID Proyek-nya 'GLOBAL' di Master_Proyek
        summary_row = df_master[df_master['ID Proyek'] == 'GLOBAL']
        
        # 2. Pisahkan tabel daftar gedung agar baris GLOBAL tidak muncul di tabel
        tabel_gedung = df_master[df_master['ID Proyek'] != 'GLOBAL'].copy()

        if not summary_row.empty:
            summary = summary_row.iloc[0]
            
            # KITA BUAT 2 KOTAK METRIK
            g1, g2 = st.columns(2)
            
            # --- PERBAIKAN LOGIKA ANTI-NAN UNTUK TOTAL PROYEK ---
            val_status = summary.get('Status', '')
            val_nama = summary.get('Nama Gedung', '')
            
            # Cek jika kolom Status TIDAK kosong dan bukan 'nan'
            if pd.notna(val_status) and str(val_status).strip().lower() != 'nan' and str(val_status).strip() != '':
                total_proyek = str(val_status)
            # Jika Status kosong, cek kolom Nama Gedung
            elif pd.notna(val_nama) and str(val_nama).strip().lower() != 'nan' and str(val_nama).strip() != '':
                total_proyek = str(val_nama)
            else:
                total_proyek = "9 Gedung" # Teks cadangan terakhir
                
            # --- PERBAIKAN LOGIKA ANTI-NAN UNTUK ANGGARAN ---
            val_anggaran = summary.get('Nilai Kontrak', 0)
            try:
                # Bersihkan spasi/koma kalau ada, dan ubah 'nan' jadi '0'
                val_clean = str(val_anggaran).replace(',', '').replace(' ', '')
                if val_clean.lower() == 'nan' or val_clean == '':
                    val_clean = '0'
                
                anggaran_rp = f"Rp {float(val_clean):,.0f}".replace(',', '.')
            except:
                anggaran_rp = "Rp 0"
                
            # Tampilkan 2 metrik ke Dashboard
            g1.metric(label="Total Proyek", value=total_proyek)
            g2.metric(label="Total Anggaran Kontrak", value=anggaran_rp)
            
        else:
            st.warning("Baris ringkasan dengan ID 'GLOBAL' tidak ditemukan di sheet Master_Proyek.")
    
    st.divider()
    st.subheader("📋 Tabel Informasi Master Seluruh Gedung")
    
    # Tampilkan hanya daftar gedung saja, baris GLOBAL disembunyikan dari tabel
    if 'tabel_gedung' in locals() and not tabel_gedung.empty:
        # Rapikan format angka Nilai Kontrak di tabel jadi Rupiah
        if 'Nilai Kontrak' in tabel_gedung.columns:
            tabel_gedung['Nilai Kontrak'] = pd.to_numeric(tabel_gedung['Nilai Kontrak'], errors='coerce')
            tabel_gedung['Nilai Kontrak'] = tabel_gedung['Nilai Kontrak'].apply(
                lambda x: f"Rp {x:,.0f}".replace(',', '.') if pd.notnull(x) else "Rp 0"
            )
        
        st.dataframe(tabel_gedung, use_container_width=True, hide_index=True)

# ==========================================
# HALAMAN 2: DETAIL LAPORAN PER GEDUNG
# ==========================================
with tab_detail:
    # --- SIDEBAR KHUSUS FILTER DETAIL ---
    # Pastikan 'GLOBAL' tidak masuk ke dalam pilihan dropdown
    daftar_gedung = df_master[df_master['ID Proyek'] != 'GLOBAL']['Nama Gedung'].unique()
    
    if len(daftar_gedung) > 0:
        pilihan_gedung = st.sidebar.selectbox("Pilih Gedung yang Mau Dilihat:", daftar_gedung)

        # Ambil data spesifik gedung yang dipilih dari Master
        info_gedung = df_master[df_master['Nama Gedung'] == pilihan_gedung].iloc[0]
        id_proyek_aktif = info_gedung['ID Proyek']

        # Filter sheet lain berdasarkan ID Proyek aktif
        df_prog_filter = df_progress[df_progress['ID Proyek'] == id_proyek_aktif].copy()
        df_foto_filter = df_foto[df_foto['ID Proyek'] == id_proyek_aktif].copy()
        df_kend_filter = df_kendala[df_kendala['ID Proyek'] == id_proyek_aktif].copy()

        # TAMPILKAN KARTU INFORMASI PROYEK 
        st.subheader(f"📍 {pilihan_gedung} ({id_proyek_aktif})")
        
        # Baris Informasi Umum dari Sheet Master
        m1, m2, m3 = st.columns(3)
        with m1:
            st.info(f"**📍 Lokasi Wilayah:**\n\nProvinsi: {info_gedung.get('Provinsi', '-')}\n\nKabupaten: {info_gedung.get('Kabupaten', '-')}")
        with m2:
            # Format nilai kontrak rupiah
            try:
                nilai_kontrak = float(str(info_gedung.get('Nilai Kontrak', 0)).replace(',', ''))
                kontrak_rp = f"Rp {nilai_kontrak:,.0f}".replace(',', '.')
            except:
                kontrak_rp = "Rp 0"
            st.info(f"**👥 Tim Pelaksana & Anggaran:**\n\nKontraktor: {info_gedung.get('Kontraktor', '-')}\n\nPengawas: {info_gedung.get('Pengawas', '-')}\n\nNilai Kontrak: {kontrak_rp}")
        with m3:
            st.info(f"**📅 Target Waktu Pelaksanaan:**\n\nTanggal Mulai: {info_gedung.get('Tgl Mulai', '-')}\n\nTarget Selesai: {info_gedung.get('Target Selesai', '-')}\n\nStatus Utama: **{info_gedung.get('Status', '-')}**")

        # --- METRIK UTAMA MINGGU TERAKHIR ---
        if not df_prog_filter.empty:
            # Mengambil baris paling bawah (data terbaru/minggu terakhir)
            baris_terakhir = df_prog_filter.iloc[-1]
            minggu_ke = baris_terakhir.get('Minggu', 'Terakhir')
            
            st.write("---")
            # Kita ubah menjadi 3 kolom (Rencana Keuangan, Realisasi Keuangan, Tahapan)
            c1, c2, c3 = st.columns(3)
            
            # 1. Rencana Keuangan
            try:
                rencana_mentah = str(baris_terakhir.get('Rencana Keuangan', 0)).replace(',', '').replace(' ', '')
                rencana_rp = f"Rp {float(rencana_mentah):,.0f}".replace(',', '.')
            except:
                rencana_rp = "Rp 0"
                
            c1.metric(label=f"Rencana Keuangan (Minggu {minggu_ke})", value=rencana_rp)
            
            # 2. Realisasi Keuangan
            try:
                realisasi_mentah = str(baris_terakhir.get('Realisasi Keuangan', 0)).replace(',', '').replace(' ', '')
                realisasi_rp = f"Rp {float(realisasi_mentah):,.0f}".replace(',', '.')
            except:
                realisasi_rp = "Rp 0"
                
            c2.metric(label=f"Realisasi Keuangan (Minggu {minggu_ke})", value=realisasi_rp)
            
            # 3. Tahapan Pekerjaan Saat Ini
            tahapan_sekarang = str(baris_terakhir.get('Tahapan', '-'))
            c3.metric(label=f"Tahapan Pekerjaan Saat Ini", value=tahapan_sekarang)
            
        else:
            st.warning("Belum ada data progres mingguan untuk gedung ini.")

        st.divider()

        # --- GRAFIK KURVA S ---
        st.subheader("📈 Tren Kurva S (Rencana vs Realisasi Fisik)")
        if not df_prog_filter.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_prog_filter['Tanggal'], y=df_prog_filter['Rencana %'], mode='lines+markers', name='Rencana Fisik (%)', line=dict(color='blue', dash='dash')))
            fig.add_trace(go.Scatter(x=df_prog_filter['Tanggal'], y=df_prog_filter['Realisasi %'], mode='lines+markers', name='Realisasi Fisik (%)', line=dict(color='green', width=3)))
            fig.update_layout(xaxis_title="Tanggal Laporan", yaxis_title="Progress (%)", yaxis=dict(range=[0, 105]), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

        # --- TABEL KENDALA ---
        st.subheader("⚠️ Kendala & Tindak Lanjut Lapangan")
        if not df_kend_filter.empty:
            st.dataframe(df_kend_filter[['Tanggal', 'Kategori', 'Uraian', 'Tindak Lanjut', 'Status']], use_container_width=True, hide_index=True)
        else:
            st.success("Tidak ada kendala dilaporkan untuk gedung ini. Proyek berjalan lancar!")

        st.divider()

        # --- GALERI FOTO OPTIMAL & CEPAT ---
        st.subheader("📸 Dokumentasi Pekerjaan Lapangan")
        if not df_foto_filter.empty:
            cols = st.columns(3) # Grid galeri 3 kolom
            
            for index, row in df_foto_filter.reset_index().iterrows():
                kolom_aktif = cols[index % 3]
                
                with kolom_aktif:
                    link_gambar = str(row.get('Nama File', '')).strip()
                    keterangan = str(row.get('Caption', 'Foto Dokumentasi'))
                    jenis_pekerjaan = str(row.get('Jenis', '-'))
                    tgl_foto = str(row.get('Tanggal', '-'))
                    
                    if "http" in link_gambar:
                        # Trik bypass blokir Google Drive via Jalur Thumbnail Ringan (w400)
                        if "drive.google.com/uc?id=" in link_gambar:
                            link_gambar = link_gambar.replace("uc?id=", "thumbnail?id=") + "&sz=w400"
                        
                        # Ambil data gambar dari cache RAM biar ngebut
                        foto_biner = download_gambar_gdrive(link_gambar)
                        
                        if foto_biner is not None:
                            # Tampilkan foto lengkap dengan detail tanggal & kategori kerjaan di captionnya
                            st.image(foto_biner, caption=f"{keterangan} ({jenis_pekerjaan} - {tgl_foto})", use_container_width=True)
                        else:
                            st.error(f"Gagal memuat gambar: {keterangan}")
                    else:
                        st.info(f"Link gambar belum di-update untuk: {keterangan}")
        else:
            st.info("Belum ada foto yang diunggah untuk lokasi ini.")
    else:
        st.error("Data Master Proyek kosong.")