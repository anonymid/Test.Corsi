import streamlit as st
import requests
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="Corsi Responsive", layout="centered")
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

# --- CSS RESPONSIVE (JURUS UTAMA) ---
st.markdown("""
<style>
    /* 1. BERSIHKAN LAYAR */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 2. CONTAINER TOMBOL (GRID SYSTEM) */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important; /* WAJIB 4 KOLOM */
        margin: 0 auto !important; /* Posisi Tengah */
        gap: 10px !important;
    }

    /* --- RESPONSIVE LOGIC --- */
    
    /* A. TAMPILAN HP (Default) */
    div[data-testid="stHorizontalBlock"] {
        max-width: 320px !important; /* Lebar pas untuk HP */
    }

    /* B. TAMPILAN PC/TABLET (Layar > 600px) */
    @media (min-width: 600px) {
        div[data-testid="stHorizontalBlock"] {
            max-width: 500px !important; /* Lebar lebih gede buat PC */
            gap: 15px !important;
        }
    }

    /* 3. RESET KOLOM BAWAAN */
    div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 4. STYLE TOMBOL (WAJIB KOTAK) */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; /* KUNCI KOTAK SEMPURNA */
        height: auto !important;
        padding: 0 !important;
        border-radius: 8px;
        border: 2px solid #bbb;
    }
    div.stButton > button:active { background-color: #007bff; color: white; }
    div.stButton { margin: 0 !important; }
    
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL (SOAL) ---
# Menggunakan CSS Inline yang support max-width 100% agar ikut ukuran container
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Kita pakai persentase width agar responsif mengikuti wadah induknya
        boxes += f'<div style="background-color:{color};aspect-ratio:1/1;border-radius:8px;border:2px solid #999;"></div>'
    
    # Wadah utama HTML Soal
    # Di HP dia akan kecil (320px), di PC dia akan membesar (500px) mengikuti style CSS di atas
    return f"""
    <div style="
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        max-width: 500px; /* Max width PC */
        width: 100%;      /* Agar mengecil di HP */
        margin: 0 auto 20px auto;
    ">
        {boxes}
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
    st.write("Versi Responsive (HP Rapi, PC Jelas)")
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
