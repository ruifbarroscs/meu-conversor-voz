import streamlit as st
import edge_tts
import asyncio
import base64
import time
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Consola de Voz PT-PT", layout="wide")

# Dicionário de Vozes PT-PT
VOZES = {
    "Raquel (Feminina - Calma)": "pt-PT-RaquelNeural",
    "Fernanda (Feminina - Alegre)": "pt-PT-FernandaNeural",
    "Duarte (Masculino - Natural)": "pt-PT-DuarteNeural"
}

# Estilo CSS para melhorar o visual
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 16px; }
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

async def gerar_audio(texto, voz, velocidade, tom):
    # Formatação de velocidade e tom para o edge-tts (ex: +0%, -10%)
    speed_str = f"{velocidade:+d}%"
    pitch_str = f"{tom:+d}Hz"
    
    communicate = edge_tts.Communicate(texto, voz, rate=speed_str, pitch=pitch_str)
    filename = f"audio_{int(time.time())}.mp3"
    await communicate.save(filename)
    return filename

def tocar_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Inicialização do Histórico e Ciclos
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.title("🎙️ Consola Multi-Ciclo de Voz PT-PT")

# Sidebar para Histórico
with st.sidebar:
    st.header("📜 Histórico")
    if st.session_state.historico:
        for item in reversed(st.session_state.historico):
            st.info(f"**{item['hora']}**\n\n{item['texto'][:50]}...")
    else:
        st.write("Nenhuma mensagem enviada.")

# Área de Criação de Ciclos
st.subheader("Configurar Novo Ciclo")
col_text, col_cfg = st.columns([2, 1])

with col_text:
    texto_input = st.text_area("Texto para ler:", placeholder="Escreve aqui o que a voz deve dizer...", height=150)

with col_cfg:
    voz_escolhida = st.selectbox("Voz:", list(VOZES.keys()))
    velocidade = st.slider("Velocidade (%)", -50, 50, -10)
    tom = st.slider("Tom (Hz)", -50, 50, 0)
    intervalo = st.number_input("Intervalo (minutos)", min_value=1, value=20)

if st.button("🚀 Iniciar Este Ciclo"):
    if texto_input:
        # Adicionar ao histórico
        agora = datetime.now().strftime("%H:%M:%S")
        st.session_state.historico.append({"hora": agora, "texto": texto_input})
        
        status_placeholder = st.empty()
        
        # Início do Loop
        try:
            while True:
                status_placeholder.warning(f"🔔 A reproduzir agora... ({agora})")
                
                # Gera e toca
                arquivo = asyncio.run(gerar_audio(texto_input, VOZES[voz_escolhida], velocidade, tom))
                tocar_audio(arquivo)
                
                # Contagem decrescente
                for i in range(intervalo * 60, 0, -1):
                    m, s = divmod(i, 60)
                    status_placeholder.info(f"⏳ Próxima leitura em {m:02d}:{s:02d} | Voz: {voz_escolhida}")
                    time.sleep(1)
                    
        except Exception as e:
            st.error(f"O ciclo foi interrompido ou parado.")
    else:
        st.error("Por favor, introduz um texto primeiro!")

st.divider()
st.caption
