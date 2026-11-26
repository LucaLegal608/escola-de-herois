import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="Escola de Heróis",
    page_icon=":material/shield:",
    layout="wide"
)

def carregar_perguntas():
    arquivos = ["defesa_pessoal.csv", "seguranca_digital.csv", "outras_materias.csv"]
    listas = []
    for arq in arquivos:
        try:
            df_temp = pd.read_csv(arq, sep=";", encoding="utf-8", on_bad_lines="skip")
            df_temp.columns = df_temp.columns.str.strip()
            for col in df_temp.select_dtypes(include="object").columns:
                df_temp[col] = df_temp[col].astype(str).str.strip()
            listas.append(df_temp)
        except Exception:
            pass
    if listas:
        return pd.concat(listas, ignore_index=True)
    return pd.DataFrame()

def carregar_animacao(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

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

df_perguntas = carregar_perguntas()
anim_heroi = carregar_animacao("https://lottie.host")

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome_heroi = st.sidebar.text_input("Codinome:", "Novato")
esquadrao_sel = st.sidebar.selectbox(
    "Esquadrão:",
    ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"]
)
filtro_esq = "Cadetes" if "Cadetes" in esquadrao_sel else "Guardiões"

st.sidebar.metric("Pontos de XP", st.session_state.xp)
menu = st.sidebar.radio(
    "Central de Missões:",
    ["Quartel-General", "Defesa Pessoal", "Segurança Digital", "Outras Matérias"]
)

if menu == "Quartel-General":
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"# :material/castle: Quartel-General de {nome_heroi}")
        st.write("Escolha uma missão no menu ao lado para treinar suas habilidades e ganhar XP.")
        st.info(f"Banco ativo com {len(df_perguntas)} missões cadastradas.", icon=":material/database:")
    with col2:
        if anim_heroi:
            st_lottie(anim_heroi, height=220, key="hero_anim")

else:
    st.markdown(f"# :material/health_and_safety: Missão: {menu}")
    if df_perguntas.empty:
        st.error("Nenhum arquivo CSV encontrado na raiz do repositório.", icon=":material/error:")
    else:
        sub_df = df_perguntas[
            (df_perguntas["esquadrao"] == filtro_esq) &
            (df_perguntas["missao"] == menu)
        ].reset_index(drop=True)

        if sub_df.empty:
            st.warning(f"Nenhuma pergunta encontrada para {filtro_esq} em {menu}.", icon=":material/info:")
        else:
            idx = st.session_state.indice_q % len(sub_df)
            q = sub_df.iloc[idx]
            opcoes = [q["opcao1"], q["opcao2"], q["opcao3"]]

            with st.container(border=True):
                st.caption(f"Questão {idx + 1} de {len(sub_df)}")
                escolha = st.radio(q["pergunta"], opcoes, key=f"q_{menu}_{filtro_esq}_{idx}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirmar Resposta", icon=":material/check_circle:", type="primary"):
                        if escolha == q["correta"]:
                            st.session_state.xp += 15
                            st.success(f"Excelente! {q['explicacao']} (+15 XP)", icon=":material/verified:")
                        else:
                            st.error("Atenção! Releia a situação e tente outra opção.", icon=":material/warning:")
                with col2:
                    if st.button("Próxima Pergunta", icon=":material/arrow_forward:"):
                        st.session_state.indice_q += 1
                        st.rerun()
