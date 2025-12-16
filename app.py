import streamlit as st
import time
import random
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠", layout="centered")

# --- 2. CSS SAKTI: FIX GRID MOBILE & TOMBOL ---
st.markdown("""
<style>
    /* Paksa Grid 4x4 Tetap Berjejer di HP */
    .grid-container {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Matikan perilaku kolom default Streamlit agar tidak tumpuk vertikal */
    [data-testid="column"] {
        width: unset !important;
        flex: unset !important;
        min-width: unset !important;
    }
    
    /* Styling Tombol Grid (Kotak Tajam & Tanpa Bayangan) */
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0 !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        border: 0.5px solid #555 !important;
        transition: none !important;
    }

    /* Warna Blink Biru Pekat */
    button[kind="primary"] {
        background-color: #0000FF !important;
        color: transparent !important;
        border: none !important;
    }

    /* Kembalikan gaya tombol Navigasi (Lanjut/Mulai) */
    div.stButton > button:not([key*="grid_"]):not([key*="blink_"]):not([key*="off_"]):not([key*="user_"]):not([key*="on_"]) {
        aspect-ratio: auto !important;
        width: auto !important;
        padding: 10px 25px !important;
        border-radius: 8px !important;
        background-color: #FF4B4B !important;
