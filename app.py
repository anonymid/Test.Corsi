import streamlit as st
import requests
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="Penelitian Psikologi", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- INIT STATE ---
# State Halaman & User
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}

# State Corsi
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 2
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 1
if 'corsi_score' not in st.session_state: st.session_state.corsi_score = 0

# State IAT
if 'iat_phase' not in st.session_state: st.session_state.iat_phase = "instruction"
if 'iat_trials' not in st.session_state: st.session_state.iat_trials = []
if 'iat_current_index' not in st.session_state: st.session_state.iat_current_index = 0
if 'iat_start_time' not in st.session_state: st.session_state.iat_start_time = 0
if 'iat_results' not in st.session_state: st.session_state.iat_results = [] # Simpan [word, reaction_time, is_correct]

# --- DATA IAT (CONTOH SEDERHANA: INTERNET vs BUKAN) ---
# Kiri: INTERNET, Kanan: BUKAN INTERNET
IAT_WORDS = [
    {"word": "Wifi", "category": "internet"},
    {"word": "Buku", "category": "bukan"},
    {"word": "Online", "category": "internet"},
    {"word": "Taman", "category": "bukan"},
    {"word": "Medsos", "category": "internet"},
    {"word": "Olahraga", "category": "bukan"},
    {"word": "Streaming", "category": "internet"},
    {"word": "Tidur", "category": "bukan"}
]

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS GLOBAL (Corsi Pixel + IAT + Form) ---
st.markdown("""
<style>
    /* 1. SETUP LAYAR */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* ================= CORSI STYLES ================= */
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(4, auto) !important;
        justify-content: center !important;
        gap: 15px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }
    div[data-testid="column"] {
        width: auto !important;
        flex: 0 0 auto !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Tombol Corsi (Pixel Lock) */
    .corsi-btn button {
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        border: 2px solid #bbb;
        padding: 0 !important;
        margin: 0 !important;
    }
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
        .corsi-btn button { width: 60px !important; height: 60px !important; }
    }
    .corsi-btn button:active { background-color: #007bff; color: white; }

    /* ================= IAT STYLES ================= */
    .iat-container {
        display: flex;
        justify-content: space-between;
        margin-top: 30px;
    }
    .iat-word {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        margin: 40px 0;
        padding: 20px;
        border: 2px dashed #ccc;
        border-radius: 10px;
    }
    /* Tombol IAT Besar */
    .iat-btn button {
        width: 100% !important;
        height: 80px !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- FUNGSI CORSI (VISUAL) ---
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

# --- FUNGSI CORSI (TOMBOL) ---
def render_corsi_buttons():
    with st.container():
        for row in range(4):
            cols = st.columns(4) 
            for col in range(4):
                idx = row * 4 + col
                # Tambahkan class khusus 'corsi-btn' agar tidak bentrok dengan tombol lain
                cols[col].markdown('<div class="corsi-btn">', unsafe_allow_html=True)
                cols[col].button(" ", key=f"btn_{idx}", on_click=lambda i=idx: st.session_state.corsi_user_input.append(i))
                cols[col].markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PAGE 1: WELCOME
# ==========================================
if st.session_state.page == "welcome":
    st.title("Penelitian Psikologi")
    st.markdown("""
    Halo! Terima kasih sudah bersedia membantu penelitian ini.
    Anda akan melalui 3 tahapan singkat:
    1.  📝 **Isi Data Diri & Kuesioner**
    2.  ⚡ **Tes Reaksi (IAT)** - Sortir kata secepat mungkin.
    3.  🧠 **Tes Memori (Corsi)** - Hafalkan urutan lingkaran.
    
    **Reward:** E-Money bagi responden beruntung!
    """)
    if st.button("Saya Bersedia, Mulai!", type="primary"):
        st.session_state.page = "data_diri"
        st.rerun()

# ==========================================
# PAGE 2: DATA DIRI (LENGKAP)
# ==========================================
elif st.session_state.page == "data_diri":
    st.header("Data Diri")
    st.info("Mohon isi data dengan jujur.")
    
    with st.form("form_data"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial Nama")
        st.session_state.user_data['umur'] = st.selectbox("Umur", list(range(15, 40)))
        st.session_state.user_data['gender'] = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        st.session_state.user_data['status'] = st.selectbox("Status", ["Pelajar", "Mahasiswa", "Bekerja", "Lainnya"])
        st.session_state.user_data['domisili'] = st.text_input("Domisili")
        st.session_state.user_data['wa'] = st.text_input("Nomor Whatsapp (Untuk Reward)")
        
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
# PAGE 3: KUESIONER (18 SOAL)
# ==========================================
elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    st.write("Seberapa setuju anda dengan pernyataan berikut? (1=Sangat Tidak Setuju, 4=Sangat Setuju)")
    
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
    
    total_q_score = 0
    with st.form("form_kuesioner"):
        for i, q in enumerate(questions):
            st.write(f"**{i+1}. {q}**")
            val = st.radio(f"q{i}", [1, 2, 3, 4], key=f"kues_{i}", horizontal=True, label_visibility="collapsed")
            total_q_score += val
            st.divider()
            
        if st.form_submit_button("Lanjut ke Tes IAT"):
            st.session_state.user_data['skor_kuesioner'] = total_q_score
            st.session_state.page = "iat_intro"
            st.rerun()

# ==========================================
# PAGE 4: IAT (IMPLICIT ASSOCIATION TEST)
# ==========================================
elif st.session_state.page == "iat_intro":
    st.header("Tes Reaksi (IAT)")
    st.info("""
    **Instruksi:**
    1. Sebuah kata akan muncul di tengah.
    2. Tekan tombol **KIRI** jika kata berhubungan dengan **INTERNET**.
    3. Tekan tombol **KANAN** jika kata berhubungan dengan **BUKAN INTERNET**.
    4. Lakukan secepat mungkin!
    """)
    if st.button("Mulai IAT", type="primary"):
        # Persiapan Soal (Diacak)
        trials = IAT_WORDS * 2 # 16 Soal
        random.shuffle(trials)
        st.session_state.iat_trials = trials
        st.session_state.iat_current_index = 0
        st.session_state.iat_results = []
        st.session_state.page = "iat_test"
        # Set waktu mulai untuk soal pertama
        st.session_state.iat_start_time = time.time()
        st.rerun()

elif st.session_state.page == "iat_test":
    # Cek apakah soal sudah habis
    if st.session_state.iat_current_index >= len(st.session_state.iat_trials):
        st.session_state.page = "corsi_intro"
        st.rerun()
    
    current_word_obj = st.session_state.iat_trials[st.session_state.iat_current_index]
    word_text = current_word_obj['word']
    correct_cat = current_word_obj['category'] # 'internet' or 'bukan'

    st.markdown(f"<div class='iat-word'>{word_text}</div>", unsafe_allow_html=True)
    
    # Fungsi Callback saat tombol ditekan
    def submit_iat(choice):
        end_time = time.time()
        rt = round((end_time - st.session_state.iat_start_time) * 1000) # ms
        
        # Cek Jawaban
        is_correct = (choice == correct_cat)
        
        # Simpan Data
        st.session_state.iat_results.append({
            "word": word_text,
            "rt": rt,
            "correct": is_correct
        })
        
        # Lanjut Soal
        st.session_state.iat_current_index += 1
        st.session_state.iat_start_time = time.time() # Reset timer untuk soal berikutnya

    # Layout Tombol Kiri Kanan
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="iat-btn">', unsafe_allow_html=True)
        st.button("INTERNET (Kiri)", on_click=submit_iat, args=("internet",), use_container_width=True, key=f"iat_l_{st.session_state.iat_current_index}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="iat-btn">', unsafe_allow_html=True)
        st.button("BUKAN INTERNET (Kanan)", on_click=submit_iat, args=("bukan",), use_container_width=True, key=f"iat_r_{st.session_state.iat_current_index}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# PAGE 5: CORSI (MEMORI KERJA) - PIXEL FIX
# ==========================================
elif st.session_state.page == "corsi_intro":
    st.header("Tes Memori (Corsi)")
    st.success("Tes IAT Selesai! Sekarang tes terakhir.")
    st.info("Hafalkan urutan lingkaran biru yang muncul, lalu ulangi.")
    
    if st.button("Mulai Tes Memori", type="primary"):
        st.session_state.page = "corsi_game"
        st.session_state.corsi_phase = "idle"
        st.rerun()

elif st.session_state.page == "corsi_game":
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
                st.session_state.corsi_score = st.session_state.corsi_level - 1 # Simpan skor
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
    
    # Hitung Rata-rata RT IAT
    total_rt = sum([x['rt'] for x in st.session_state.iat_results])
    avg_rt = total_rt / len(st.session_state.iat_results) if st.session_state.iat_results else 0
    correct_iat = len([x for x in st.session_state.iat_results if x['correct']])
    
    # Susun Payload
    payload = st.session_state.user_data.copy()
    payload['skor_corsi'] = st.session_state.corsi_score
    payload['iat_avg_rt'] = avg_rt
    payload['iat_accuracy'] = correct_iat
    # Kita bisa kirim detail IAT jika perlu, tapi ini ringkasannya saja
    
    if send_data(payload):
        status.empty()
        st.success("Data Berhasil Disimpan!")
        st.balloons()
        st.markdown(f"""
        ### Terima Kasih!
        Skor Memori Anda: **{st.session_state.corsi_score}**
        Rata-rata Waktu Reaksi: **{avg_rt} ms**
        
        Kami akan menghubungi via WhatsApp jika Anda terpilih mendapatkan reward.
        """)
    else:
        status.error("Gagal koneksi internet.")
        if st.button("Coba Kirim Lagi"):
            st.rerun()
