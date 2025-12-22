import streamlit as st
import requests
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="Corsi Final Kotak", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS GRID SYSTEM (KOTAK TAJAM) ---
st.markdown("""
<style>
    /* 1. LAYOUT HALAMAN */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* 2. GRID SYSTEM MUTLAK (HP & PC) */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important; /* 4 Kolom */
        gap: 8px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* ATUR LEBAR TOTAL BIAR PAS */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] { max-width: 300px !important; }
    }
    @media (min-width: 601px) {
        div[data-testid="stHorizontalBlock"] { max-width: 450px !important; }
    }

    /* 3. RESET ELEMENT KOLOM */
    div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 4. TOMBOL JADI KOTAK TAJAM (SQUARE) */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        min-height: 0 !important;
        padding: 0 !important;
        
        /* INI PERBAIKANNYA: */
        border-radius: 4px !important; /* Dikecilin biar gak jadi lingkaran */
        border: 2px solid #bbb;
        margin: 0 !important;
        line-height: 0 !important;
    }
    div.stButton > button:active { background-color: #007bff; color: white; }
    div.stButton { margin: 0 !important; width: 100% !important; }
    
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL (SOAL) ---
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # border-radius disamakan 4px
        boxes += f'<div style="background-color:{color}; aspect-ratio:1/1; border-radius:4px; border:2px solid #999; width:100%;"></div>'
    
    return f"""
    <div style="
        display: grid; 
        grid-template-columns: repeat(4, 1fr); 
        gap: 8px; 
        width: 100%;
        max-width: 450px; /* Default PC */
        margin: 0 auto 20px auto;
    ">
    <style>
    @media (max-width: 600px) {{ 
        .soal-container {{ max-width: 300px !important; }} 
    }}
    </style>
    <div class="soal-container" style="display:contents;">
        {boxes}
    </div>
    </div>
    """

# --- FUNGSI INPUT (JAWABAN) ---
def render_buttons():
    with st.container():
        for row in range(4):
            cols = st.columns(4) 
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i))

# --- PAGE 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Tes Memori")
    st.write("Versi Final: Kotak (Bukan Bulet)")
    with st.form("f"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai", use_container_width=True):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- PAGE 2: GAME ---
elif st.session_state.page == "corsi_game":
    st.markdown(f"<h4 style='text-align:center'>Level: {st.session_state.corsi_level - 1}</h4>", unsafe_allow_html=True)
    layar = st.empty()

    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.info("Hafalkan urutan biru!")
            st.markdown(get_html(None), unsafe_allow_html=True)
            
            # Tombol Mulai
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Mulai", type="primary", use_container_width=True):
                    st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                    st.session_state.corsi_user_input = []
                    st.session_state.corsi_phase = "showing"
                    st.rerun()

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

    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.success("Giliran Kamu!")
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

# --- PAGE 3: SAVING ---
elif st.session_state.page == "saving":
    st.header("Selesai")
    status = st.empty()
    status.info("Simpan...")
    
    payload = st.session_state.user_data
    payload['skorCorsi'] = st.session_state.corsi_level - 1
    
    if send_data(payload):
        status.empty()
        st.success("Tersimpan!")
        if st.button("Ulang"):
            st.session_state.clear()
            st.rerun()
    else:
        status.error("Gagal.")
