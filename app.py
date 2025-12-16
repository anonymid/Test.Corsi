import streamlit as st
import time
import random
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- CSS: MEMAKSA GRID DAN MEMBERSIHKAN TAMPILAN ---
st.markdown("""
<style>
    /* Paksa tombol navigasi tetap terlihat normal */
    .stButton > button {
        border-radius: 8px !important;
        margin-top: 10px;
    }
    
    /* Hilangkan padding berlebih di mobile */
    .main .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* CONTAINER GRID KHUSUS */
    .corsi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    /* Gaya Kotak Grid */
    .grid-box {
        width: 100%;
        aspect-ratio: 1/1;
        border: 1px solid #444;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI SIMPAN ---
def save_to_google_sheets(data):
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    try:
        requests.post(SCRIPT_URL, json=data, timeout=10)
    except:
        pass

# --- INITIAL STATE ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 0, 'data_diri': {}, 'skor_kuesioner': 0, 'sudah_simpan': False,
        'corsi': {'level': 1, 'sequence': [], 'user_input': [], 'playing_sequence': False, 'lives': 2, 'score': 0}
    })

# --- NAVIGATION ---

if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("Terimakasih telah bersedia menjadi responden.")
    bersedia = st.checkbox("Saya bersedia mengikuti penelitian ini")
    if st.button("Lanjut"):
        if bersedia: 
            st.session_state.step = 1
            st.rerun()

elif st.session_state.step == 1:
    st.header("Data Responden")
    with st.form("bio"):
        inisial = st.text_input("Inisial")
        wa = st.text_input("Nomor Whatsapp")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        if st.form_submit_button("Lanjut ke Kuesioner"):
            if inisial and wa:
                st.session_state.data_diri = {"Inisial": inisial, "WA": wa, "Umur": umur, "JK": jk}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Inisial dan WA wajib diisi")

elif st.session_state.step == 2:
    st.header("Kuesioner Singkat")
    with st.form("kues"):
        q1 = st.radio("Saya merasa sulit berhenti menggunakan internet", [1,2,3,4], horizontal=True)
        # Tambahkan pertanyaan lain di sini jika perlu
        if st.form_submit_button("Mulai Tes Corsi"):
            st.session_state.skor_kuesioner = q1
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.header("Instruksi Tes Corsi")
    st.info("Perhatikan urutan kotak yang akan menyala **BIRU**, lalu klik kotak tersebut sesuai urutannya.")
    if st.button("MULAI SEKARANG"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4
        st.rerun()

# --- HALAMAN GAME: SOLUSI GRID STABIL ---
elif st.session_state.step == 4:
    st.subheader(f"Level {st.session_state.corsi['level']} / 9")
    
    # CSS KHUSUS UNTUK TOMBOL GRID AGAR TETAP KOTAK 4x4
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            gap: 5px !important;
            width: 100% !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: none !important;
        }
        .stButton button {
            width: 100% !important;
            aspect-ratio: 1 / 1 !important;
            padding: 0 !important;
            border-radius: 4px !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    def next_level_logic():
        st.session_state.corsi['score'] = st.session_state.corsi['level']
        if st.session_state.corsi['level'] < 9:
            st.session_state.corsi['level'] += 1
            st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(st.session_state.corsi['level'] + 1)]
            st.session_state.corsi['user_input'] = []
            st.session_state.corsi['playing_sequence'] = True
            st.session_state.corsi['lives'] = 2
        else:
            st.session_state.step = 5
        st.rerun()

    # PHASE 1: MENAMPILKAN URUTAN (BLINK)
    if st.session_state.corsi['playing_sequence']:
        st.warning("Perhatikan...")
        grid_placeholder = st.empty()
        
        for target in st.session_state.corsi['sequence']:
            with grid_placeholder.container():
                for r in range(4):
                    cols = st.columns(4)
                    for c in range(4):
                        idx = r * 4 + c
                        if idx == target:
                            cols[c].button(" ", key=f"blink_{idx}_{time.time()}", type="primary", disabled=True)
                        else:
                            cols[c].button(" ", key=f"off_{idx}_{time.time()}", disabled=True)
            time.sleep(0.8)
            grid_placeholder.empty()
            time.sleep(0.2)
            
        st.session_state.corsi['playing_sequence'] = False
        st.rerun()

    # PHASE 2: INPUT USER
    else:
        st.success("Giliran Anda! Klik kotak.")
        for r in range(4):
            cols = st.columns(4)
            for c in range(4):
                idx = r * 4 + c
                if cols[c].button(" ", key=f"btn_{idx}"):
                    st.session_state.corsi['user_input'].append(idx)
                    curr_step = len(st.session_state.corsi['user_input']) - 1
                    
                    if idx != st.session_state.corsi['sequence'][curr_step]:
                        st.session_state.corsi['lives'] -= 1
                        if st.session_state.corsi['lives'] > 0:
                            st.error("Salah! Mengulang level ini...")
                            time.sleep(1)
                            st.session_state.corsi['user_input'] = []
                            st.session_state.corsi['playing_sequence'] = True
                        else:
                            st.session_state.step = 5
                        st.rerun()
                    elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                        next_level_logic()

elif st.session_state.step == 5:
    st.header("Selesai!")
    st.write("Terimakasih, data Anda telah tersimpan.")
    if not st.session_state.sudah_simpan:
        final_data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **st.session_state.data_diri,
            "Skor_Kuesioner": st.session_state.skor_kuesioner,
            "Skor_Corsi": st.session_state.corsi['score']
        }
        save_to_google_sheets(final_data)
        st.session_state.sudah_simpan = True
