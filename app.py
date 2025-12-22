import streamlit as st
import requests
import time
import random

# --- SETUP ---
st.set_page_config(page_title="Tes Corsi Pixel Fix", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1

# --- KIRIM DATA ---
def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS KHUSUS: KUNCI MATI UKURAN (PIXEL) ---
st.markdown("""
<style>
    /* 1. BERSIHKAN PADDING HALAMAN BIAR GAK SUMPEK */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* 2. SEMUA ISI DI-TENGAH-KAN */
    div[data-testid="stVerticalBlock"] { align-items: center; }
    
    /* 3. UBAH TOMBOL JADI KOTAK KECIL FIX (55px) */
    div.stButton > button {
        width: 55px !important;  /* LEBAR FIX */
        height: 55px !important; /* TINGGI FIX */
        min-width: 55px !important;
        min-height: 55px !important;
        padding: 0 !important;
        border-radius: 8px;
        border: 2px solid #bbb;
        margin: 2px !important; /* Jarak antar tombol */
    }
    div.stButton > button:active { background-color: #007bff; color: white; }
    
    /* 4. MENGECILKAN KOLOM STREAMLIT AGAR PAS DENGAN TOMBOL */
    div[data-testid="column"] {
        width: auto !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
        padding: 0 !important;
    }
    
    /* 5. TENGAHKAN GRID TOMBOL */
    div[data-testid="stHorizontalBlock"] {
        justify-content: center !important;
        gap: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL (SOAL) - KITA SAMAKAN JADI 55px ---
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Disini kita pakai pixel (55px) juga biar sama persis kayak tombol
        boxes += f'<div style="float:left; width:55px; height:55px; margin:2px; background-color:{color}; border-radius:8px; border:2px solid #999; box-sizing:border-box;"></div>'
    
    # Bungkus dalam wadah selebar (55px + 4px margin) * 4 = ~240px. Center align.
    return f'<div style="width:240px; margin:0 auto 15px auto; overflow:hidden;">{boxes}</div>'

# --- FUNGSI TOMBOL (JAWABAN) ---
def render_buttons():
    # Grid 4x4
    # Kita pakai container biasa, CSS di atas yang akan maksa ukurannya jadi 55px
    with st.container():
        for row in range(4):
            # Buat 4 kolom
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                # Tombol Kosong
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i))

# --- HALAMAN 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Tes Memori")
    st.caption("Versi Pixel Fix (Ukuran Dijamin Sama)")
    with st.form("f"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai", use_container_width=True):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- HALAMAN 2: GAME ---
elif st.session_state.page == "corsi_game":
    st.markdown(f"<h4 style='text-align:center;'>Level: {st.session_state.corsi_level - 1}</h4>", unsafe_allow_html=True)
    layar = st.empty()

    # IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.caption("Hafalkan urutan biru!")
            st.markdown(get_html(None), unsafe_allow_html=True)
            # Tombol Mulai (kecil & center)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
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
