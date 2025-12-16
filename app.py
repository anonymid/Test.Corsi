import streamlit as st
import requests
import time
import random

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Penelitian Memori Kerja", layout="centered")

# --- URL GOOGLE SCRIPT ANDA ---
# Pastikan URL ini sesuai dengan yang Anda berikan
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- INISIALISASI SESSION STATE (Variable Global) ---
if 'page' not in st.session_state:
    st.session_state.page = "welcome"
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
# State untuk Corsi
if 'corsi_level' not in st.session_state:
    st.session_state.corsi_level = 2  # Mulai dari 2 kotak
if 'corsi_sequence' not in st.session_state:
    st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state:
    st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state:
    st.session_state.corsi_phase = "idle" # idle, showing, input
if 'corsi_lives' not in st.session_state:
    st.session_state.corsi_lives = 1 # Kesempatan salah 1x (total 2 nyawa per level biasanya, tapi kita set 1 retry)
if 'corsi_score' not in st.session_state:
    st.session_state.corsi_score = 0

# --- FUNGSI KIRIM DATA KE GOOGLE SHEET ---
def send_data_to_google_script(final_data):
    try:
        # Mengirim data sebagai JSON
        response = requests.post(GOOGLE_SCRIPT_URL, json=final_data)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")
        return False

# ==========================================
# SLIDE 1: WELCOME SCREEN
# ==========================================
if st.session_state.page == "welcome":
    st.title("Penelitian Pengaruh Ketergantungan Internet terhadap Kinerja Memori Kerja")
    st.markdown("""
    Terimakasih telah bersedia menjadi responden kami dalam penelitian ini. Semua data yang Anda masukkan 
    akan kami gunakan untuk keperluan akademik dan dijaga kerahasiaannya.
    
    Sebagai bentuk apresiasi, kami akan memberikan **e-money kepada 5 orang terpilih**.
    """)
    
    consent = st.checkbox("Apakah Anda bersedia menjadi responden?")
    
    if st.button("Lanjut", disabled=not consent):
        st.session_state.page = "data_diri"
        st.rerun()

