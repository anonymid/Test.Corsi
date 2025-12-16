import streamlit as st
import time
import random
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- CSS: HANYA UNTUK NAVIGASI ---
st.markdown("""
<style>
    /* Tombol Navigasi (Lanjut/Mulai) tetap standar */
    .stButton > button {
        border-radius: 8px;
    }
    /* Sembunyikan Header Streamlit biar fokus */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    bersedia = st.checkbox("Saya bersedia")
    if st.button("Lanjut"):
        if bersedia: st.session_state.step = 1; st.rerun()

elif st.session_state.step == 1:
    st.header("Data Responden")
    with st.form("bio"):
        inisial = st.text_input("Inisial")
        wa = st.text_input("WA")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("JK", ["Pria", "Wanita"])
        submit = st.form_submit_button("Next")
        if submit:
            st.session_state.data_diri = {"Inisial": inisial, "WA": wa, "Umur": umur, "JK": jk}
            st.session_state.step = 2; st.rerun()

elif st.session_state.step == 2:
    st.header("Kuesioner")
    with st.form("kues"):
        # Anggap kuesioner singkat untuk testing
        q1 = st.radio("Saya sulit berhenti main internet", [1,2,3,4], horizontal=True)
        if st.form_submit_button("Mulai Tes Corsi"):
            st.session_state.skor_kuesioner = q1
            st.session_state.step = 3; st.rerun()

elif st.session_state.step == 3:
    st.header("Tes Corsi")
    st.write("Ingat urutan kotak BIRU.")
    if st.button("MULAI TES"):
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)]
        st.session_state.corsi['playing_sequence'] = True
        st.session_state.step = 4; st.rerun()

# --- BAGIAN GAME: GRID PERMANEN 4X4 ---
elif st.session_state.step == 4:
    st.write(f"### Level {st.session_state.corsi['level']}")
    
    # Fungsi pembantu buat bikin grid pake tombol asli agar responsif klik-nya
    def render_grid(target_id=None, is_off=False):
        # Kita pakai 4 kolom standar tapi dengan CSS 'gap 0' dan 'flex-row'
        # Supaya paksa 4x4, kita bungkus dalam container khusus
        st.markdown("""
            <style>
                div[data-testid="column"] {
                    flex: 1 1 20% !important;
                    min-width: 20% !important;
                }
                div[data-testid="stHorizontalBlock"] {
                    display: flex !important;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    gap: 5px !important;
                }
                .stButton button {
                    width: 100% !important;
                    aspect-ratio: 1/1 !important;
                    border-radius: 4px !important;
                    padding: 0px !important;
                    box-shadow: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Render 4 Baris
        for r in range(4):
            cols = st.columns(4)
            for c in range(4):
                idx = r * 4 + c
                # Jika sedang blinking (target_id cocok)
                if target_id is not None and idx == target_id and not is_off:
                    cols[c].button(" ", key=f"grid_{idx}_{time.time()}", type="primary", disabled=True)
                else:
                    # Jika mode input user
                    if not st.session_state.corsi['playing_sequence']:
                        if cols[c].button(" ", key=f"btn_{idx}"):
                            handle_click(idx)
                    else:
                        # Jika mode nonton sequence (tombol mati)
                        cols[c].button(" ", key=f"view_{idx}_{time.time()}", disabled=True)

    def handle_click(clicked_idx):
        st.session_state.corsi['user_input'].append(clicked_idx)
        curr = len(st.session_state.corsi['user_input']) - 1
        if clicked_idx != st.session_state.corsi['sequence'][curr]:
            st.session_state.corsi['lives'] -= 1
            if st.session_state.corsi['lives'] > 0:
                st.error("Salah! Ulangi.")
                time.sleep(1)
                st.session_state.corsi['user_input'] = []
                st.session_state.corsi['playing_sequence'] = True
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
            else:
                st.session_state.step = 5
            st.rerun()

    if st.session_state.corsi['playing_sequence']:
        placeholder = st.empty()
        for target in st.session_state.corsi['sequence']:
            with placeholder.container():
                render_grid(target_id=target)
            time.sleep(0.8)
            with placeholder.container():
                render_grid(target_id=target, is_off=True)
            time.sleep(0.3)
        st.session_state.corsi['playing_sequence'] = False
        st.rerun()
    else:
        st.success("Giliran Anda!")
        render
