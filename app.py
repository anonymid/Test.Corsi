import streamlit as st
import requests
import time
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Penelitian Memori Kerja", layout="centered")

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
if 'corsi_score' not in st.session_state: st.session_state.corsi_score = 0

# --- FUNGSI KIRIM DATA ---
def send_data_to_google_script(final_data):
    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=final_data)
        return response.status_code == 200
    except:
        return False

# --- FUNGSI HTML VISUAL (Fix: Satu baris agar tidak bocor jadi teks) ---
def get_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        border = "3px solid #0056b3" if i == highlight_idx else "2px solid #bbb"
        # PENTING: String HTML ini jangan di-enter/spasi aneh-aneh
        boxes += f'<div style="background-color:{color}; border-radius:8px; border:{border}; height:70px; transition: background-color 0.1s;"></div>'
    return f'<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:20px;">{boxes}</div>'

# --- FUNGSI TOMBOL INPUT (Fix: Paksa 4 kolom di HP) ---
def render_buttons():
    # CSS INI YANG MEMPERBAIKI TAMPILAN HP
    st.markdown("""
    <style>
    /* Paksa kolom Streamlit selebar 25% (4 kolom) bahkan di layar HP */
    div[data-testid="column"] {
        width: 25% !important;
        flex: 0 0 25% !important;
        min-width: 0 !important;
        padding: 0 2px !important;
    }
    /* Styling tombol */
    div.stButton > button {
        width: 100%;
        height: 60px; /* Tinggi tombol */
        border-radius: 6px;
        border: 2px solid #bbb;
        padding: 0 !important;
    }
    div.stButton > button:active {
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    input_container = st.container()
    with input_container:
        for row in range(4):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                cols[col].button("⬜", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i), use_container_width=True)

# ==========================================
# SLIDE 1: WELCOME
# ==========================================
if st.session_state.page == "welcome":
    st.title("Penelitian Memori Kerja")
    st.write("Terimakasih telah bersedia menjadi responden. Data Anda aman.")
    if st.button("Saya Bersedia"):
        st.session_state.page = "data_diri"
        st.rerun()

# ==========================================
# SLIDE 2: DATA DIRI
# ==========================================
elif st.session_state.page == "data_diri":
    st.header("Data Responden")
    with st.form("form_data"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial")
        st.session_state.user_data['wa'] = st.text_input("Nomor WA (Untuk E-Money)")
        # ... (Tambahkan field lain sesuai kebutuhan Anda disini) ...
        # Saya singkat biar kodenya muat, silakan copas field lengkap dari kode sebelumnya jika perlu
        
        if st.form_submit_button("Lanjut"):
            st.session_state.page = "kuesioner"
            st.rerun()

# ==========================================
# SLIDE 3: KUESIONER
# ==========================================
elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    # ... (Logic kuesioner Anda tetap sama) ...
    if st.button("Mulai Tes Corsi"):
        st.session_state.page = "corsi_game"
        st.rerun()

# ==========================================
# SLIDE 4: GAME CORSI (FINAL FIX)
# ==========================================
elif st.session_state.page == "corsi_game":
    st.header(f"Level: {st.session_state.corsi_level - 1}")
    
    # Placeholder layar utama
    layar_utama = st.empty()

    if st.session_state.corsi_phase == "idle":
        with layar_utama.container():
            st.info(f"Hafalkan urutan {st.session_state.corsi_level} kotak!")
            # Tampilkan grid visual (HTML)
            st.markdown(get_html(None), unsafe_allow_html=True)
            if st.button("Mulai Level Ini", type="primary"):
                seq = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                st.session_state.corsi_sequence = seq
                st.session_state.corsi_user_input = []
                st.session_state.corsi_phase = "showing"
                st.rerun()

    elif st.session_state.corsi_phase == "showing":
        # Animasi Blink
        layar_utama.markdown(get_html(None), unsafe_allow_html=True)
        time.sleep(1)
        for item in st.session_state.corsi_sequence:
            layar_utama.markdown(get_html(highlight_idx=item), unsafe_allow_html=True)
            time.sleep(0.8)
            layar_utama.markdown(get_html(None), unsafe_allow_html=True)
            time.sleep(0.4)
        st.session_state.corsi_phase = "input"
        st.rerun()

    elif st.session_state.corsi_phase == "input":
        layar_utama.empty() # Bersihkan visual HTML
        st.success("Giliran Anda! Klik urutan tadi.")
        render_buttons() # Tampilkan tombol interaktif (Grid 4x4 HP Fix)

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
                st.session_state.corsi_score = st.session_state.corsi_level - 1
                st.session_state.corsi_level += 1
                st.session_state.corsi_lives = 1
                st.session_state.corsi_phase = "idle"
                st.rerun()

# ==========================================
# SLIDE 5: SAVING (Fix: Teks Loading Hilang)
# ==========================================
elif st.session_state.page == "saving":
    st.header("Penelitian Selesai")
    
    # Buat wadah khusus untuk status loading
    status_box = st.empty()
    status_box.info("Sedang menyimpan data Anda...")
    
    final_payload = st.session_state.user_data.copy()
    final_payload['skorCorsi'] = st.session_state.corsi_score
    
    with st.spinner('Menghubungi server...'):
        success = send_data_to_google_script(final_payload)
    
    if success:
        # HAPUS pesan "Sedang menyimpan..."
        status_box.empty()
        
        # Tampilkan pesan sukses
        st.success("Data berhasil disimpan!")
        st.markdown("### Terimakasih! Silakan tutup tab ini.")
        st.session_state.page = "done"
    else:
        status_box.error("Gagal menyimpan. Cek koneksi.")
        if st.button("Coba Lagi"): st.rerun()

elif st.session_state.page == "done":
    st.balloons()
    st.success("Selesai.")
