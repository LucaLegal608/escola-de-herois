import streamlit as st
import random
import requests
from streamlit_lottie import st_lottie
from perguntas import DEFESA_CADETES, DEFESA_GUARDIOES

st.set_page_config(
    page_title="Escola de Heróis",
    page_icon=":material/shield:",
    layout="wide"
)

def carregar_animacao(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None

# CSS para deixar botões e cartões mais bonitos
st.markdown("""
<style>
div.stButton > button {
    border-radius: 12px;
    font-weight: bold;
    padding: 0.6rem 1.2rem;
    transition: transform 0.2s;
}
div.stButton > button:hover {
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)

if "xp" not in st.session_state:
    st.session_state.xp = 0
if "indice_q" not in st.session_state:
    st.session_state.indice_q = 0

anim_heroi = carregar_animacao("https://lottie.host")

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome_heroi = st.sidebar.text_input("Codinome:", "Novato")
esquadrao = st.sidebar.selectbox(
    "Esquadrão:",
    ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"]
)

st.sidebar.metric("Pontos de XP", st.session_state.xp)
menu = st.sidebar.radio(
    "Missões:",
    ["Quartel-General", "Missão: Defesa Pessoal"]
)

if menu == "Quartel-General":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"# :material/castle: Quartel-General de {nome_heroi}")
        st.write("Complete os desafios diários para dominar a defesa pessoal e subir de nível.")
        st.info("Cada missão sorteia um novo desafio do nosso banco de treinamento.", icon=":material/bolt:")
    with col2:
        if anim_heroi:
            st_lottie(anim_heroi, height=220, key="hero_anim")

elif menu == "Missão: Defesa Pessoal":
    st.markdown("# :material/health_and_safety: Treinamento Tático")
    banco = DEFESA_CADETES if "Cadetes" in esquadrao else DEFESA_GUARDIOES
    
    # Garante que o índice não passe do tamanho da lista
    idx = st.session_state.indice_q % len(banco)
    questao = banco[idx]

    with st.container(border=True):
        st.subheader(f"Desafio #{idx + 1}")
        escolha = st.radio(questao["pergunta"], questao["opcoes"], key=f"q_{idx}")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Confirmar Resposta", icon=":material/check_circle:", type="primary"):
                if escolha == questao["correta"]:
                    st.session_state.xp += 15
                    st.success(f"Excelente! {questao['explicacao']} (+15 XP)", icon=":material/verified:")
                else:
                    st.error("Atenção! Releia a situação e tente outra abordagem.", icon=":material/warning:")
        with col_btn2:
            if st.button("Próxima Missão", icon=":material/arrow_forward:"):
                st.session_state.indice_q = random.randint(0, len(banco) - 1)
                st.rerun()
