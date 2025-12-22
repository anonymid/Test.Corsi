import streamlit as st
import requests
import time
import random

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Tes Corsi Final", layout="centered")

# --- URL GOOGLE SCRIPT ---
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

# --- CSS: PAKSA UKURAN KECIL (300px) & TENGAH ---
st.markdown("""
<style>
    /* 1. KUNCI LEBAR KONTEN AGAR TIDAK MELEBAR (ANTI SCROLL SAMPING) */
    .block-container {
        padding: 1rem 0.5rem !important; /* Padding tipis */
        max-width: 100% !important;
    }
    
    /* 2. HEADER KECIL */
    h1 { font-size: 1.2rem !important; text-align: center; }
    p, div { font-size: 0.9rem !important; }
    
    /* 3. WADAH GRID: DIKUNCI MAX 300px DAN DI-TENGAH-KAN */
    /* Ini trik biar di HP gak kegedean */
    div[data-testid="stVerticalBlock"] > div {
        margin-left: auto !important;
        margin-right: auto !important;
        max-width: 320px !important; /* KUNCI LEBAR DISINI */
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI HTML VISUAL (KOMPUTER MAIN) ---
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Ukuran fix dalam persen relatif terhadap wadah 320px tadi
        boxes += f'<div style="float:left; width:22%; margin:1.5%; padding-bottom:22%; background-color:{color}; border-radius:5px; border:2px solid #999; height:0;"></div>'
    
    # Wadah ini akan mengikuti max-width 320px dari CSS di atas
    return f'<div style="width:100%; overflow:hidden; margin-bottom:10px;">{boxes}</div>'

# --- FUNGSI TOMBOL INTERAKTIF (USER MAIN) ---
def render_buttons():
    st.markdown("""
    <style>
    /* PAKSA ROW */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    
    /* PAKSA KOLOM */
    div[data-testid="column"] {
        width: 25% !important;
        flex: 1 1 25% !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    /* TOMBOL KOTAK 1:1 */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        padding: 0 !important;
        border-radius: 5px;
        border: 2px solid #bbb;
    }
    
    div.stButton > button:active { background-color: #007bff; color: white; }
    div.stButton { margin: 0 !important; width: 100% !important; }
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
    st.title("Tes Memori (Mini)")
    st.caption("Versi 300px Fixed (Muat Semua HP)")
    with st.form("f"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai", use_container_width=True):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- HALAMAN 2: GAME ---
elif st.session_state.page == "corsi_game":
    # Header level di tengah
    st.markdown(f"<h4 style='text-align:center; margin:0;'>Level: {st.session_state.corsi_level - 1}</h4>", unsafe_allow_html=True)
    layar = st.empty()

    # IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.caption("Hafalkan urutan biru!")
            st.markdown(get_html(None), unsafe_allow_html=True)
            if st.button("Mulai Level Ini", type="primary", use_container_width=True):
                st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                st.session_state.corsi_user_input = []
                st.session_state.corsi_phase = "showing"
                st.rerun()

    # SHOWING
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
    status.info("Simpan...")
