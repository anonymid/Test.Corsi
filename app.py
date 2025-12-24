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
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 1
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 2 # 2 Nyawa
if 'corsi_score' not in st.session_state: st.session_state.corsi_score = 0

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS GLOBAL ---
st.markdown("""
<style>
    /* 1. SETUP LAYAR */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 2. RESET PADDING KOLOM */
    div[data-testid="column"] {
        width: auto !important;
        flex: 0 0 auto !important; 
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* CSS KHUSUS GAME CORSI */
    
    /* GRID 4 KOLOM */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4)) {
        display: grid !important;
        grid-template-columns: repeat(4, auto) !important;
        justify-content: center !important;
        gap: 15px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* TOMBOL JAWABAN (BULAT) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4)) button[kind="secondary"] {
        width: 80px !important;    
        height: 80px !important;
        border-radius: 50% !important; 
        border: 2px solid #bbb;
        padding: 0 !important;
        margin: 0 !important;
        line-height: 0 !important;
    }

    /* RESPONSIF HP */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4)) button[kind="secondary"] {
            width: 60px !important;
            height: 60px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4)) {
            gap: 10px !important;
        }
    }

    /* TOMBOL MULAI (KOTAK NORMAL - PRIMARY) */
    button[kind="primary"] {
        width: 100% !important;     
        height: auto !important;    
        aspect-ratio: unset !important;
        border-radius: 8px !important; 
        padding: 0.5rem 1rem !important;
        margin-top: 10px !important;
        line-height: 1.5 !important;
        white-space: normal !important;
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
# PAGE: WELCOME
# ==========================================
if st.session_state.page == "welcome":
    st.title("Penelitian Pengaruh Ketergantungan Internet terhadap Kinerja Memori Kerja")
    st.write("")
    st.markdown("""
    Terimakasih telah bersedia menjadi responden kami dalam penelitian ini, semua data yang anda masukkan akan kami gunakan untuk keperluan akademik dan akan kami jaga kerahasiaannya. Sebagai bentuk terimakasih, silahkan isi nomor whatsapp dengan benar, kami akan memberikan e-money kepada 5 orang yang terpilih sebegai bentuk apresiasi kami.
    """)
    
    bersedia = st.checkbox("Apakah anda bersedia menjadi responden?")
    
    if st.button("Lanjut", type="primary", disabled=not bersedia):
        st.session_state.page = "data_diri"
        st.rerun()

# ==========================================
# PAGE: DATA DIRI
# ==========================================
elif st.session_state.page == "data_diri":
    st.header("Data Responden")
    st.write("Mohon diisi dengan kondisi anda yang sebenarnya.")
    
    with st.form("form_data"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial")
        st.session_state.user_data['umur'] = st.selectbox("Umur", list(range(17, 29)))
        st.session_state.user_data['gender'] = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        st.session_state.user_data['status'] = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        st.session_state.user_data['domisili'] = st.text_input("Domisili")
        st.session_state.user_data['wa'] = st.text_input("Nomor Whatsapp")
        
        st.session_state.user_data['durasi_inet'] = st.selectbox("Durasi Penggunaan Internet Perhari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        st.session_state.user_data['tujuan_inet'] = st.selectbox("Tujuan Penggunaan Internet", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        
        st.session_state.user_data['aktivitas_dominan'] = st.selectbox(
            "Jenis Aktifitas Dominan", 
            [
                "Scrolling Pasif (Hanya Scrolling, Hanya melihat feed atau reels, tidak berkomentar)", 
                "Scrolling Aktif (Membuat Konten, Menulis komentar/komunikasi, Mencari informasi)"
            ]
        )
        
        st.session_state.user_data['gadget_tidur'] = st.selectbox("Menggunakan Gadget sebelum tidur?", ["Ya", "Tidak"])
        st.session_state.user_data['durasi_tidur'] = st.selectbox("Durasi Rata-rata tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        st.session_state.user_data['kualitas_tidur'] = st.selectbox("Kualitas tidur", ["Baik", "Sedang", "Buruk"])
        st.session_state.user_data['kafein'] = st.selectbox("Konsumsi Kafein", ["Tidak pernah", "1xsehari", "2xsehari", "3xsehari"])
        
        st.session_state.user_data['gangguan_neuro'] = st.selectbox(
            "Gangguan Neurologis", 
            ["Tidak Ada", "ADHD", "Autisme", "Parkinson", "Riwayat Kecelakaan Kepala", "Stroke", "Gangguan Perkembangan Syaraf", "Tumor Otak"]
        )
        
        st.session_state.user_data['gangguan_psiko'] = st.selectbox(
            "Gangguan Psikologis Diagnosis dari Psikolog/Psikiater", 
            ["Tidak ada", "Stress Psikologis", "Kecemasan", "Depresi Ringan-Sedang", "Kelelahan Mental"]
        )
        
        if st.form_submit_button("Lanjut"):
            if not st.session_state.user_data['inisial'] or not st.session_state.user_data['wa']:
                st.error("Mohon lengkapi Inisial dan Nomor Whatsapp.")
            else:
                st.session_state.page = "kuesioner"
                st.rerun()

# ==========================================
# PAGE: KUESIONER
# ==========================================
elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    st.markdown("""
    Silahkan pilih kondisi yang sesuai dengan anda.
    * 1 = Sangat Tidak Setuju
    * 2 = Tidak Setuju
    * 3 = Setuju
    * 4 = Sangat Setuju
    """)
    
    questions = [
        "Saya bermain internet lebih lama dari yang saya rencanakan.",
        "Saya membentuk pertemanan baru melalui internet.",
        "Saya merahasiakan aktivitas saya di internet dari orang lain.",
        "Saya menutupi pikiran yang mengganggu dengan memikirkan hal menyenangkan tentang internet.",
        "Saya takut hidup tanpa internet akan membosankan atau kosong.",
        "Saya marah jika ada yang mengganggu saat saya bermain internet.",
        "Saya terus memikirkan internet ketika tidak sedang bermain.",
        "Saya lebih memilih internet daripada beraktivitas dengan orang lain.",
        "Saya merasa gelisah jika tidak bermain internet, dan tenang kembali setelah bermain.",
        "Saya mengabaikan pekerjaan rumah demi bermain internet.",
        "Waktu belajar atau nilai akademik saya menurun akibat internet.",
        "Kinerja saya di sekolah/rumah terganggu karena internet.",
        "Saya sering kurang tidur karena bermain internet.",
        "Saya berusaha mengurangi waktu internet tetapi gagal.",
        "Saya sering berkata 'sebentar lagi' saat bermain internet.",
        "Saya berusaha menyembunyikan durasi bermain internet.",
        "Saya mengabaikan kegiatan penting demi internet.",
        "Saya merasa sulit berhenti ketika sedang bermain internet."
    ]
    
    responses = []
    with st.form("form_kuesioner"):
        for i, q in enumerate(questions):
            st.write(f"**{i+1}. {q}**")
            # Index None agar default kosong
            val = st.radio(f"q{i}", [1, 2, 3, 4], key=f"kues_{i}", horizontal=True, label_visibility="collapsed", index=None)
            responses.append(val)
            st.divider()
            
        submitted = st.form_submit_button("Mulai Tes")
        
        if submitted:
            if None in responses:
                st.error("Mohon isi semua pertanyaan sebelum melanjutkan.")
            else:
                # 1. SIMPAN DETAIL PER PERTANYAAN (Q1=.., Q2=..)
                for i, r in enumerate(responses):
                    st.session_state.user_data[f'soal_{i+1}'] = r
                
                # 2. SIMPAN JUGA TOTALNYA (Opsional, buat jaga-jaga)
                total_q_score = sum(responses)
                st.session_state.user_data['skor_kuesioner'] = total_q_score
                
                # LANJUT KE GAME
                st.session_state.page = "corsi_game"
                st.session_state.corsi_phase = "idle"
                # Reset State Game
                st.session_state.corsi_level = 1
                st.session_state.corsi_lives = 2
                st.session_state.corsi_score = 0
                st.rerun()

# ==========================================
# PAGE: CORSI GAME
# ==========================================
elif st.session_state.page == "corsi_game":
    st.header("Tes Corsi Block Tapping")
    st.write(f"Level: {st.session_state.corsi_level} / 9")
    
    layar = st.empty()

    # FASE 1: PERSIAPAN
    if st.session_state.corsi_phase == "idle":
        with layar.container():
            st.write("Perhatikan kolom di bawah ini, lalu ulangi bagian yang menyala pada kolom yang tersedia.")
            st.markdown(get_corsi_html(None), unsafe_allow_html=True)
            
            # Level 1 = 2 blink, dst
            seq_len = st.session_state.corsi_level + 1
            
            c1, c2, c3 = st.columns([1,4,1]) 
            with c2:
                if st.button("Mulai Level Ini", type="primary", use_container_width=True):
                    st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(seq_len)]
                    st.session_state.corsi_user_input = []
                    st.session_state.corsi_phase = "showing"
                    st.rerun()

    # FASE 2: SHOWING
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

    # FASE 3: INPUT
    elif st.session_state.corsi_phase == "input":
        layar.empty()
        st.write("Giliran Kamu!")
        render_corsi_buttons()

        if len(st.session_state.corsi_user_input) > 0:
            curr = len(st.session_state.corsi_user_input) - 1
            
            # JIKA SALAH
            if st.session_state.corsi_user_input[curr] != st.session_state.corsi_sequence[curr]:
                time.sleep(0.3) # Silent fail
                
                st.session_state.corsi_lives -= 1
                
                if st.session_state.corsi_lives > 0:
                    # Masih punya nyawa -> Ulangi Level yang sama
                    st.session_state.corsi_phase = "idle" 
                    st.rerun()
                else:
                    # Nyawa habis -> STOP
                    st.session_state.page = "saving"
                    st.rerun()
            
            # JIKA BENAR
            elif len(st.session_state.corsi_user_input) == len(st.session_state.corsi_sequence):
                time.sleep(0.2)
                st.session_state.corsi_score = st.session_state.corsi_level # Save score level
                
                if st.session_state.corsi_level >= 9:
                    st.session_state.page = "saving" # Tamat
                else:
                    st.session_state.corsi_level += 1
                    st.session_state.corsi_lives = 2 # Reset nyawa
                    st.session_state.corsi_phase = "idle"
                st.rerun()

# ==========================================
# PAGE: PENUTUP (AUTO SAVE)
# ==========================================
elif st.session_state.page == "saving":
    st.header("Penutup")
    status = st.empty()
    status.info("Menyimpan data...")
    
    payload = st.session_state.user_data.copy()
    payload['skor_corsi'] = st.session_state.corsi_score
    
    if send_data(payload):
        status.empty()
        st.success("Terimakasih telah menjadi bagian dari penelitian kami, jawaban anda telah tersimpan secara otomatis.")
        st.balloons()
    else:
        status.error("Gagal menyimpan data karena koneksi internet.")
        if st.button("Coba Simpan Lagi"):
            st.rerun()
