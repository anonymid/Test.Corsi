import streamlit as st
import time
import random
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- 2. CSS SAKTI: FIX GRID MOBILE & TOMBOL ---
st.markdown("""
<style>
    /* Paksa Grid 4x4 Tetap Berjejer di HP */
    .grid-container {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Matikan perilaku kolom default Streamlit agar tidak tumpuk vertikal */
    [data-testid="column"] {
        width: unset !important;
        flex: unset !important;
        min-width: unset !important;
    }
    
    /* Styling Tombol Grid (Kotak Tajam & Tanpa Bayangan) */
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0 !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        border: 0.5px solid #555 !important;
        transition: none !important;
    }

    /* Warna Blink Biru Pekat */
    button[kind="primary"] {
        background-color: #0000FF !important;
        color: transparent !important;
        border: none !important;
    }

    /* Kembalikan gaya tombol Navigasi (Lanjut/Mulai) */
    div.stButton > button:not([key*="grid_"]):not([key*="blink_"]):not([key*="off_"]):not([key*="user_"]):not([key*="on_"]) {
        aspect-ratio: auto !important;
        width: auto !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        background-color: #FF4B4B !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNGSI SIMPAN DATA ---
def save_to_google_sheets(data):
    # PASTIIN URL INI BENAR (URL APPS SCRIPT)
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    try:
        requests.post(SCRIPT_URL, json=data, timeout=10)
    except:
        pass

# --- 4. INISIALISASI STATE ---
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

# --- 5. LOGIKA NAVIGASI ---

# --- HALAMAN 0: WELCOME ---
if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("Terimakasih telah bersedia menjadi responden dalam penelitian ini.")
    bersedia = st.checkbox("Saya bersedia mengikuti penelitian ini secara sukarela.")
    if st.button("Lanjut"):
        if bersedia: 
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("Mohon centang persetujuan.")

# --- HALAMAN 1: DATA DIRI ---
elif st.session_state.step == 1:
    st.header("Data Responden")
    with st.form("bio_form"):
        inisial = st.text_input("Inisial")
        wa = st.text_input("Nomor Whatsapp")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        pekerjaan = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        neuro = st.selectbox("Gangguan Neurologis", ["Tidak Ada", "ADHD", "Autisme", "Lainnya"])
        psiko = st.selectbox("Gangguan Psikologis", ["Tidak ada", "Stress", "Kecemasan", "Lainnya"])
        
        if st.form_submit_button("Lanjut ke Kuesioner"):
            if inisial and wa:
                st.session_state.data_diri = {
                    "Inisial": inisial, "WA": wa, "Umur": umur, "JK": jk, 
                    "Pekerjaan": pekerjaan, "Domisili": domisili, 
                    "Neuro": neuro, "Psiko": psiko
                }
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Inisial dan WA wajib diisi.")

# --- HALAMAN 2: KUESIONER (18 PERTANYAAN) ---
elif st.session_state.step == 2:
    st.header("Kuesioner")
    st.info("Skala: 1 (Sangat Tidak Setuju) sampai 4 (Sangat Setuju)")
    
    questions = [
        "Saya bermain internet lebih lama dari rencana.",
        "Saya membentuk pertemanan baru di internet.",
        "Saya merahasiakan aktivitas internet saya.",
        "Saya menutupi pikiran mengganggu dengan internet.",
        "Saya takut hidup tanpa internet akan terasa kosong.",
        "Saya merasa marah jika diganggu saat main internet.",
        "Saya terus memikirkan internet saat tidak online.",
        "Saya memilih internet daripada bertemu orang lain.",
        "Saya merasa gelisah jika tidak main internet.",
        "Saya mengabaikan tugas demi internet.",
        "Nilai akademik saya menurun karena internet.",
        "Kinerja harian saya terganggu karena internet.",
        "Saya kurang tidur karena internet.",
        "Saya gagal mengurangi waktu main internet.",
        "Saya sering berkata 'sebentar lagi' saat online.",
        "Saya menyembunyikan durasi main internet.",
        "Saya mengabaikan kegiatan penting demi internet.",
        "Saya merasa sulit berhenti main internet."
    ]
    
    with st.form("kues_form"):
        total_score = 0
        for i, q in enumerate(questions):
            choice = st.radio(f"{i+1}. {q}", [1, 2, 3, 4], horizontal=True, key=f"q_{i}")
            total_score += choice
        
        if st.form_submit_button("Lanjut ke Tes Corsi"):
            st.session_state.skor_kuesioner = total_score
            st.session_state.step = 3
            st.rerun()

# --- HALAMAN 3: INTRO TES ---
elif st.session_state.step == 3:
    st.header("Tes Corsi Block Tapping")
    st.write("Ingat urutan kotak yang menyala **BIRU**, lalu klik ulang kotak tersebut.")
    if st.button("MULAI SEKARANG"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4
        st.rerun()

# --- HALAMAN 4: GAME CORSI (FIX BLINK & GRID) ---
elif st.session_state.step == 4:
    st.write(f"### Level {st.session_state.corsi['level']} / 9")
    
    # --- PHASE 1: ANIMASI KEDIPAN ---
    if st.session_state.corsi['playing_sequence']:
        st.warning("Perhatikan kedipan BIRU...")
        placeholder = st.empty()
        
        for target in st.session_state.corsi['sequence']:
            # Nyalakan kotak Biru
            with placeholder.container():
                st.markdown('<div class="grid-container">', unsafe_allow_html=True)
                cols = st.columns(4)
                for i in range(16):
                    with cols[i%4]:
                        if i == target:
                            st.button(" ", key=f"on_{i}_{target}_{time.time()}", type="primary")
                        else:
                            st.button(" ", key=f"bg_{i}_{target}_{time.time()}")
                st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(0.9)
            
            # Matikan kotak (jeda)
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

    # --- PHASE 2: INPUT USER ---
    else:
        st.success("Giliran Anda! Klik sesuai urutan.")
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        cols = st.columns(4)
        for i in range(16):
            with cols[i%4]:
                if st.button(" ", key=f"user_{i}"):
                    st.session_state.corsi['user_input'].append(i)
                    curr = len(st.session_state.corsi['user_input']) - 1
                    
                    # Validasi klik
                    if i != st.session_state.corsi['sequence'][curr]:
                        st.session_state.corsi['lives'] -= 1
                        if st.session_state.corsi['lives'] > 0:
                            st.error("Salah! Mengulang level ini...")
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
                            new_len = st.session_state.corsi['level'] + 1
                            st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(new_len)]
                            st.session_state.corsi['user_input'] = []
                            st.session_state.corsi['playing_sequence'] = True
                            st.session_state.corsi['lives'] = 2
                            st.rerun()
                        else:
                            st.session_state.step = 5
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 5: PENUTUP & SIMPAN DATA ---
elif st.session_state.step == 5:
    st.header("Selesai")
    st.success("Terimakasih! Data Anda telah tersimpan otomatis.")
    
    if not st.session_state.sudah_simpan:
        final_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **st.session_state.data_diri,
            "Skor_Kuesioner": st.session_state.skor_kuesioner,
            "Skor_Corsi": st.session_state.corsi['score']
        }
        save_to_google_sheets(final_data)
        st.session_state.sudah_simpan = True

    st.write("Anda bisa menutup halaman ini sekarang.")
