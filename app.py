import streamlit as st
import requests
import time
import random

# --- SETUP HALAMAN ---
# Kita set layout="wide" biar gak terlalu kepotong padding bawaan
st.set_page_config(page_title="Tes Corsi Mobile Fix", layout="wide")

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

# --- KIRIM DATA ---
def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS KHUSUS MOBILE ---
# Kita gunakan @media query untuk memaksa tampilan HP
st.markdown("""
<style>
    /* 1. HAPUS PADDING HALAMAN BIAR LEGA */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* 2. HEADER TENGAH */
    h1, h2, h3, h4, p { text-align: center; }

    /* =========================================
       BAGIAN INI YANG MEMAKSA 4 KOLOM DI HP
       ========================================= */
    
    /* Target semua layar (termasuk HP) */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important; /* Paksa baris ke samping */
        flex-wrap: nowrap !important;   /* DILARANG TURUN BARIS */
        gap: 5px !important;            /* Jarak antar kolom tipis */
        justify-content: center !important;
    }

    /* Paksa Kolom agar mengecil dan muat */
    div[data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
        min-width: 10px !important; /* Biarkan mengecil sampai 10px pun boleh */
        padding: 0 !important;
    }

    /* STYLE TOMBOL (Soal & Jawaban) */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; /* KOTAK */
        height: auto !important;
        padding: 0 !important;
        border-radius: 6px;
        border: 2px solid #999;
        margin: 0 !important;
    }
    
    /* Biar tombol gak kegedean di layar laptop */
    @media (min-width: 600px) {
        div.stButton > button {
            max-width: 60px !important; /* Max lebar di laptop */
        }
    }
    
    div.stButton > button:active { background-color: #007bff; color: white; }
    
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL (SOAL) ---
def get_html(highlight_idx=None):
    # Kita buat grid manual pakai HTML biar presisi
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        # Grid System HTML
        boxes += f"""
        <div style="
            display: inline-block;
            width: 20%; 
            margin: 1.5%;
            aspect-ratio: 1/1; 
            background-color: {color};
            border-radius: 6px;
            border: 2px solid #999;
            vertical-align: top;
        "></div>
        """
    
    # Wadah utama max 300px biar sama kayak tombol
    return f"""
    <div style="
        width: 100%; 
        max-width: 350px; 
        margin: 0 auto 20px auto; 
        text-align: center;
    ">
        {boxes}
    </div>
    """

# --- FUNGSI TOMBOL (JAWABAN) ---
def render_buttons():
    # Kuncinya: Wadah container ini kita batasi lebarnya biar center
    # Kita pakai 3 kolom kosong di kiri kanan untuk "memeras" grid ke tengah (di laptop)
    # Tapi di HP kita biarkan full width
    
    # Wadah pembungkus agar max-width terjaga
    container = st.container()
    
    # CSS Injector lokal untuk membatasi lebar container tombol ini saja
    st.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
            max-width: 400px !important; /* Grid tombol maks 400px */
            margin: 0 auto !important;   /* Posisi Tengah */
        }
    </style>
    """, unsafe_allow_html=True)
    
    with container:
        for row in range(4):
            cols = st.columns(4) # CSS Global di atas akan memaksa ini tetap 4 kolom
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i), use_container_width=True)

# --- HALAMAN 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Tes Memori")
    st.write("Versi Anti-Stack Mobile")
    with st.form("f"):
        nama = st.text_input("Nama")
        wa = st.text_input("WA")
        if st.form_submit_button("Mulai", use_container_width=True):
            st.session_state.user_data = {"inisial": nama, "wa": wa}
            st.session_state.page = "corsi_game"
            st.rerun()

# --- HALAMAN 2: GAME ---
elif st.session_state.page == "corsi_game":
    st.markdown(f"#### Level: {st.session_state.corsi_level - 1}")
    layar = st.empty()

    # IDLE
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.info("Hafalkan urutan biru!")
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
