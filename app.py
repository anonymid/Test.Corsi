import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import time

# Pengaturan Halaman
st.set_page_config(page_title="Penelitian Memori Kerja", layout="centered")

# Inisialisasi Database Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Inisialisasi State (Penyimpanan Sementara)
if 'page' not in st.session_state:
    st.session_state.page = "welcome"
if 'corsi_level' not in st.session_state:
    st.session_state.corsi_level = 2
if 'corsi_lives' not in st.session_state:
    st.session_state.corsi_lives = 1
if 'corsi_score' not in st.session_state:
    st.session_state.corsi_score = 0
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- FUNGSI SIMPAN DATA ---
def save_to_sheet(final_data):
    # Membaca data lama
    existing_data = conn.read(worksheet="Sheet1")
    updated_df = pd.concat([existing_data, pd.DataFrame([final_data])], ignore_index=True)
    # Menulis kembali ke Google Sheets
    conn.update(worksheet="Sheet1", data=updated_df)

# --- SLIDE 0: WELCOME ---
if st.session_state.page == "welcome":
    st.title("Penelitian Pengaruh Ketergantungan Internet terhadap Kinerja Memori Kerja")
    st.write("""
    Terimakasih telah bersedia menjadi responden kami dalam penelitian ini, semua data yang anda masukkan 
    akan kami gunakan untuk keperluan akademik dan akan kami jaga kerahasiaannya. Sebagai bentuk terimakasih, 
    silahkan isi nomor whatsapp dengan benar, kami akan memberikan e-money kepada 5 orang yang terpilih.
    """)
    
    consent = st.checkbox("Apakah anda bersedia menjadi responden?")
    if st.button("Next", disabled=not consent):
        st.session_state.page = "data_responden"
        st.rerun()

# --- SLIDE 1: DATA RESPONDEN ---
elif st.session_state.page == "data_responden":
    st.header("Data Responden")
    st.info("Mohon diisi dengan kondisi anda yang sebenarnya.")
    
    with st.form("form_responden"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial")
        st.session_state.user_data['umur'] = st.selectbox("Umur", list(range(17, 29)))
        st.session_state.user_data['gender'] = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        st.session_state.user_data['status'] = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        st.session_state.user_data['domisili'] = st.text_input("Domisili")
        st.session_state.user_data['wa'] = st.text_input("Nomor Whatsapp")
        st.session_state.user_data['durasi'] = st.selectbox("Durasi Penggunaan Internet Perhari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        st.session_state.user_data['tujuan'] = st.selectbox("Tujuan Penggunaan Internet", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        st.session_state.user_data['aktivitas'] = st.selectbox("Jenis Aktifitas Dominan", ["Scrolling Pasif", "Scrolling Aktif"])
        st.session_state.user_data['gadget'] = st.radio("Menggunakan Gadget sebelum tidur?", ["Ya", "Tidak"])
        st.session_state.user_data['tidur_durasi'] = st.selectbox("Durasi Rata-rata tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        st.session_state.user_data['tidur_kualitas'] = st.selectbox("Kualitas tidur", ["Baik", "Sedang", "Buruk
