import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import requests

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- CSS CUSTOM: GRID 4x4 RAPI, TANPA SHADOW, TANPA GAP ---
st.markdown("""
<style>
    /* Paksa grid kolom rapat */
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
    /* Styling tombol grid */
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 0px !important;
        border: 0.5px solid #dddddd !important;
        background-color: #f8f9fa;
        box-shadow: none !important; /* Hapus bayangan */
        transition: none !important;
    }
    /* Warna saat blink biru */
    button[kind="primary"] {
        background-color: #0000FF !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* Hilangkan shadow saat hover/klik */
    .stButton button:focus, .stButton button:active, .stButton button:hover {
        box-shadow: none !important;
        background-color: #f8f9fa;
        border: 0.5px solid #dddddd !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI SIMPAN DATA ---
def save_to_google_sheets(data):
    # GANTI DENGAN URL APPS SCRIPT KAMU
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    try:
        requests.post(SCRIPT_URL, json=data)
    except:
        pass

# --- INISIALISASI STATE ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 0,
        'data_diri': {},
        'skor_kuesioner': 0,
        'sudah_simpan': False,
        'corsi': {
            'level': 1,
            'sequence': [],
            'user_input': [],
            'playing_sequence': False,
            'lives': 2,
            'score': 0
        }
    })

# --- NAVIGASI HALAMAN ---

# 0. WELCOME
if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("Terimakasih telah bersedia menjadi responden kami dalam penelitian ini. Semua data dirahasiakan. Tersedia e-money untuk 5 orang terpilih.")
    bersedia = st.checkbox("Apakah anda bersedia menjadi responden?")
    if st.button("Lanjut"):
        if bersedia:
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("Mohon centang persetujuan.")

# 1. DATA RESPONDEN
elif st.session_state.step == 1:
    st.header("Data Responden")
    with st.form("bio"):
        inisial = st.text_input("Inisial")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        pekerjaan = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        wa = st.text_input("Nomor Whatsapp")
        durasi_inet = st.selectbox("Durasi Internet/Hari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        tujuan = st.selectbox("Tujuan Utama", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        aktifitas = st.selectbox("Aktifitas Dominan", ["Scrolling Pasif", "Scrolling Aktif"])
        gadget_tidur = st.radio("Gadget sebelum tidur?", ["Ya", "Tidak"])
        durasi_tidur = st.selectbox("Durasi Tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        kualitas_tidur = st.selectbox("Kualitas Tidur", ["Baik", "Sedang", "Buruk"])
        kafein = st.selectbox("Konsumsi Kafein", ["Tidak pernah", "1x sehari", "2x sehari", "3x sehari"])
        neuro = st.selectbox("Gangguan Neurologis", ["Tidak Ada", "ADHD", "Autisme", "Lainnya"])
        psiko = st.selectbox("Gangguan Psikologis", ["Tidak ada", "Stress", "Kecemasan", "Lainnya"])
        
        if st.form_submit_button("Next"):
            st.session_state.data_diri = {
                "Inisial": inisial, "Umur": umur, "JK": jk, "Pekerjaan": pekerjaan,
                "Domisili": domisili, "WA": wa, "Durasi_Inet": durasi_inet,
                "Tujuan": tujuan, "Aktifitas": aktifitas, "Gadget_Tidur": gadget_tidur,
                "Durasi_Tidur": durasi_tidur, "Kualitas_Tidur": kualitas_tidur,
                "Kafein": kafein, "Neuro": neuro, "Psiko": psiko
            }
            st.session_state.step = 2
            st.rerun()

# 2. KUESIONER
elif st.session_state.step == 2:
    st.header("Kuesioner")
    st.write("1=Sangat Tidak Setuju, 4=Sangat Setuju")
    q_list = [
        "Saya bermain internet lebih lama dari rencana.",
        "Saya membentuk pertemanan baru di internet.",
        "Saya merahasiakan aktivitas internet.",
        "Saya menutupi pikiran mengganggu dengan internet.",
        "Takut hidup tanpa internet akan kosong.",
        "Marah jika diganggu saat main internet.",
        "Terus memikirkan internet saat tidak main.",
        "Memilih internet daripada orang lain.",
        "Gelisah jika tidak main internet.",
        "Mengabaikan tugas demi internet.",
        "Nilai akademik menurun karena internet.",
        "Kinerja terganggu karena internet.",
        "Kurang tidur karena internet.",
        "Gagal mengurangi waktu internet.",
        "Sering berkata 'sebentar lagi'.",
        "Menyembunyikan durasi main internet.",
        "Mengabaikan kegiatan penting demi internet.",
        "Sulit berhenti main internet."
    ]
    total = 0
    with st.form("kues"):
        for i, q in enumerate(q_list):
            val = st.radio(f"{i+1}. {q}", [1, 2, 3, 4], horizontal=True)
            total += val
        if st.form_submit_button("Mulai Tes Corsi"):
            st.session_state.skor_kuesioner = total
            st.session_state.step = 3
            st.rerun()

# 3. INTRO CORSI
elif st.session_state.step == 3:
    st.header("Tes Corsi Block Tapping")
    st.write("Perhatikan urutan kotak yang menyala biru, lalu ulangi.")
    if st.button("MULAI"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4
        st.rerun()

# 4. GAME CORSI
elif st.session_state.step == 4:
    st.write(f"### Level {st.session_state.corsi['level']} / 9")
    
    if st.session_state.corsi['playing_sequence']:
        placeholder = st.empty()
        for target in st.session_state.corsi['sequence']:
            with placeholder.container():
                cols = st.columns(4)
                for i in range(16):
                    if i == target:
                        cols[i%4].button("", key=f"b_{i}_{target}_{time.time()}", type="primary")
                    else:
                        cols[i%4].button("", key=f"e_{i}_{target}_{time.time
