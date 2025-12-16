import streamlit as st
import time
import random
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- 2. CSS SAKTI: FIX WARNA & GRID ---
st.markdown("""
<style>
    /* Paksa Grid 4x4 Tetap Berjejer */
    .grid-container {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        max-width: 400px;
        margin: 0 auto;
    }
    
    [data-testid="column"] {
        width: unset !important;
        flex: unset !important;
        min-width: unset !important;
    }
    
    /* STYLE DASAR TOMBOL GRID */
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0 !important;
        border-radius: 0px !important;
        border: 0.5px solid #555 !important;
        background-color: #f0f2f6 !important; /* Warna dasar abu muda */
        color: transparent !important;
        box-shadow: none !important;
    }

    /* KELAS KHUSUS UNTUK BLINK BIRU (DIPAKSA) */
    /* Kita gunakan selector khusus agar tidak kalah dengan css streamlit */
    div.stButton > button[key*="on_"] {
        background-color: #0000FF !important; /* BIRU MURNI */
        border: none !important;
    }

    /* TOMBOL NAVIGASI (Lanjut, Next, Mulai) */
    /* Kita targetkan tombol yang ADA teksnya */
    div.stButton > button:not([key*="grid_"]):not([key*="blink_"]):not([key*="off_"]):not([key*="user_"]):not([key*="on_"]):not([key*="bg_"]) {
        aspect-ratio: auto !important;
        width: auto !important;
        padding: 10px 25px !important;
        background-color: #FF4B4B !important; /* Warna Merah Navigasi */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNGSI SIMPAN DATA ---
def save_to_google_sheets(data):
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    try:
        requests.post(SCRIPT_URL, json=data, timeout=10)
    except:
        pass

# --- 4. INISIALISASI STATE ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 0, 'data_diri': {}, 'skor_kuesioner': 0, 'sudah_simpan': False,
        'corsi': {'level': 1, 'sequence': [], 'user_input': [], 'playing_sequence': False, 'lives': 2, 'score': 0}
    })

# --- 5. NAVIGASI ---

if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("Terimakasih telah bersedia menjadi responden.")
    bersedia = st.checkbox("Saya bersedia ikut serta.")
    if st.button("Lanjut"):
        if bersedia: st.session_state.step = 1; st.rerun()

elif st.session_state.step == 1:
    st.header("Data Responden")
    with st.form("bio"):
        inisial = st.text_input("Inisial")
        wa = st.text_input("WA")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("JK", ["Pria", "Wanita"])
        pekerjaan = st.selectbox("Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        neuro = st.selectbox("Gangguan Neurologis", ["Tidak Ada", "ADHD", "Autisme", "Lainnya"])
        psiko = st.selectbox("Gangguan Psikologis", ["Tidak ada", "Stress", "Kecemasan", "Lainnya"])
        if st.form_submit_button("Lanjut ke Kuesioner"):
            if inisial and wa:
                st.session_state.data_diri = {"Inisial":inisial,"WA":wa,"Umur":umur,"JK":jk,"Pekerjaan":pekerjaan,"Domisili":domisili,"Neuro":neuro,"Psiko":psiko}
                st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.header("Kuesioner")
    questions = [
        "Internet lebih lama dari rencana.", "Pertemanan baru di internet.", "Merahasiakan aktivitas internet.",
        "Menutupi pikiran dengan internet.", "Takut hidup hampa tanpa internet.", "Marah jika diganggu main internet.",
        "Memikirkan internet saat offline.", "Memilih internet dibanding orang.", "Gelisah jika tidak main internet.",
        "Mengabaikan tugas.", "Nilai akademik menurun.", "Kinerja harian terganggu.",
        "Kurang tidur karena internet.", "Gagal mengurangi waktu internet.", "Berkata 'sebentar lagi'.",
        "Menyembunyikan durasi internet.", "Abaikan kegiatan penting.", "Sulit berhenti main internet."
    ]
    with st.form("kues"):
        sc = 0
        for i, q in enumerate(questions):
            val = st.radio(f"{i+1}. {q}", [1, 2, 3, 4], horizontal=True, key=f"q_{i}")
            sc += val
        if st.form_submit_button("Mulai Tes Corsi"):
            st.session_state.skor_kuesioner = sc
            st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.header("Tes Corsi")
    st.write("Ingat kotak yang menyala **BIRU**.")
    if st.button("MULAI SEKARANG"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4; st.rerun()

# --- 6. GAME: FIX BLINK BIRU ---
elif st.session_state.step == 4:
    st.write(f"### Level {st.session_state.corsi['level']}")
    
    if st.session_state.corsi['playing_sequence']:
        placeholder = st.empty()
        for target in st.session_state.corsi['sequence']:
            with placeholder.container():
                st.markdown('<div class="grid-container">', unsafe_allow_html=True)
                cols = st.columns(4)
                for i in range(16):
                    with cols[i%4]:
                        if i == target:
                            # Gunakan key "on_" agar dideteksi CSS Biru
                            st.button(" ", key=f"on_{i}_{target}_{time.time()}")
                        else:
                            st.button(" ", key=f"bg_{i}_{target}_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(1.0) # Kedip biru 1 detik
            
            # Jeda antar kotak (Semua abu-abu)
            with placeholder.container():
                st.markdown('<div class="grid-container">', unsafe_allow_html=True)
                cols = st.columns(4)
                for i in range(16):
                    with cols[i%4]:
                        st.button(" ", key=f"off_{i}_{target}_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(0.3)
            
        st.session_state.corsi['playing_sequence'] = False
        st.rerun()

    else:
        st.success("Ulangi urutan!")
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        cols = st.columns(4)
        for i in range(16):
            with cols[i%4]:
                if st.button(" ", key=f"user_{i}"):
                    st.session_state.corsi['user_input'].append(i)
                    curr = len(st.session_state.corsi['user_input']) - 1
                    if i != st.session_state.corsi['sequence'][curr]:
                        st.session_state.corsi['lives'] -= 1
                        if st.session_state.corsi['lives'] > 0:
                            st.error("Salah! Mengulang...")
                            time.sleep(1); st.session_state.corsi['user_input'] = []; st.session_state.corsi['playing_sequence'] = True; st.rerun()
                        else:
                            st.session_state.step = 5; st.rerun()
                    elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                        st.session_state.corsi['score'] = st.session_state.corsi['level']
                        if st.session_state.corsi['level'] < 9:
                            st.session_state.corsi['level'] += 1
                            st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(st.session_state.corsi['level'] + 1)]
                            st.session_state.corsi['user_input'] = []; st.session_state.corsi['playing_sequence'] = True; st.session_state.corsi['lives'] = 2; st.rerun()
                        else:
                            st.session_state.step = 5; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 5:
    st.header("Selesai")
    if not st.session_state.sudah_simpan:
        final_data = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **st.session_state.data_diri, "Skor_Kuesioner": st.session_state.skor_kuesioner, "Skor_Corsi": st.session_state.corsi['score']}
        save_to_google_sheets(final_data)
        st.session_state.sudah_simpan = True
    st.success("Terimakasih! Data telah tersimpan.")
