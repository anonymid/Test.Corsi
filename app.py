import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import requests

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- CSS CUSTOM: MEMAKSA GRID 4X4 DAN SETTING TOMBOL KHUSUS ---
st.markdown("""
<style>
    /* 1. Memaksa Grid 4x4 di Mobile */
    [data-testid="column"] {
        flex: 1 1 20% !important;
        min-width: 20% !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0px !important;
    }

    /* 2. Styling Khusus untuk Tombol Grid Corsi */
    /* Kita beri target tombol yang TIDAK memiliki teks di dalamnya */
    div.stButton > button {
        border-radius: 0px !important;
        box-shadow: none !important;
        transition: none !important;
    }

    /* Tombol Grid (Kotak Putih/Abu) */
    div.stButton > button:not([kind="primary"]):not([kind="secondary"]) {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: #ffffff !important;
        border: 0.5px solid #cccccc !important;
        height: auto !important;
    }

    /* Tombol Blink (Biru) */
    div.stButton > button[kind="primary"] {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        background-color: #0000FF !important;
        border: none !important;
        color: transparent !important;
    }

    /* Tombol Navigasi (Lanjut, Mulai, Next) - Kita kembalikan warnanya */
    /* Tombol di Form biasanya bertipe secondary secara default */
    div.stButton > button[kind="secondaryFormSubmit"], 
    div.stButton > button:contains("Lanjut"),
    div.stButton > button:contains("Next"),
    div.stButton > button:contains("MULAI") {
        width: auto !important;
        aspect-ratio: auto !important;
        background-color: #FF4B4B !important; /* Warna merah khas Streamlit */
        color: white !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI SIMPAN DATA ---
def save_to_google_sheets(data):
    # GANTI DENGAN URL APPS SCRIPT KAMU
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    try:
        requests.post(SCRIPT_URL, json=data, timeout=10)
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
    st.write("Terimakasih telah bersedia menjadi responden kami dalam penelitian ini. Semua data dirahasiakan.")
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
        wa = st.text_input("Nomor Whatsapp")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        pekerjaan = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        durasi_inet = st.selectbox("Durasi Internet/Hari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        tujuan = st.selectbox("Tujuan Utama", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        aktifitas = st.selectbox("Aktifitas Dominan", ["Scrolling Pasif", "Scrolling Aktif"])
        gadget_tidur = st.radio("Gadget sebelum tidur?", ["Ya", "Tidak"])
        durasi_tidur = st.selectbox("Durasi Tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        kualitas_tidur = st.selectbox("Kualitas Tidur", ["Baik", "Sedang", "Buruk"])
        kafein = st.selectbox("Konsumsi Kafein", ["Tidak pernah", "1x sehari", "2x sehari", "3x sehari"])
        neuro = st.selectbox("Gangguan Neurologis", ["Tidak Ada", "ADHD", "Autisme", "Parkinson", "Lainnya"])
        psiko = st.selectbox("Gangguan Psikologis", ["Tidak ada", "Stress Psikologis", "Kecemasan", "Lainnya"])
        
        submit = st.form_submit_button("Next")
        if submit:
            if not inisial or not wa:
                st.error("Inisial dan WA wajib diisi.")
            else:
                st.session_state.data_diri = {
                    "Inisial": inisial, "WA": wa, "Umur": umur, "JK": jk, "Pekerjaan": pekerjaan,
                    "Domisili": domisili, "Durasi_Inet": durasi_inet, "Tujuan": tujuan,
                    "Aktifitas": aktifitas, "Gadget_Tidur": gadget_tidur, "Durasi_Tidur": durasi_tidur,
                    "Kualitas_Tidur": kualitas_tidur, "Kafein": kafein, "Neuro": neuro, "Psiko": psiko
                }
                st.session_state.step = 2
                st.rerun()

# 2. KUESIONER
elif st.session_state.step == 2:
    st.header("Kuesioner")
    st.write("1=Sangat Tidak Setuju, 4=Sangat Setuju")
    q_list = ["Internet lebih lama dari rencana.", "Pertemanan baru di internet.", "Merahasiakan aktivitas internet.", "Menutupi pikiran dengan internet.", "Takut hidup hampa tanpa internet.", "Marah jika diganggu main internet.", "Memikirkan internet saat offline.", "Memilih internet dibanding orang.", "Gelisah jika tidak main internet.", "Mengabaikan tugas.", "Nilai akademik menurun.", "Kinerja terganggu.", "Kurang tidur.", "Gagal mengurangi waktu internet.", "Berkata 'sebentar lagi'.", "Sembunyikan durasi internet.", "Abaikan kegiatan penting.", "Sulit berhenti."]
    
    with st.form("kues"):
        scores = []
        for i, q in enumerate(q_list):
            scores.append(st.radio(f"{i+1}. {q}", [1, 2, 3, 4], horizontal=True))
        
        if st.form_submit_button("Mulai Tes Corsi"):
            st.session_state.skor_kuesioner = sum(scores)
            st.session_state.step = 3
            st.rerun()

# 3. INTRO CORSI
elif st.session_state.step == 3:
    st.header("Tes Corsi Block Tapping")
    st.info("Perhatikan kedipan biru, lalu ulangi.")
    if st.button("MULAI TES"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4
        st.rerun()

# 4. GAME CORSI
elif st.session_state.step == 4:
    st.write(f"### Level {st.session_state.corsi['level']}")
    
    if st.session_state.corsi['playing_sequence']:
        placeholder = st.empty()
        for target in st.session_state.corsi['sequence']:
            with placeholder.container():
                cols = st.columns(4)
                for i in range(16):
                    if i == target:
                        cols[i%4].button("", key=f"b_{i}_{target}_{time.time()}", type="primary")
                    else:
                        cols[i%4].button("", key=f"e_{i}_{target}_{time.time()}")
            time.sleep(0.8)
            with placeholder.container():
                cols = st.columns(4)
                for i in range(16):
                    cols[i%4].button("", key=f"off_{i}_{target}_{time.time()}")
            time.sleep(0.3)
        st.session_state.corsi['playing_sequence'] = False
        st.rerun()
    else:
        st.success("Ulangi urutannya!")
        cols = st.columns(4)
        for i in range(16):
            if cols[i%4].button("", key=f"user_{i}"):
                st.session_state.corsi['user_input'].append(i)
                curr = len(st.session_state.corsi['user_input']) - 1
                if i != st.session_state.corsi['sequence'][curr]:
                    st.session_state.corsi['lives'] -= 1
                    if st.session_state.corsi['lives'] > 0:
                        st.error("Salah! Ulangi level ini.")
                        time.sleep(1)
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.rerun()
                    else:
                        st.session_state.step = 5
                        st.rerun()
                elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                    st.session_state.corsi['score'] = st.session_state.corsi['level']
                    if st.session_state.corsi['level'] < 9:
                        st.session_state.corsi['level'] += 1
                        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(st.session_state.corsi['level'] + 1)]
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.session_state.corsi['lives'] = 2
                        st.rerun()
                    else:
                        st.session_state.step = 5
                        st.rerun()

# 5. PENUTUP
elif st.session_state.step == 5:
    st.header("Terimakasih")
    st.write("Jawaban anda telah tersimpan otomatis.")
    if not st.session_state.sudah_simpan:
        final_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **st.session_state.data_diri,
            "Skor_Kuesioner": st.session_state.skor_kuesioner,
            "Skor_Corsi": st.session_state.corsi['score']
        }
        save_to_google_sheets(final_data)
        st.session_state.sudah_simpan = True
