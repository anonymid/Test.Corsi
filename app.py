import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import requests # <--- Kita pakai ini sekarang
import json

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studi Responden", page_icon="🧠")

# --- CSS CUSTOM (Agar tampilan Corsi 4x4 rapi di HP & Desktop) ---
st.markdown("""
<style>
    [data-testid="column"] { padding: 0 !important; margin: 0 !important; }
    .stButton button {
        width: 100% !important;
        aspect-ratio: 1/1 !important;
        border-radius: 0px !important;
        border: 0.5px solid #ddd !important;
        box-shadow: none !important; /* Hapus bayangan */
        margin: 0 !important;
    }
    /* Tombol Biru saat Blink */
    button[kind="primary"] {
        background-color: blue !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI GOOGLE SHEETS (Placeholder) ---
# --- FUNGSI SIMPAN KE GOOGLE SHEET (VIA APPS SCRIPT) ---
def save_to_google_sheets(data):
    # Ganti URL ini dengan URL panjang yang tadi kamu Copy dari Google Apps Script
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"
    
    try:
        response = requests.post(SCRIPT_URL, json=data)
        if response.status_code == 200:
            st.success("✅ Data berhasil disimpan ke server!")
        else:
            st.error("Gagal menyimpan data (Server Error).")
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi: {e}")

# --- INISIALISASI STATE ---
if 'sudah_simpan' not in st.session_state:
    st.session_state.sudah_simpan = False
    
if 'step' not in st.session_state:
    st.session_state.update({
        'step': 0, # 0: Welcome, 1: Data Diri, 2: Kuesioner, 3: Corsi Intro, 4: Corsi Game, 5: Finish
        'data_diri': {},
        'skor_kuesioner': 0,
        'corsi': {
            'level': 1,
            'sequence': [],
            'user_input': [],
            'playing_sequence': False,
            'lives': 2, # Kesempatan salah (jika salah 1x ulang, salah lagi game over)
            'score': 0,
            'max_level': 0,
            'status_msg': "Siap mulai?"
        }
    })

# --- HALAMAN 0: WELCOME SCREEN ---
if st.session_state.step == 0:
    st.title("Selamat Datang")
    st.write("""
    Terimakasih telah bersedia menjadi responden kami dalam penelitian ini, semua data yang anda masukkan 
    akan kami gunakan untuk keperluan akademik dan akan kami jaga kerahasiaannya. 
    Sebagai bentuk terimakasih, silahkan isi nomor whatsapp dengan benar, 
    kami akan memberikan e-money kepada 5 orang yang terpilih sebagai bentuk apresiasi kami.
    """)
    
    bersedia = st.checkbox("Apakah anda bersedia menjadi responden?")
    
    if bersedia:
        if st.button("Lanjut"):
            st.session_state.step = 1
            st.rerun()

# --- HALAMAN 1: DATA RESPONDEN ---
elif st.session_state.step == 1:
    st.header("Data Responden")
    st.caption("Mohon diisi dengan kondisi anda yang sebenarnya.")

    with st.form("form_data_diri"):
        inisial = st.text_input("Inisial")
        umur = st.selectbox("Umur", ["17 - 28", "< 17", "> 28"])
        jk = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        pekerjaan = st.selectbox("Status Pekerjaan", ["SMA/SMK", "Mahasiswa", "Pekerja"])
        domisili = st.text_input("Domisili")
        wa = st.text_input("Nomor Whatsapp")
        durasi_internet = st.selectbox("Durasi Penggunaan Internet Perhari", ["1-3 jam", "4-7 jam", "> 7 jam"])
        tujuan = st.selectbox("Tujuan Penggunaan Internet", ["Media Sosial", "Menonton Film", "Game Online", "Belajar/Bekerja"])
        aktivitas = st.selectbox("Jenis Aktifitas Dominan", [
            "Scrolling Pasif (Hanya Scrolling, melihat feed/reels, tidak komen)",
            "Scrolling Aktif (Membuat Konten, Komentar, Mencari info)"
        ])
        gadget_tidur = st.radio("Menggunakan Gadget sebelum tidur?", ["Ya", "Tidak"])
        durasi_tidur = st.selectbox("Durasi Rata-rata tidur", ["< 5 jam", "6 jam", "7 jam", "> 8 jam"])
        kualitas_tidur = st.selectbox("Kualitas tidur", ["Baik", "Sedang", "Buruk"])
        kafein = st.selectbox("Konsumsi Kafein", ["Tidak pernah", "1x sehari", "2x sehari", "3x sehari"])
        neurologis = st.selectbox("Gangguan Neurologis", [
            "Tidak Ada", "ADHD", "Autisme", "Parkinson", "Riwayat Kecelakaan Kepala", 
            "Stroke", "Gangguan Perkembangan Syaraf", "Tumor Otak"
        ])
        psikologis = st.selectbox("Gangguan Psikologis (Diagnosis)", [
            "Tidak ada", "Stress Psikologis", "Kecemasan", "Depresi Ringan-Sedang", "Kelelahan Mental"
        ])

        submit_bio = st.form_submit_button("Next")
        
        if submit_bio:
            if not inisial or not wa:
                st.error("Mohon lengkapi Inisial dan Nomor Whatsapp.")
            else:
                st.session_state.data_diri = {
                    "Inisial": inisial, "Umur": umur, "JK": jk, "Pekerjaan": pekerjaan,
                    "Domisili": domisili, "WA": wa, "Durasi_Inet": durasi_internet,
                    "Tujuan": tujuan, "Aktivitas": aktivitas, "Gadget_Tidur": gadget_tidur,
                    "Durasi_Tidur": durasi_tidur, "Kualitas_Tidur": kualitas_tidur,
                    "Kafein": kafein, "Neuro": neurologis, "Psiko": psikologis
                }
                st.session_state.step = 2
                st.rerun()

# --- HALAMAN 2: KUESIONER ---
elif st.session_state.step == 2:
    st.header("Kuesioner")
    st.write("Silahkan pilih kondisi yang sesuai. (1=Sangat Tidak Setuju, 4=Sangat Setuju)")
    
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
    
    responses = {}
    with st.form("kuesioner_form"):
        for i, q in enumerate(questions):
            responses[f"q{i+1}"] = st.radio(f"{i+1}. {q}", [1, 2, 3, 4], horizontal=True, index=None)
        
        submit_kuesioner = st.form_submit_button("Mulai Tes Corsi")
        
        if submit_kuesioner:
            # Cek apakah semua terisi
            if any(v is None for v in responses.values()):
                st.error("Mohon isi semua pertanyaan kuesioner.")
            else:
                total_score = sum(responses.values())
                st.session_state.skor_kuesioner = total_score
                st.session_state.step = 3
                st.rerun()

# --- HALAMAN 3: INTRO CORSI ---
elif st.session_state.step == 3:
    st.header("Tes Corsi Block Tapping")
    st.info("Perhatikan kotak yang menyala biru, lalu ulangi urutannya dengan mengklik kotak tersebut.")
    st.write(f"Level awal: 2 Kedipan. Total 9 Level.")
    
    if st.button("MULAI GAME"):
        st.session_state.step = 4
        # Setup Level 1
        st.session_state.corsi['level'] = 1
        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(2)] # Mulai 2 blink
        st.session_state.corsi['user_input'] = []
        st.session_state.corsi['playing_sequence'] = True
        st.rerun()

# --- HALAMAN 4: CORSI GAME ---
elif st.session_state.step == 4:
    st.header(f"Level {st.session_state.corsi['level']} / 9")
    
    # 1. LOGIKA MENAMPILKAN URUTAN (BLINK)
    if st.session_state.corsi['playing_sequence']:
        placeholder = st.empty()
        seq = st.session_state.corsi['sequence']
        
        # Tampilkan grid kosong sebentar sebelum mulai
        with placeholder.container():
            st.warning("Perhatikan urutan...")
            cols = st.columns(4)
            for i in range(16):
                cols[i%4].button("", key=f"init_{i}", disabled=True)
            time.sleep(1)

        # Proses kedipan biru
        for target_idx in seq:
            with placeholder.container():
                st.warning("Perhatikan...")
                cols = st.columns(4)
                for i in range(16):
                    if i == target_idx:
                        cols[i%4].button("", key=f"blink_{i}_{time.time()}", type="primary")
                    else:
                        cols[i%4].button("", key=f"bg_{i}_{time.time()}")
            time.sleep(0.8)
            
            # Jeda antar kedipan (mati sebentar)
            with placeholder.container():
                st.warning("Perhatikan...")
                cols = st.columns(4)
                for i in range(16):
                    cols[i%4].button("", key=f"off_{i}_{time.time()}")
            time.sleep(0.3)
            
        st.session_state.corsi['playing_sequence'] = False
        st.rerun()

    # 2. LOGIKA MENERIMA INPUT USER (SETELAH BLINK SELESAI)
    else:
        st.success("Giliran Anda! Ulangi urutannya.")
        
        cols = st.columns(4)
        for i in range(16):
            if cols[i%4].button("", key=f"user_{i}"):
                # Catat input user
                st.session_state.corsi['user_input'].append(i)
                
                # Cek apakah klik user benar
                idx_skrg = len(st.session_state.corsi['user_input']) - 1
                benar = st.session_state.corsi['sequence'][idx_skrg]
                
                if i != benar:
                    # JIKA SALAH
                    st.session_state.corsi['lives'] -= 1
                    if st.session_state.corsi['lives'] > 0:
                        st.error("Salah! Mengulang level ini...")
                        time.sleep(1)
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.rerun()
                    else:
                        # Gagal total (sudah salah 2x)
                        st.session_state.step = 5
                        st.rerun()
                
                elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                    # JIKA BENAR SEMUA DALAM SATU LEVEL
                    st.session_state.corsi['score'] = st.session_state.corsi['level']
                    
                    if st.session_state.corsi['level'] < 9:
                        st.session_state.corsi['level'] += 1
                        # Panjang urutan bertambah
                        new_len = st.session_state.corsi['level'] + 1 
                        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(new_len)]
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.session_state.corsi['lives'] = 2 
                        st.rerun()
                    else:
                        # Selesai level 9
                        st.session_state.step = 5
                        st.rerun()

    # Logic Input User (Setelah kedipan selesai)
else:
        st.success("Giliran Anda! Ulangi urutannya.")
        
        cols = st.columns(4)
        for i in range(16):
            if cols[i%4].button("", key=f"user_{i}"):
                # Catat klik user
                st.session_state.corsi['user_input'].append(i)
                
                # Cek apakah klik user benar
                idx_skrg = len(st.session_state.corsi['user_input']) - 1
                benar = st.session_state.corsi['sequence'][idx_skrg]
                
                # --- PERHATIKAN SEJAJARNYA IF DAN ELSE DI BAWAH INI ---
                if i != benar:
                    st.session_state.corsi['lives'] -= 1
                    if st.session_state.corsi['lives'] > 0:
                        st.error("Salah! Mengulang level ini...")
                        time.sleep(1)
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.rerun()
                    else:
                        st.session_state.step = 5
                        st.rerun()
                
                elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                    st.session_state.corsi['score'] = st.session_state.corsi['level']
                    
                    if st.session_state.corsi['level'] < 9:
                        st.session_state.corsi['level'] += 1
                        new_len = st.session_state.corsi['level'] + 1 
                        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(new_len)]
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.session_state.corsi['lives'] = 2 
                        st.rerun()
                    else:
                        st.session_state.step = 5
                        st.rerun()
                
                # JIKA BENAR DAN SUDAH SEMUA
                elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                    st.session_state.corsi['score'] = st.session_state.corsi['level']
                    if st.session_state.corsi['level'] < 9:
                        st.session_state.corsi['level'] += 1
                        # Panjang urutan = level + 1 (Level 1: 2 blink, dst)
                        new_len = st.session_state.corsi['level'] + 1 
                        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(new_len)]
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.session_state.corsi['lives'] = 2 
                        st.rerun()
                    else:
                        st.session_state.step = 5 # Tamat
                        st.rerun()

    # Logic User Input
    else:
        st.success("Giliran Anda! Ulangi urutannya.")
        
        # Grid Input User
        cols = st.columns(4)
        for i in range(16):
            # Tombol interaktif
            if cols[i%4].button("⬜", key=f"btn_{i}"):
                # Blink Hijau Feedback (via toast/info karena rerun instan)
                st.toast(f"Anda memilih kotak {i+1}")
                st.session_state.corsi['user_input'].append(i)
                
                # Cek jawaban sementara
                current_step = len(st.session_state.corsi['user_input']) - 1
                correct_val = st.session_state.corsi['sequence'][current_step]
                
                if i != correct_val:
                    # SALAH
                    st.session_state.corsi['lives'] -= 1
                    
                    if st.session_state.corsi['lives'] > 0:
                        st.error("Salah! Mengulang level yang sama...")
                        time.sleep(1)
                        # Reset input, sequence tetap sama (atau bisa diacak ulang jika mau)
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.rerun()
                    else:
                        # GAME OVER (Salah 2x di level sama)
                        st.error("Game Selesai!")
                        st.session_state.step = 5 # Ke Finish
                        st.rerun()
                
                elif len(st.session_state.corsi['user_input']) == len(st.session_state.corsi['sequence']):
                    # BENAR & SELESAI SATU LEVEL
                    st.session_state.corsi['score'] = st.session_state.corsi['level'] # Update max score
                    
                    if st.session_state.corsi['level'] < 9:
                        st.success("Benar! Lanjut Level Berikutnya...")
                        time.sleep(0.5)
                        st.session_state.corsi['level'] += 1
                        # Tambah tingkat kesulitan (+1 panjang sequence setiap level? atau bertahap)
                        # Soal: acak level meningkat mulai dari 2 blink.
                        new_len = 2 + (st.session_state.corsi['level'] - 1)
                        st.session_state.corsi['sequence'] = [random.randint(0, 15) for _ in range(new_len)]
                        st.session_state.corsi['user_input'] = []
                        st.session_state.corsi['playing_sequence'] = True
                        st.session_state.corsi['lives'] = 2 # Reset nyawa di level baru? (Asumsi: Ya)
                        st.rerun()
                    else:
                        st.balloons()
                        st.success("SELAMAT! Anda menamatkan semua level!")
                        st.session_state.step = 5
                        st.rerun()

# --- HALAMAN 5: PENUTUP & SIMPAN DATA ---
elif st.session_state.step == 5:
    st.header("Terimakasih")
    st.write("Terimakasih telah menjadi bagian dari penelitian kami, jawaban anda telah tersimpan secara otomatis.")
    
    # Persiapkan Data Final
    final_payload = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **st.session_state.data_diri,
        "Skor_Kuesioner": st.session_state.skor_kuesioner,
        "Skor_Corsi_Level": st.session_state.corsi['score'],
        "Status_Corsi": "Completed" if st.session_state.corsi['score'] == 9 else "Failed/Stopped"
    }
    
    # Jalankan fungsi simpan (Hanya sekali)
    if 'saved' not in st.session_state:
        save_to_google_sheets(final_payload)
        st.session_state['saved'] = True
    
    st.json(final_payload) # Tampilkan data (untuk debug/user melihat hasil sendiri)
    st.info("Anda boleh menutup halaman ini.")
