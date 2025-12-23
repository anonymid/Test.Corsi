import streamlit as st
import requests
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="Penelitian Psikologi", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- INIT STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}

# State Corsi
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1
if 'corsi_score' not in st.session_state: st.session_state.corsi_score = 0

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS GLOBAL (HANYA LAYOUT DASAR, TIDAK MERUSAK TOMBOL LAIN) ---
st.markdown("""
<style>
    /* 1. SETUP LAYAR */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* 2. RESET PADDING KOLOM BIAR RAPI */
    div[data-testid="column"] {
        width: auto !important;
        flex: 0 0 auto !important; 
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CSS KHUSUS GAME (Hanya dipanggil saat main game) ---
def inject_game_css():
    st.markdown("""
    <style>
        /* INI HANYA BERLAKU SAAT GAME BERJALAN */
        
        /* 1. GRID SYSTEM: DITENGAHKAN */
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: repeat(4, auto) !important;
            justify-content: center !important;
            gap: 15px !important;
            margin: 0 auto !important;
            width: 100% !important;
        }

        /* 2. TOMBOL BULAT (FIX PIXEL) */
        div.stButton > button {
            width: 80px !important;    /* Default PC */
            height: 80px !important;
            border-radius: 50% !important; /* LINGKARAN */
            border: 2px solid #bbb;
            padding: 0 !important;
            margin: 0 !important;
            line-height: 0 !important;
        }

        /* 3. UKURAN HP */
        @media (max-width: 600px) {
            div.stButton > button {
                width: 60px !important;
                height: 60px !important;
            }
            div[data-testid="stHorizontalBlock"] {
                gap: 10px !important;
            }
        }
        
        div.stButton > button:active { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI VISUAL CORSI ---
def get_corsi_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        boxes += f'<div class="bola" style="background-color:{color}; border-radius:50%; border:2px solid #999;"></div>'
    
    return f"""
    <div style="display:flex; justify-content:center; margin-bottom:20px;">
        <style>
            .grid-soal {{ display: grid; grid-template-columns: repeat(4, auto); gap: 15px; justify-content: center; }}
            .bola {{ width: 80px; height: 80px; }}
            @media (max-width: 600px) {{
                .grid-soal {{ gap: 10px; }}
                .bola {{ width: 60px; height: 60px; }}
            }}
        </style>
        <div class="grid-soal">{boxes}</div>
    </div>
    """

def render_corsi_buttons():
    with st.container():
        for row in range(4):
            cols = st.columns(4) 
            for col in range(4):
                idx = row * 4 + col
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i))

# ==========================================
# PAGE 1: WELCOME
# ==========================================
if st.session_state.page == "welcome":
    st.title("Penelitian Psikologi")
    st.markdown("""
    Halo! Terima kasih sudah bersedia membantu penelitian ini.
    
    **Tahapan:**
    1.  📝 **Isi Data Diri**
    2.  📋 **Kuesioner Singkat**
    3.  🧠 **Tes Memori**
    """)
    # Tombol ini sekarang AMAN (Tidak akan jadi bulat aneh)
    if st.button("Saya Bersedia, Mulai!", type="primary"):
        st.session_state.page = "data_diri"
        st.rerun()