# ==========================================
# SLIDE 2: DATA RESPONDEN
# ==========================================
elif st.session_state.page == "data_diri":
    st.header("Data Responden")
    st.info("Mohon diisi dengan kondisi sebenarnya.")
    
    with st.form("form_data_diri"):
        inisial = st.text_input("Inisial Nama")
        umur = st.selectbox("Umur", list(range(17, 29)))
        gender = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        status = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        wa = st.text_input("Nomor Whatsapp (Untuk E-Money)")
        
        st.subheader("Kebiasaan Digital")
        durasi = st.selectbox("Durasi Penggunaan Internet Perhari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        tujuan = st.selectbox("Tujuan Penggunaan Internet", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        aktivitas = st.selectbox("Jenis Aktifitas Dominan", [
            "Scrolling Pasif (Hanya melihat, tidak komen)", 
            "Scrolling Aktif (Membuat konten, komen, cari info)"
        ])
        gadget = st.radio("Menggunakan Gadget sebelum tidur?", ["Ya", "Tidak"])
        
        st.subheader("Kesehatan")
        durasi_tidur = st.selectbox("Durasi Rata-rata tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        kualitas_tidur = st.selectbox("Kualitas tidur", ["Baik", "Sedang", "Buruk"])
        kafein = st.selectbox("Konsumsi Kafein", ["Tidak pernah", "1xsehari", "2xsehari", "3xsehari"])
        neuro = st.selectbox("Gangguan Neurologis", ["Tidak Ada", "ADHD", "Autisme", "Parkinson", "Riwayat Kecelakaan Kepala", "Stroke", "Lainnya"])
        psiko = st.selectbox("Gangguan Psikologis (Diagnosis)", ["Tidak ada", "Stress Psikologis", "Kecemasan", "Depresi Ringan-Sedang", "Kelelahan Mental"])

        submit = st.form_submit_button("Lanjut ke Kuesioner")
        
        if submit:
            if not inisial or not wa:
                st.error("Mohon lengkapi Inisial dan Nomor Whatsapp.")
            else:
                # Simpan data sementara
                st.session_state.user_data.update({
                    "inisial": inisial, "umur": umur, "gender": gender, "status": status,
                    "domisili": domisili, "wa": wa, "durasi": durasi, "tujuan": tujuan,
                    "aktivitas": aktivitas, "gadget": gadget, "tidur": durasi_tidur,
                    "kualitas": kualitas_tidur, "kafein": kafein, "neuro": neuro, "psiko": psiko
                })
                st.session_state.page = "kuesioner"
                st.rerun()

# ==========================================
# SLIDE 3: KUESIONER (LIKERT SCALE)
# ==========================================
elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    st.write("Silakan pilih kondisi yang sesuai. (1=Sangat Tidak Setuju, 4=Sangat Setuju)")
    
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
    
    # Dictionary untuk menyimpan jawaban kuesioner
    q_answers = {}
    
    with st.form("form_kuesioner"):
        total_score_kuesioner = 0
        for i, q in enumerate(questions):
            st.write(f"**{i+1}. {q}**")
            val = st.radio(f"Jawaban No {i+1}", [1, 2, 3, 4], index=None, horizontal=True, key=f"q{i}")
            if val:
                total_score_kuesioner += val
        
        st.write("---")
        submit_kuesioner = st.form_submit_button("Mulai Tes Memori (Corsi)")
        
        if submit_kuesioner:
            # Validasi apakah semua terisi? (Optional, disini kita anggap user mengisi)
            st.session_state.user_data['skorKuesioner'] = total_score_kuesioner
            st.session_state.page = "corsi_intro"
            st.rerun()

# ==========================================
# SLIDE 4: INTRO CORSI
# ==========================================
elif st.session_state.page == "corsi_intro":
    st.header("Tes Corsi Block Tapping")
    st.markdown("""
    **Instruksi:**
    1. Anda akan melihat kotak-kotak berkedip secara berurutan berwarna **Biru**.
    2. Hafalkan urutannya.
    3. Setelah selesai berkedip, **klik kotak** sesuai urutan yang Anda lihat.
    4. Tingkat kesulitan akan bertambah terus menerus.
    """)
    if st.button("Mulai Tes"):
        st.session_state.page = "corsi_game"
        st.session_state.corsi_phase = "idle"
        st.rerun()

# ==========================================
# SLIDE 5: GAME CORSI (CORE LOGIC)
# ==========================================
elif st.session_state.page == "corsi_game":
    st.header(f"Level: {st.session_state.corsi_level - 1}")
    
    # --- Container untuk Grid ---
    grid_container = st.container()

    # --- LOGIKA TOMBOL GRID ---
    def make_grid(disabled=True, highlight_idx=None):
        """Fungsi untuk menampilkan Grid 4x4"""
        with grid_container:
            # CSS untuk membuat kotak rapi
            st.markdown("""
            <style>
            div.stButton > button:first-child {
                height: 60px;
                width: 100%;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Grid 4x4 (0-15)
            for row in range(4):
                cols = st.columns(4)
                for col in range(4):
                    idx = row * 4 + col
                    
                    # Tentukan warna tombol (Biru jika highlight, Putih biasa)
                    if idx == highlight_idx:
                        # Streamlit tidak bisa ubah warna tombol native secara dinamis dengan mudah,
                        # kita pakai trick emoji atau text jika highlight
                        label = "🟦" 
                    else:
                        label = "⬜"

                    # Callback saat tombol diklik (hanya aktif saat fase input)
                    def on_click(clicked_idx=idx):
                        st.session_state.corsi_user_input.append(clicked_idx)
                    
                    # Render Tombol
                    cols[col].button(
                        label, 
                        key=f"btn_{idx}_{time.time()}", # Key unik agar tidak crash refresh
                        disabled=disabled,
                        on_click=on_click if not disabled else None,
                        use_container_width=True
                    )

    # --- FASE 1: IDLE / GENERATE SEQUENCE ---
    if st.session_state.corsi_phase == "idle":
        st.info("Klik tombol 'Mulai Level Ini' untuk melihat urutan.")
        if st.button("Mulai Level Ini"):
            # Generate urutan acak
            seq = [random.randint(0, 15) for _ in range(st.session_state.corsi_level)]
            st.session_state.corsi_sequence = seq
            st.session_state.corsi_user_input = []
            st.session_state.corsi_phase = "showing"
            st.rerun()

    # --- FASE 2: SHOWING SEQUENCE (ANIMASI) ---
    elif st.session_state.corsi_phase == "showing":
        # Placeholder agar tidak menumpuk UI
        placeholder = st.empty()
        
        with placeholder.container():
            st.warning("Perhatikan urutan...")
            # Tampilkan tombol mati dulu
            make_grid(disabled=True)
            
        time.sleep(1)
        
        # Loop sequence untuk animasi
        for item in st.session_state.corsi_sequence:
            with placeholder.container():
                # Tampilkan kotak yang menyala (Highlight)
                st.warning(f"Perhatikan...")
                make_grid(disabled=True, highlight_idx=item)
            time.sleep(0.7) # Waktu nyala
            
            with placeholder.container():
                # Tampilkan kosong (jeda antar kedipan)
                st.warning(f"Perhatikan...")
                make_grid(disabled=True, highlight_idx=None)
            time.sleep(0.3) # Jeda
            
        # Pindah ke fase Input
        st.session_state.corsi_phase = "input"
        st.rerun()

    # --- FASE 3: INPUT USER ---
    elif st.session_state.corsi_phase == "input":
        st.success("Ulangi urutan tadi!")
        
        # Tampilkan Grid Aktif (Bisa diklik)
        make_grid(disabled=False)
        
        # Cek Jawaban secara Real-time
        if len(st.session_state.corsi_user_input) > 0:
            current_step = len(st.session_state.corsi_user_input) - 1
            
            # Cek apakah klik terakhir benar?
            if st.session_state.corsi_user_input[current_step] != st.session_state.corsi_sequence[current_step]:
                # SALAH KLIK
                st.error("Salah urutan!")
                time.sleep(1)
                
                if st.session_state.corsi_lives > 0:
                    # Masih ada nyawa, ulang level yang sama
                    st.session_state.corsi_lives -= 1
                    st.toast("Gagal! Anda punya 1 kesempatan lagi di level ini.", icon="⚠️")
                    st.session_state.corsi_phase = "idle"
                    st.session_state.corsi_user_input = []
                    time.sleep(1)
                    st.rerun()
                else:
                    # Game Over
                    st.session_state.page = "saving"
                    st.rerun()
            
            # Jika Benar dan sudah lengkap
            elif len(st.session_state.corsi_user_input) == len(st.session_state.corsi_sequence):
                st.balloons()
                st.success("Benar! Lanjut level berikutnya.")
                time.sleep(1)
                
                # Naik Level
                st.session_state.corsi_score = st.session_state.corsi_level - 1 # Skor = Level terakhir sukses
                st.session_state.corsi_level += 1
                st.session_state.corsi_lives = 1 # Reset nyawa di level baru
                st.session_state.corsi_phase = "idle"
                st.rerun()

# ==========================================
# SLIDE 6: SIMPAN DATA & TERIMAKASIH
# ==========================================
elif st.session_state.page == "saving":
    st.header("Penelitian Selesai")
    st.write("Sedang menyimpan data Anda...")
    
    # Gabungkan semua data
    final_payload = st.session_state.user_data.copy()
    final_payload['skorCorsi'] = st.session_state.corsi_score
    
    # Debug: Print data (bisa dihapus nanti)
    # st.json(final_payload)
    
    # Kirim ke Google Script
    with st.spinner('Mengirim data ke server...'):
        success = send_data_to_google_script(final_payload)
    
    if success:
        st.success("Data berhasil disimpan!")
        st.markdown("""
        ### Terimakasih!
        Jawaban Anda telah kami terima. Kami akan menghubungi nomor Whatsapp Anda 
        jika Anda terpilih mendapatkan e-money.
        
        Silakan tutup tab browser ini.
        """)
        st.session_state.page = "done" # Stop loop
    else:
        st.error("Gagal menyimpan data. Mohon periksa koneksi internet Anda.")
        if st.button("Coba Kirim Lagi"):
            st.rerun()

elif st.session_state.page == "done":
    st.success("Data Tersimpan. Terimakasih.")
