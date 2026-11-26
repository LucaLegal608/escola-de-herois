import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Escola de Heróis",
    page_icon=":material/shield:",
    layout="wide"
)

def ler_csv_seguro(nome_arquivo):
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            df = pd.read_csv(nome_arquivo, sep=";", encoding=enc, on_bad_lines="skip")
            if "esquadrao" in [c.strip().lower() for c in df.columns]:
                df.columns = df.columns.str.strip().str.lower()
                for col in df.select_dtypes(include="object").columns:
                    df[col] = df[col].astype(str).str.strip()
                return df
        except Exception:
            continue
    return pd.DataFrame()

def carregar_perguntas():
    arquivos = [
        "defesa_pessoal.csv",
        "seguranca_digital.csv",
        "logica.csv",
        "argumentacao.csv",
        "prototipagem.csv",
        "outras_materias.csv"
    ]
    listas = [ler_csv_seguro(arq) for arq in arquivos]
    listas = [df for df in listas if not df.empty]
    if listas:
        return pd.concat(listas, ignore_index=True)
    return pd.DataFrame()

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

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome_heroi = st.sidebar.text_input("Codinome do Herói:", "Novato")
esquadrao_sel = st.sidebar.selectbox(
    "Esquadrão:",
    ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"]
)
filtro_esq = "cadet" if "Cadetes" in esquadrao_sel else "guard"

st.sidebar.metric("Pontos de XP", st.session_state.xp)
menu = st.sidebar.radio(
    "Central de Missões:",
    [
        "Defesa Pessoal",
        "Segurança Digital",
        "Lógica",
        "Argumentação",
        "Prototipagem Eletrônica",
        "Outras Matérias"
    ]
)

st.markdown(f"# :material/bolt: {menu} — {esquadrao_sel}")
st.caption(f"Herói ativo: **{nome_heroi}**")

if df_perguntas.empty:
    st.error("Nenhum arquivo CSV encontrado na raiz do repositório.", icon=":material/error:")
else:
    prefixo_missao = menu[:3].lower()
    sub_df = df_perguntas[
        (df_perguntas["esquadrao"].str.lower().str.startswith(filtro_esq)) &
        (df_perguntas["missao"].str.lower().str.startswith(prefixo_missao))
    ].reset_index(drop=True)

    if sub_df.empty:
        st.warning(f"Nenhuma pergunta encontrada para {esquadrao_sel} em {menu}.", icon=":material/info:")
    else:
        total = len(sub_df)
        idx = st.session_state.indice_q % total
        q = sub_df.iloc[idx]
        opcoes = [q["opcao1"], q["opcao2"], q["opcao3"]]

        with st.container(border=True):
            st.progress((idx + 1) / total, text=f"Desafio {idx + 1} de {total}")
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
