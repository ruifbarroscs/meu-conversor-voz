mport streamlit as st
from supabase import create_client, Client
import edge_tts
import asyncio
import base64
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE ACESSO (SECRETS) ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro nos Secrets: {e}")
    st.stop()

# --- 2. FUNÇÕES DE ÁUDIO ---
VOZES = {
    "Raquel (Feminina)": "pt-PT-RaquelNeural",
    "Duarte (Masculino)": "pt-PT-DuarteNeural",
    "Fernanda (Feminina)": "pt-PT-FernandaNeural"
}

async def gerar_audio(texto, voz, velocidade):
    speed_str = f"{velocidade:+d}%"
    communicate = edge_tts.Communicate(texto, voz, rate=speed_str)
    filename = "temp_audio.mp3"
    await communicate.save(filename)
    return filename

def tocar_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)

# --- 3. GESTÃO DE SESSÃO ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Login")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
            st.session_state.user = res.user
            st.rerun()
        except:
            st.error("Dados de login incorretos.")
    st.stop()

# --- 4. APP PRINCIPAL ---
st.sidebar.title("Opções")
st.sidebar.write(f"Utilizador: {st.session_state.user.