# ==========================================
# PAGE 2: DATA DIRI
# ==========================================
elif st.session_state.page == "data_diri":
    st.header("Data Diri")
    
    with st.form("form_data"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial Nama")
        st.session_state.user_data['umur'] = st.selectbox("Umur", list(range(15, 40)))
        st.session_state.user_data['gender'] = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        st.session_state.user_data['status'] = st.selectbox("Status", ["Pelajar", "Mahasiswa", "Bekerja", "Lainnya"])
        st.session_state.user_data['domisili'] = st.text_input("Domisili")
        st.session_state.user_data['wa'] = st.text_input("Nomor Whatsapp")
        
        st.markdown("---")
        st.write("**Kebiasaan Digital**")
        st.session_state.user_data['durasi_inet'] = st.selectbox("Durasi Internet/Hari", ["< 1 jam", "1-3 jam", "3-5 jam", "5-7 jam", "> 7 jam"])
        st.session_state.user_data['tujuan_inet'] = st.multiselect("Tujuan Utama", ["Medsos", "Game", "Kerja/Belajar", "Streaming", "Belanja"])
        st.session_state.user_data['tidur'] = st.selectbox("Rata-rata Tidur", ["< 5 jam", "5-6 jam", "7-8 jam", "> 8 jam"])
        
        if st.form_submit_button("Lanjut ke Kuesioner"):
            if not st.session_state.user_data['inisial'] or not st.session_state.user_data['wa']:
                st.error("Nama dan WA wajib diisi.")
            else:
                st.session_state.page = "kuesioner"
                st.rerun()

# ==========================================
# PAGE 3: KUESIONER (FIXED)
# ==========================================
elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    st.write("Mohon isi sesuai kondisi sebenarnya. (1=Sangat Tidak Setuju, 4=Sangat Setuju)")
    
    questions = [
        "Saya bermain internet lebih lama dari yang saya rencanakan.",
        "Saya membentuk pertemanan baru melalui internet.",
        "Saya merahasiakan aktivitas saya di internet dari orang lain.",
        "Saya menutupi pikiran yang mengganggu dengan internet.",
        "Saya takut hidup tanpa internet akan membosankan.",
        "Saya marah jika ada yang mengganggu saat saya online.",
        "Saya terus memikirkan internet ketika offline.",
        "Saya lebih memilih internet daripada beraktivitas dengan orang lain.",
        "Saya merasa gelisah jika tidak main internet, dan tenang setelah main.",
        "Saya mengabaikan pekerjaan rumah demi internet.",
        "Nilai atau kinerja saya menurun akibat internet.",
        "Kinerja saya terganggu karena internet.",
        "Saya sering kurang tidur karena bermain internet.",
        "Saya berusaha mengurangi waktu internet tetapi gagal.",
        "Saya sering berkata 'sebentar lagi' saat bermain internet.",
        "Saya berusaha menyembunyikan durasi bermain internet.",
        "Saya mengabaikan kegiatan sosial demi internet.",
        "Saya merasa sulit berhenti ketika sedang online."
    ]
    
    responses = []
    with st.form("form_kuesioner"):
        for i, q in enumerate(questions):
            st.write(f"**{i+1}. {q}**")
            # FIX: index=None agar defaultnya kosong
            val = st.radio(f"q{i}", [1, 2, 3, 4], key=f"kues_{i}", horizontal=True, label_visibility="collapsed", index=None)
            responses.append(val)
            st.divider()
            
        submitted = st.form_submit_button("Lanjut ke Tes Memori")
        
        if submitted:
            # Validasi: Cek apakah ada yang None (belum diisi)
            if None in responses:
                st.error("Mohon isi semua pertanyaan kuesioner sebelum lanjut.")
            else:
                total_q_score = sum(responses)
                st.session_state.user_data['skor_kuesioner'] = total_q_score
                st.session_state.page = "corsi_intro"
                st.rerun()

# ==========================================
# PAGE 4: CORSI INTRO
# ==========================================
elif st.session_state.page == "corsi_intro":
    st.header("Tes Memori (Corsi)")
    st.info("Hafalkan urutan lingkaran biru yang muncul.")
    
    if st.button("Mulai Tes Memori", type="primary"):
        st.session_state.page = "corsi_game"
        st.session_state.corsi_phase = "idle"
        st.rerun()

# ==========================================
# PAGE 5: CORSI GAME (CSS Tombol Bulat Aktif Disini)
# ==========================================
elif st.session_state.page == "corsi_game":
    # AKTIFKAN CSS KHUSUS GAME DI SINI
    inject_game_css()
    
    st.markdown(f"<h4 style='text-align:center'>Level: {st.session_state.corsi_level - 1}</h4>", unsafe_allow_html=True)
    layar = st.empty()

    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.write("Perhatikan urutan!")
            st.markdown(get_corsi_html(None), unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                if st.button("Mulai Level Ini", type="primary", use_container_width=True):
                    st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
                    st.session_state.corsi_user_input = []
                    st.session_state.corsi_phase = "showing"
                    st.rerun()

    elif st.session_state.corsi_phase == "showing":
        layar.markdown(get_corsi_html(None), unsafe_allow_html=True)
        time.sleep(0.5)
        for item in st.session_state.corsi_sequence:
            layar.markdown(get_corsi_html(item), unsafe_allow_html=True)
            time.sleep(0.8)
            layar.markdown(get_corsi_html(None), unsafe_allow_html=True)
            time.sleep(0.3)
        st.session_state.corsi_phase = "input"
        st.rerun()

    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.caption("Giliran Anda!")
        render_corsi_buttons()

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
# PAGE 6: SAVING
# ==========================================
elif st.session_state.page == "saving":
    st.header("Selesai")
    status = st.empty()
    status.info("Sedang menyimpan data...")
    
    payload = st.session_state.user_data.copy()
    payload['skor_corsi'] = st.session_state.corsi_score
    
    if send_data(payload):
        status.empty()
        st.success("Data Berhasil Disimpan!")
        st.balloons()
        st.markdown(f"""
        ### Terima Kasih!
        Skor Memori Anda: **{st.session_state.corsi_score}**
        """)
    else:
        status.error("Gagal koneksi internet.")
        if st.button("Coba Kirim Lagi"):
            st.rerun()
