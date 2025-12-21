import streamlit as st
import requests
import time
import random

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Tes Corsi Final", layout="centered")

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

# --- FUNGSI HTML VISUAL (KOMPUTER MAIN) ---
# Dibuat satu baris rapat supaya tidak bocor jadi teks
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Kita pakai float left teknik lama yang paling stabil di semua browser
        boxes += f'<div style="float:left; width:23%; margin:1%; height:60px; background-color:{color}; border-radius:6px; border:2px solid #999; box-sizing:border-box;"></div>'
    
    return f'<div style="width:100%; overflow:hidden; margin-bottom:15px;">{boxes}</div>'

# --- FUNGSI TOMBOL INTERAKTIF (USER MAIN) ---
# CSS INI SUDAH DIUPDATE AGAR TIDAK JUMBO DI HP
def render_buttons():
    st.markdown("""
    <style>
    /* 1. PAKSA WADAH UTAMA JADI BARIS (ROW), BUKAN KOLOM */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important; 
        flex-wrap: nowrap !important;
    }
    
    /* 2. PAKSA KOLOM JADI 25% */
    div[data-testid="column"] { 
        width: 25% !important; 
        flex: 1 1 25% !important; 
        min-width: 0px !important;
        padding: 1px !important;
    }
    
    /* 3. TOMBOL KOTAK RAPI */
    div.stButton > button { 
        width: 100% !important; 
        aspect-ratio: 1/1; 
        height: auto !important; 
        padding: 0 !important; 
        border-radius: 5px; 
        border: 2px solid #bbb; 
    }
    
    /* Efek Klik */
    div.stButton > button:active { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i), use_container_width=True)

# --- HALAMAN 1: WELCOME & DATA ---
if st.session_state.page == "welcome":
    st.title("Tes Memori")
    st.info("Versi Final: Anti-Jumbo Mobile")
    
    with st.form("test_form"):
        nama = st.text_input("Nama Inisial")
        wa = st.text_input("No WA")
        if st.form_submit_button("Mulai Tes"):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- HALAMAN 2: GAME ---
elif st.session_state.page == "corsi_game":
    st.subheader(f"Level: {st.session_state.corsi_level - 1}")
    layar = st.empty()

    # IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.write("Hafalkan urutan biru!")
            st.markdown(get_html(None), unsafe_allow_html=True)
            if st.button("Mulai Level Ini", type="primary"):
                st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                st.session_state.corsi_user_input = []
                st.session_state.corsi_phase = "showing"
                st.rerun()

    # ANIMASI
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

    # INPUT
    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.success("Giliran Kamu! (Klik tombol)")
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
    status.info("Menyimpan data...")
    
    payload = st.session_state.user_data
    payload['skorCorsi'] = st.session_state.corsi_level - 1
    
    if send_data(payload):
        status.empty()
        st.success("Data Tersimpan! Terima kasih.")
        if st.button("Ulang"):
            st.session_state.clear()
            st.rerun()
    else:
        status.error("Gagal koneksi.")
