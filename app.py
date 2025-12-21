import streamlit as st
import requests
import time
import random

# --- SETUP ---
st.set_page_config(page_title="Tes Corsi Lite", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1

# --- FUNGSI-FUNGSI UTAMA ---

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# 1. FIX VISUAL (Agar kotak tidak jadi teks aneh)
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # String dibuat rapat satu baris
        boxes += f'<div style="background-color:{color}; border-radius:6px; border:2px solid #999; height:60px;"></div>'
    return f'<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:5px; margin-bottom:15px;">{boxes}</div>'

# 2. FIX TAMPILAN HP (Agar tombol tetap 4 kolom)
def render_buttons():
    st.markdown("""
    <style>
    div[data-testid="column"] { width: 25% !important; flex: 0 0 25% !important; min-width: 0 !important; padding: 0 1px !important; }
    div.stButton > button { width: 100%; aspect-ratio: 1/1; padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i), use_container_width=True)

# --- SLIDE 1: WELCOME & DATA (DIGABUNG BIAR CEPAT) ---
if st.session_state.page == "welcome":
    st.title("Tes Corsi (Versi Test)")
    st.info("Ini versi singkat untuk cek sistem.")
    
    with st.form("form_test"):
        nama = st.text_input("Nama Inisial")
        wa = st.text_input("No WA")
        soal_test = st.radio("Apakah sistem ini berjalan lancar?", ["Ya", "Tidak"])
        
        if st.form_submit_button("Lanjut ke Game"):
            st.session_state.user_data = {"inisial": nama, "wa": wa, "test_response": soal_test}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- SLIDE 2: GAME CORSI ---
elif st.session_state.page == "corsi_game":
    st.subheader(f"Level: {st.session_state.corsi_level - 1}")
    layar = st.empty() # Placeholder agar tidak numpuk

    # FASE IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.write("Hafalkan urutan biru.")
            st.markdown(get_html(None), unsafe_allow_html=True)
            if st.button("Mulai", type="primary"):
                st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                st.session_state.corsi_user_input = []
                st.session_state.corsi_phase = "showing"
                st.rerun()

    # FASE SHOWING (ANIMASI)
    elif st.session_state.corsi_phase == "showing":
        layar.markdown(get_html(None), unsafe_allow_html=True)
        time.sleep(0.5)
        for item in st.session_state.corsi_sequence:
            layar.markdown(get_html(item), unsafe_allow_html=True) # Nyala
            time.sleep(0.8)
            layar.markdown(get_html(None), unsafe_allow_html=True) # Mati
            time.sleep(0.3)
        st.session_state.corsi_phase = "input"
        st.rerun()

    # FASE INPUT
    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.success("Giliran kamu klik!")
        render_buttons() # Tombol interaktif

        # LOGIKA CEK JAWABAN
        if len(st.session_state.corsi_user_input) > 0:
            curr = len(st.session_state.corsi_user_input) - 1
            # Jika Salah
            if st.session_state.corsi_user_input[curr] != st.session_state.corsi_sequence[curr]:
                st.toast("Salah!")
                time.sleep(0.5)
                if st.session_state.corsi_lives > 0:
                    st.session_state.corsi_lives -= 1
                    st.session_state.corsi_phase = "idle" # Ulang level
                    st.rerun()
                else:
                    st.session_state.page = "saving" # Game Over
                    st.rerun()
            # Jika Benar Selesai
            elif len(st.session_state.corsi_user_input) == len(st.session_state.corsi_sequence):
                st.toast("Benar!")
                time.sleep(0.5)
                st.session_state.corsi_level += 1
                st.session_state.corsi_lives = 1
                st.session_state.corsi_phase = "idle"
                st.rerun()

# --- SLIDE 3: SIMPAN DATA ---
elif st.session_state.page == "saving":
    st.header("Selesai")
    status = st.empty()
    status.info("Sedang menyimpan...")
    
    payload = st.session_state.user_data
    payload['skorCorsi'] = st.session_state.corsi_level - 1
    
    if send_data(payload):
        status.empty() # Hapus loading
        st.success("Data Tersimpan! (Cek Google Sheet)")
        if st.button("Ulangi Tes"):
            for key in st.session_state.keys(): del st.session_state[key]
            st.rerun()
    else:
        status.error("Gagal koneksi.")
