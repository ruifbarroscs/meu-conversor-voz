import streamlit as st
from supabase import create_client, Client
import edge_tts
import asyncio
import base64
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE ACESSO ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Erro nos Secrets do Streamlit. Verifica as chaves!")
    st.stop()

# --- 2. FUNÇÕES DE ÁUDIO (PT-PT) ---
VOZES = {
    "Raquel (Feminina)": "pt-PT-RaquelNeural",
    "Duarte (Masculino)": "pt-PT-DuarteNeural",
    "Fernanda (Feminina)": "pt-PT-FernandaNeural"
}

async def gerar_audio(texto, voz, velocidade):
    speed_str = f"{velocidade:+d}%"
    communicate = edge_tts.Communicate(texto, voz, rate=speed_str)
    filename = f"temp_audio.mp3"
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
            st.error("Dados incorretos.")
    st.stop()

# --- 4. APP PRINCIPAL ---
st.sidebar.title("Opções")
st.sidebar.write(f"Utilizador: {st.session_state.user.email}")
if st.sidebar.button("Sair"):
    st.session_state.user = None
    st.rerun()

st.title("🎙️ Repetidor de Frases PT-PT")

# Secção para guardar novas frases
with st.expander("➕ Adicionar à Biblioteca"):
    nome_f = st.text_input("Nome da frase (ex: Aviso 1)")
    texto_f = st.text_area("O que deve ser dito?")
    if st.button("Guardar na Base de Dados"):
        try:
            supabase.table("frases_guardadas").insert({
                "email": st.session_state.user.email,
                "frase": texto_f,
                "nome_predefinicao": nome_f
            }).execute()
            st.success("Guardado com sucesso!")
            time.sleep(1)
            st.rerun()
        except:
            st.error("Erro: Já criaste a tabela no SQL Editor do Supabase?")

# Carregar frases guardadas
try:
    res = supabase.table("frases_guardadas").select("*").eq("email", st.session_state.user.email).execute()
    frases = res.data
except:
    frases = []

# Configurações de Voz
st.divider()
if frases:
    escolha = st.selectbox("Escolher frase da biblioteca:", [f["nome_predefinicao"] for f in frases])
    texto_final = next(f["frase"] for f in frases if f["nome_predefinicao"] == escolha)
    st.info(f"Texto selecionado: {texto_final}")
else:
    texto_final = st.text_area("Texto livre:", "Olá, bem-vindo à tua consola de voz.")

col1, col2 = st.columns(2)
voz_escolhida = col1.selectbox("Voz:", list(VOZES.keys()))
velocidade = col1.slider("Velocidade:", -50, 50, 0)
intervalo = col2.number_input("Repetir a cada (minutos):", 1, 1440, 20)

# --- 5. O CICLO DE REPETIÇÃO ---
if st.button("▶️ INICIAR CICLO"):
    placeholder = st.empty()
    while True:
        placeholder.warning(f"🔔 A tocar agora... ({datetime.now().strftime('%H:%M:%S')})")
        arquivo = asyncio.run(gerar_audio(texto_final, VOZES[voz_escolhida], velocidade))
        tocar_audio(arquivo)
        
        # Contagem decrescente visual
        for i in range(int(intervalo * 60), 0, -1):
            mins, segs = divmod(i, 60)
            placeholder.info(f"⏳ Próxima repetição em {mins:02d}:{segs:02d}")
            time.sleep(1)

