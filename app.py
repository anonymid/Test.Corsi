import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import requests

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- CSS CUSTOM: GRID 4x4 RAPI, TANPA SHADOW, TANPA GAP ---
st.markdown("""
<style>
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 0px !important;
        border: 0.5px solid #dddddd !important;
        background-color: #f8f9fa;
        box-shadow: none !important;
        transition: none !important;
    }
    /* Warna saat blink biru */
    button[kind="primary"] {
        background-color: #0000FF !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stButton button:focus, .stButton button:active, .stButton button:hover {
        box-shadow: none !important;
        background-color: #f8f9fa;
        border: 0.5px solid #dddddd !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI SIMPAN DATA ---
def save_to_google_sheets(data):
    # GANTI DENGAN URL APPS SCRIPT KAMU
    SCRIPT_URL = "ISI_URL_APPS_SCRIPT_DISINI"
    try:
        requests.post(SCRIPT_URL, json=data, timeout=10)
    except:
        pass

# --- INISIALISASI STATE ---
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 0,
        'data_diri': {},
        'skor_kuesioner': 0,
        'sudah_simpan': False,
        'corsi': {
            'level': 1,
            'sequence': [],
            'user_input': [],
            'playing_sequence': False,
            'lives': 2,
            'score': 0
        }
    })

# --- NAVIGASI HALAMAN ---

# 0. WELCOME
if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("Terimakasih telah bersedia menjadi responden kami dalam penelitian ini. Semua data dirahasiakan. Tersedia e-money untuk 5 orang terpilih.")
    bersedia = st.checkbox("Apakah anda bersedia menjadi responden?")
    if st.button("Lanjut"):
        if bersedia:
            st.session_state.step = 1
            st.rerun()
        else:
            st.warning("Mohon centang pers
