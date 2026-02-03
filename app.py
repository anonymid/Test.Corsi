import streamlit as st
import requests
import time
import random
import streamlit as st


# --- CONFIG ---
st.set_page_config(page_title="Penelitian Psikologi", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxwN-PHPecqTdSZDyGiQyKAtfYNcLtuMeqPi8nGJ3gKlmFl3aCInGN0K_SlxmCZffKmXQ/exec"

# --- INIT STATE ---
if 'page' not in st.session_state: st.session_state.page = "welcome"
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'corsi_level' not in st.session_state: st.session_state.corsi_level = 1
if 'corsi_sequence' not in st.session_state: st.session_state.corsi_sequence = []
if 'corsi_user_input' not in st.session_state: st.session_state.corsi_user_input = []
if 'corsi_phase' not in st.session_state: st.session_state.corsi_phase = "idle"
if 'corsi_lives' not in st.session_state: st.session_state.corsi_lives = 2
if 'corsi_score' not in st.session_state: st.session_state.corsi_score = 0

def send_data(data):
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=data)
        return True
    except:
        return False

# --- CSS AMAN (ANTI ERROR SAFARI/IPHONE) ---
st.markdown("""
<style>
    /* Layout Dasar */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* Gunakan class spesifik untuk membungkus Grid Game */
    .papan-game {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 15px !important;
        max-width: 450px !important;
        margin: 0 auto !important;
        justify-items: center;
    }

    /* Target Tombol di dalam Game agar Bulat */
    /* Kita pakai selector button yang lebih umum tapi tetap dalam konteks grid */
    div[data-testid="column"] button {
        border-radius: 50% !important;
        width: 75px !important;
        height: 75px !important;
        min-width: 75px !important;
        line-height: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* KEMBALIKAN TOMBOL NAVIGASI JADI KOTAK */
    /* Tombol Mulai/Lanjut biasanya punya class st-emotion-cache atau 'kind-primary' */
    button[kind="primary"], button[kind="secondaryFormSubmit"] {
        border-radius: 8px !important;
        width: 100% !important;
        height: auto !important;
        padding: 10px 20px !important;
    }

    @media (max-width: 600px) {
        div[data-testid="column"] button {
            width: 55px !important;
            height: 55px !important;
            min-width: 55px !important;
        }
        .papan-game { gap: 10px !important; max-width: 280px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI VISUAL CORSI ---
def get_corsi_html(highlight_idx=None):
    boxes = ""
    for i in range(16):
        color = "#007bff" if i == highlight_idx else "#e0e0e0"
        boxes += f'<div style="background-color:{color}; border-radius:50%; border:2px solid #999; width:100%; aspect-ratio:1/1;"></div>'
    
    return f"""
    <div class="papan-game">
        {boxes}
    </div>
    """

# --- PAGE LOGIC ---
if st.session_state.page == "welcome":
    st.title("Penelitian Pengaruh Ketergantungan Internet terhadap Kinerja Memori Kerja")
    st.write("Terimakasih telah bersedia menjadi responden kami...")
    bersedia = st.checkbox("Apakah anda bersedia menjadi responden?")
    if st.button("Lanjut", type="primary", disabled=not bersedia):
        st.session_state.page = "data_diri"
        st.rerun()

elif st.session_state.page == "data_diri":
    st.header("Data Responden")
    with st.form("form_data"):
        st.session_state.user_data['inisial'] = st.text_input("Inisial")
        st.session_state.user_data['umur'] = st.selectbox("Umur", list(range(17, 29)))
        st.session_state.user_data['wa'] = st.text_input("Nomor Whatsapp")
        # ... (tambahkan field lainnya sesuai kebutuhan)
        if st.form_submit_button("Lanjut"):
            st.session_state.page = "kuesioner"
            st.rerun()

elif st.session_state.page == "kuesioner":
    st.header("Kuesioner")
    questions = ["Saya bermain internet lebih lama...", "Soal 2...", "Soal 3..."] # Lengkapi daftar soalnya
    responses = []
    with st.form("form_k"):
        for i, q in enumerate(questions):
            st.write(f"{i+1}. {q}")
            val = st.radio(f"q{i}", [1,2,3,4], horizontal=True, index=None, key=f"k_{i}")
            responses.append(val)
        if st.form_submit_button("Mulai Tes"):
            if None in responses: st.error("Isi semua!")
            else:
                st.session_state.user_data['skor_kuesioner'] = sum(responses)
                st.session_state.page = "corsi_game"
                st.rerun()

elif st.session_state.page == "corsi_game":
    st.header("Tes Corsi Block Tapping")
    st.write(f"Level: {st.session_state.corsi_level} / 9")
    
    if st.session_state.corsi_phase == "idle":
        st.markdown(get_corsi_html(None), unsafe_allow_html=True)
        if st.button("Mulai Level Ini", type="primary"):
            st.session_state.corsi_sequence = [random.randint(0, 15) for _ in range(st.session_state.corsi_level + 1)]
            st.session_state.corsi_user_input = []
            st.session_state.corsi_phase = "showing"
            st.rerun()

    elif st.session_state.corsi_phase == "showing":
        papan = st.empty()
        for item in st.session_state.corsi_sequence:
            papan.markdown(get_corsi_html(item), unsafe_allow_html=True)
            time.sleep(0.8)
            papan.markdown(get_corsi_html(None), unsafe_allow_html=True)
            time.sleep(0.3)
        st.session_state.corsi_phase = "input"
        st.rerun()

    elif st.session_state.corsi_phase == "input":
        st.write("Giliran Kamu!")
        # Render tombol 4x4
        for r in range(4):
            cols = st.columns(4)
            for c in range(4):
                idx = r * 4 + c
                if cols[c].button(" ", key=f"btn_{idx}"):
                    st.session_state.corsi_user_input.append(idx)
                    curr = len(st.session_state.corsi_user_input) - 1
                    if st.session_state.corsi_user_input[curr] != st.session_state.corsi_sequence[curr]:
                        st.session_state.corsi_lives -= 1
                        if st.session_state.corsi_lives <= 0: st.session_state.page = "saving"
                        else: st.session_state.corsi_phase = "idle"
                        st.rerun()
                    elif len(st.session_state.corsi_user_input) == len(st.session_state.corsi_sequence):
                        st.session_state.corsi_score = st.session_state.corsi_level
                        if st.session_state.corsi_level >= 9: st.session_state.page = "saving"
                        else:
                            st.session_state.corsi_level += 1
                            st.session_state.corsi_lives = 2
                            st.session_state.corsi_phase = "idle"
                        st.rerun()

elif st.session_state.page == "saving":
    st.header("Penutup")
    payload = st.session_state.user_data
    payload['skor_corsi'] = st.session_state.corsi_score
    if send_data(payload):
        st.success("Terimakasih! Jawaban tersimpan.")
        st.balloons()
