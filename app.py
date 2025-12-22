import streamlit as st
import requests
import time
import random

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Tes Corsi Compact", layout="centered")

# --- URL SCRIPT GOOGLE KAMU ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- INIT STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1

# --- FUNGSI KIRIM DATA ---
def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS GLOBAL UNTUK MENGHILANGKAN WHITESPACE ---
st.markdown("""
<style>
    /* 1. HAPUS PADDING ATAS BAWAH HALAMAN AGAR NAIK KE ATAS */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    /* 2. HEADER LEBIH KECIL */
    h1 { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI HTML VISUAL (KOMPUTER MAIN) ---
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # UBAH height jadi 55px fix biar kecil
        boxes += f'<div style="float:left; width:23%; margin:1%; height:55px; background-color:{color}; border-radius:6px; border:2px solid #999; box-sizing:border-box;"></div>'
    
    return f'<div style="width:100%; overflow:hidden; margin-bottom:10px;">{boxes}</div>'

# --- FUNGSI TOMBOL INTERAKTIF (USER MAIN) ---
def render_buttons():
    st.markdown("""
    <style>
    /* 1. PAKSA HORIZONTAL */
    div[data-testid="stHorizontalBlock"] { flex-direction: row !important; }
    
    /* 2. PAKSA KOLOM 25% */
    div[data-testid="column"] { 
        width: 25% !important; 
        flex: 1 1 25% !important; 
        min-width: 0px !important;
        padding: 1px !important;
    }
    
    /* 3. TOMBOL COMPACT (TIDAK JUMBO) */
    div.stButton > button { 
        width: 100% !important; 
        height: 55px !important; /* Fix tinggi 55px */
        min-height: 55px !important;
        padding: 0 !important; 
        border-radius: 5px; 
        border: 2px solid #bbb; 
    }
    div.stButton > button:active { background-color: #007bff; color: white; }
    
    /* Hapus margin tombol */
    div.stButton { margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i), use_container_width=True)

# --- HALAMAN 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Tes Memori (Compact)")
    st.info("Versi ini lebih kecil dan muat satu layar.")
    
    with st.form("test_form"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai Tes"):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- HALAMAN 2: GAME ---
elif st.session_state.page == "corsi_game":
    # Header Level Kecil
    st.markdown(f"#### Level: {st.session_state.corsi_level - 1}")
    layar = st.empty()

    # IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.caption("Hafalkan urutan biru!")
            st.markdown(get_html(None), unsafe_allow_html=True)
            # Tombol Mulai dibuat compact
            if st.button("Mulai", type="primary", use_container_width=True):
                st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                st.session_state.corsi_user_input = []
                st.session_state.corsi_phase = "showing"
                st.rerun()

    # ANIMASI
    elif st.session_state.corsi_phase == "showing":
        layar.markdown(get_html(None), unsafe_allow_html=True)
        time.sleep(0.5)
        for item in st.session_state.corsi_sequence:
            layar.markdown(get_html(item), unsafe_allow_html=True) 
            time.sleep(0.8)
            layar.markdown(get_html(None), unsafe_allow_html=True) 
            time.sleep(0.3)
        st.session_state.corsi_phase = "input"
        st.rerun()

    # INPUT
    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.caption("Giliran Kamu! (Klik tombol)")
        render_buttons() 

        # Cek Jawaban
        if len(st.session_state.corsi_user_input) > 0:
            curr = len(st.session_state.corsi_user_input) - 1
            if st.session_state.corsi_user_input[curr] != st.session_state.corsi_sequence[curr]:
                st.toast("Salah! ❌")
                time.sleep(0.5)
                if st.session_state.corsi_lives > 0:
                    st.session_state.corsi_lives -= 1
                    st.session_state.corsi_phase = "idle"
                    st.rerun()
                else:
                    st.session_state.page = "saving"
                    st.rerun()
            elif len(st.session_state.corsi_user_input) == len(st.session_state.corsi_sequence):
                st.toast("Benar! 🎉")
                time.sleep(0.5)
                st.session_state.corsi_level += 1
                st.session_state.corsi_lives = 1
                st.session_state.corsi_phase = "idle"
                st.rerun()

# --- HALAMAN 3: SAVING ---
elif st.session_state.page == "saving":
    st.header("Selesai")
    status = st.empty()
    status.info("Menyimpan...")
    
    payload = st.session_state.user_data
    payload['skorCorsi'] = st.session_state.corsi_level - 1
    
    if send_data(payload):
        status.empty()
        st.success("Tersimpan!")
        if st.button("Ulang"):
            st.session_state.clear()
            st.rerun()
    else:
        status.error("Gagal koneksi.")
