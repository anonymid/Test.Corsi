import streamlit as st
import requests
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="Corsi Final Fix", layout="centered")
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

# --- CSS ANTI-ERROR & ANTI-JUMBO ---
st.markdown("""
<style>
    /* 1. HAPUS PADDING BIAR LEGA */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* 2. TENGAHKAN SEMUA */
    div[data-testid="stVerticalBlock"] { align-items: center; text-align: center; }
    
    /* 3. TOMBOL (JAWABAN) DIKUNCI MATI UKURANNYA */
    /* Ini biar gak melar jadi raksasa di HP */
    div.stButton > button {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        padding: 0 !important;
        border-radius: 6px;
        border: 2px solid #bbb;
        margin: 2px !important;
    }
    div.stButton > button:active { background-color: #007bff; color: white; }

    /* 4. PAKSA 4 KOLOM (JANGAN TURUN KE BAWAH) */
    div[data-testid="column"] {
        width: auto !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
        padding: 0 !important;
    }
    
    /* 5. RAPATKAN GRID TOMBOL */
    div[data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        gap: 0px !important;
        flex-wrap: nowrap !important; /* HARAM TURUN BARIS */
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL (SOAL) ---
# FIX: SAYA HAPUS INDENTASI DAN MULTILINE STRING
# HTML ditulis satu baris lurus biar gak muncul teksnya
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Style ditulis rapat tanpa spasi
        boxes += f'<div style="float:left;width:50px;height:50px;margin:2px;background-color:{color};border-radius:6px;border:2px solid #999;"></div>'
    
    # Bungkus wadah selebar (50px+4px)*4 = ~220px. Center.
    return f'<div style="width:220px;margin:0 auto 20px auto;overflow:hidden;">{boxes}</div>'

# --- FUNGSI INPUT (JAWABAN) ---
def render_buttons():
    # Grid dibuat manual pakai container biar kena CSS Global
    with st.container():
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i))

# --- PAGE 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Tes Memori")
    st.caption("Versi Final Anti-Bug")
    with st.form("f"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai", use_container_width=True):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- PAGE 2: GAME ---
elif st.session_state.page == "corsi_game":
    st.markdown(f"**Level: {st.session_state.corsi_level - 1}**")
    layar = st.empty()

    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.info("Hafalkan biru!")
            # Render HTML Soal
            st.markdown(get_html(None), unsafe_allow_html=True)
            
            # Tombol Mulai
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Mulai Level", type="primary"):
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
