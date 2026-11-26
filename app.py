import streamlit as st
import random

st.set_page_config(
    page_title="Escola de Heróis",
    page_icon=":material/shield:",
    layout="centered"
)

if "xp" not in st.session_state:
    st.session_state.xp = 0
if "codigo_secreto" not in st.session_state:
    st.session_state.codigo_secreto = random.randint(10, 50)
if "tentativas" not in st.session_state:
    st.session_state.tentativas = 0

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome_heroi = st.sidebar.text_input("Codinome do Herói:", "Novato")

faixa_etaria = st.sidebar.selectbox(
    "Selecione seu Esquadrão:",
    ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"]
)

xp = st.session_state.xp
if xp >= 50:
    patente = "Herói Lendário"
elif xp >= 30:
    patente = "Guardião Oficial"
elif xp >= 10:
    patente = "Aprendiz de Herói"
else:
    patente = "Recruta"

st.sidebar.markdown("---")
st.sidebar.metric("Pontos de XP", xp)
st.sidebar.info(f"**Patente Atual:** {patente}", icon=":material/military_tech:")

menu = st.sidebar.radio(
    "Central de Missões:",
    [
        "Quartel-General",
        "Missão: Defesa Pessoal",
        "Treino Mental (Outras Matérias)",
        "Jogo: Radar de Atenção"
    ]
)

if menu == "Quartel-General":
    st.markdown(f"# :material/castle: Bem-vindo(a), {nome_heroi}!")
    st.subheader(f"Esquadrão: {faixa_etaria}")
    st.write(
        "Na Escola de Heróis, o poder está na mente alerta e na prevenção. "
        "Complete as missões no menu ao lado para ganhar XP."
    )
    st.warning(
        "Regra de Ouro: Defesa pessoal serve para proteger e evitar o perigo.",
        icon=":material/gavel:"
    )

elif menu == "Missão: Defesa Pessoal":
    st.markdown("# :material/health_and_safety: Treinamento de Defesa Pessoal")
    st.write("Escolha a atitude mais segura (+15 XP).")

    if "Cadetes" in faixa_etaria:
        situacao = (
            "Um adulto desconhecido oferece um doce no parque e pede ajuda. "
            "O que um herói faz?"
        )
        opcoes = [
            "Vai ajudar rápido para ser educado.",
            "Diz NÃO bem alto, se afasta e avisa um adulto de confiança.",
            "Aceita o doce, mas diz que não pode ir."
        ]
        correta = opcoes[1]
        explicacao = "Heróis nunca vão com estranhos e sempre avisam um adulto."
    else:
        situacao = (
            "Você percebe que alguém está te seguindo na rua. "
            "Qual a melhor estratégia?"
        )
        opcoes = [
            "Colocar fones e entrar em uma rua vazia.",
            "Confrontar a pessoa na rua.",
            "Entrar em um local público movimentado e ligar para um responsável."
        ]
        correta = opcoes[2]
        explicacao = "A base da defesa pessoal é buscar locais seguros e movimentados."

    escolha = st.radio(situacao, opcoes)

    if st.button("Confirmar Decisão", icon=":material/check_circle:"):
        if escolha == correta:
            st.session_state.xp += 15
            st.success(f"Missão Cumprida! {explicacao} (+15 XP)", icon=":material/verified:")
        else:
            st.error("Cuidado! Essa atitude traz riscos. Tente novamente.", icon=":material/warning:")

      elif menu == "Treino Mental (Outras Matérias)":
    st.markdown("# :material/psychology: Academia do Conhecimento")
    st.write("Um herói também domina ciências e lógica (+10 XP).")

    if "Cadetes" in faixa_etaria:
        pergunta = "[Ciências] Qual parte da planta absorve água do solo?"
        opcoes = ["As folhas", "A raiz", "As flores"]
        resposta_certa = "A raiz"
    else:
        pergunta = "[Ciências] Qual gás agrava o efeito estufa?"
        opcoes = ["Oxigênio (O2)", "Dióxido de Carbono (CO2)", "Hélio (He)"]
        resposta_certa = "Dióxido de Carbono (CO2)"

    resp_materia = st.radio(pergunta, opcoes)

    if st.button("Enviar Resposta", icon=":material/send:"):
        if resp_materia == resposta_certa:
            st.session_state.xp += 10
            st.success("Resposta exata! (+10 XP)", icon=":material/bolt:")
        else:
            st.warning("Quase! Tente novamente.", icon=":material/refresh:")

elif menu == "Jogo: Radar de Atenção":
    st.markdown("# :material/radar: Radar do Herói")
    st.write("Descubra o código secreto entre 10 e 50 (+20 XP).")

    palpite = st.number_input("Digite o código:", min_value=10, max_value=50, step=1)

    if st.button("Testar Código", icon=":material/lock_open:"):
        st.session_state.tentativas += 1
        alvo = st.session_state.codigo_secreto

        if palpite == alvo:
            st.session_state.xp += 20
            st.success(
                f"Desbloqueado em {st.session_state.tentativas} tentativas! (+20 XP)",
                icon=":material/key:"
            )
            st.session_state.codigo_secreto = random.randint(10, 50)
            st.session_state.tentativas = 0
        elif palpite < alvo:
            st.info("O código secreto é MAIOR.", icon=":material/arrow_upward:")
        else:
            st.info("O código secreto é MENOR.", icon=":material/arrow_downward:")
