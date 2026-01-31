import streamlit as st
from supabase import create_client, Client
import edge_tts
import asyncio
import base64
import time

# --- CONFIGURAÇÕES DE SEGURANÇA (Vão ficar escondidas no Streamlit) ---
# O Streamlit vai ler estas chaves da área "Secrets" que já te explico
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Erro: Configurações do Supabase não encontradas nos Secrets.")

# --- INTERFACE DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.sidebar.title("🔐 Acesso")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user
            st.rerun()
        except: st.sidebar.error("Falha no login")
        
    if col2.button("Criar Conta"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.sidebar.success("Verifica o teu email para confirmar!")
        except: st.sidebar.error("Erro ao criar conta")

if st.session_state.user is None:
    login()
    st.warning("Por favor, faz login para usar a tua biblioteca de frases.")
    st.stop()

# --- APLICAÇÃO PRINCIPAL (Após Login) ---
st.title(f"🎙️ Biblioteca de {st.session_state.user.email}")

# Seção para guardar nova frase
with st.expander("💾 Guardar Nova Frase Predefinida"):
    nome_frase = st.text_input("Nome da Predefinição (ex: Aviso de Pausa)")
    texto_frase = st.text_area("Texto para ler")
    if st.button("Guardar na Nuvem"):
        supabase.table("frases_guardadas").insert({
            "email": st.session_state.user.email,
            "frase": texto_frase,
            "nome_predefinicao": nome_frase
        }).execute()
        st.success("Guardado com sucesso!")

# Seção para carregar frases
st.subheader("📚 As Minhas Frases")
res = supabase.table("frases_guardadas").select("*").eq("email", st.session_state.user.email).execute()
frases = res.data

if frases:
    escolha = st.selectbox("Escolher uma frase guardada:", [f["nome_predefinicao"] for f in frases])
    texto_atual = next(f["frase"] for f in frases if f["nome_predefinicao"] == escolha)
    st.info(f"Texto selecionado: {texto_atual}")
    
    # Aqui segues com o código de repetição (gerar_audio e tocar_audio) que já tínhamos
else:
    st.write("Ainda não tens frases guardadas.")

if st.sidebar.button("Sair (Logout)"):
    st.session_state.user = None
    st.rerun()
