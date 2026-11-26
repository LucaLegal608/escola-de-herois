import streamlit as st
import pandas as pd
import random
import time
import requests
from streamlit_lottie import st_lottie
from streamlit_local_storage import LocalStorage

st.set_page_config(
    page_title="Escola de Heróis",
    page_icon=":material/shield:",
    layout="wide"
)

localS = LocalStorage()

def carregar_animacao(url):
    try:
        r = requests.get(url, timeout=4)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

ANIM_CERTO = carregar_animacao("https://lottie.host")
ANIM_ERRADO = carregar_animacao("https://lottie.host")

st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(135deg, #0052D4, #0088FF);
    color: #FFFFFF;
    border: 1px solid #00F0FF;
    border-radius: 12px;
    font-weight: bold;
    padding: 0.6rem 1.2rem;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.55);
    transition: all 0.25s ease;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #0066FF, #00C6FF);
    box-shadow: 0 0 22px rgba(0, 240, 255, 0.95);
    transform: scale(1.03);
    border-color: #FFFFFF;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1.5px solid #00F0FF !important;
    border-radius: 16px !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.25) !important;
    background-color: #0B1528 !important;
}
</style>
""", unsafe_allow_html=True)

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
    return pd.concat(listas, ignore_index=True) if listas else pd.DataFrame()

# Recupera dados salvos no navegador ao abrir o app
dados_salvos = localS.getItem("escola_herois_save")
if isinstance(dados_salvos, dict) and "dados_carregados" not in st.session_state:
    st.session_state.xp = int(dados_salvos.get("xp", 0))
    st.session_state.indice_q = int(dados_salvos.get("indice_q", 0))
    st.session_state.nome_salvo = str(dados_salvos.get("nome", "Novato"))
    st.session_state.esquadrao_salvo = str(dados_salvos.get("esquadrao", "Cadetes (6 a 10 anos)"))
    st.session_state.dados_carregados = True

for chave, valor in {
    "xp": 0,
    "indice_q": 0,
    "nome_salvo": "Novato",
    "esquadrao_salvo": "Cadetes (6 a 10 anos)",
    "inicio_tempo": time.time(),
    "respondida": False,
    "feedback_tipo": None,
    "feedback_msg": "",
    "chave_atual": "",
    "resposta_certa_atual": "",
    "opcoes_formatadas": []
}.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

def salvar_progresso(nome, esquadrao):
    localS.setItem("escola_herois_save", {
        "xp": st.session_state.xp,
        "indice_q": st.session_state.indice_q,
        "nome": nome,
        "esquadrao": esquadrao
    })

df_perguntas = carregar_perguntas()

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome_heroi = st.sidebar.text_input("Codinome do Herói:", value=st.session_state.nome_salvo)

opcoes_esq = ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"]
idx_esq = opcoes_esq.index(st.session_state.esquadrao_salvo) if st.session_state.esquadrao_salvo in opcoes_esq else 0
esquadrao_sel = st.sidebar.selectbox("Esquadrão:", opcoes_esq, index=idx_esq)
filtro_esq = "cadet" if "Cadetes" in esquadrao_sel else "guard"

if nome_heroi != st.session_state.nome_salvo or esquadrao_sel != st.session_state.esquadrao_salvo:
    st.session_state.nome_salvo = nome_heroi
    st.session_state.esquadrao_salvo = esquadrao_sel
    salvar_progresso(nome_heroi, esquadrao_sel)

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

st.sidebar.markdown("---")
if st.sidebar.button("Zerar Progresso Salvo", icon=":material/delete:"):
    st.session_state.xp = 0
    st.session_state.indice_q = 0
    st.session_state.chave_atual = ""
    localS.deleteAll()
    st.rerun()

st.markdown(f"# :material/bolt: {menu} — {esquadrao_sel}")
st.caption(f"Herói ativo: **{nome_heroi}** | Progresso salvo automaticamente no navegador")

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
        id_questao = f"{menu}_{filtro_esq}_{idx}"

        if st.session_state.chave_atual != id_questao:
            st.session_state.chave_atual = id_questao
            st.session_state.inicio_tempo = time.time()
            st.session_state.respondida = False
            st.session_state.feedback_tipo = None

            correta_orig = str(q["correta"]).strip()
            todas_op = [str(q["opcao1"]).strip(), str(q["opcao2"]).strip(), str(q["opcao3"]).strip()]
            erradas_orig = [op for op in todas_op if op != correta_orig and op != "nan"]

            # Busca uma 4ª alternativa real de outras questões da mesma missão (ou coluna opcao4 se existir)
            if "opcao4" in q and pd.notna(q["opcao4"]) and str(q["opcao4"]).strip() not in ["", "nan", correta_orig]:
                quarta_op = str(q["opcao4"]).strip()
            else:
                candidatas = pd.concat([sub_df["opcao1"], sub_df["opcao2"], sub_df["opcao3"]]).dropna().astype(str).str.strip().unique().tolist()
                candidatas_validas = [c for c in candidatas if c not in todas_op and c != correta_orig and c != "nan"]
                quarta_op = random.choice(candidatas_validas) if candidatas_validas else "Consultar um adulto responsável ou professor"

            op_lista = [correta_orig] + erradas_orig[:2] + [quarta_op]
            st.session_state.resposta_certa_atual = correta_orig

            random.shuffle(op_lista)
            letras = ["a)", "b)", "c)", "d)"]
            st.session_state.opcoes_formatadas = [f"{letras[i]} {op_lista[i]}" for i in range(4)]

        @st.fragment(run_every=1)
        def exibir_cronometro():
            tempo_limite = 30
            restante = max(0, int(tempo_limite - (time.time() - st.session_state.inicio_tempo)))
            if restante > 0 and not st.session_state.respondida:
                st.info(f"Tempo: **{restante}s**", icon=":material/timer:")
            elif restante == 0 and not st.session_state.respondida:
                st.session_state.respondida = True
                st.session_state.xp = max(0, st.session_state.xp - 10)
                salvar_progresso(nome_heroi, esquadrao_sel)
                st.session_state.feedback_tipo = "erro"
                st.session_state.feedback_msg = f"Tempo esgotado! A resposta certa era: {st.session_state.resposta_certa_atual} (-10 XP)"
                st.rerun()

        with st.container(border=True):
            col_top1, col_top2 = st.columns([3, 1])
            with col_top1:
                st.progress((idx + 1) / total, text=f"Desafio {idx + 1} de {total}")
            with col_top2:
                exibir_cronometro()

            escolha = st.radio(
                q["pergunta"],
                st.session_state.opcoes_formatadas,
                key=f"rad_{id_questao}",
                disabled=st.session_state.respondida
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Confirmar Resposta",
                    icon=":material/check_circle:",
                    disabled=st.session_state.respondida
                ):
                    st.session_state.respondida = True
                    texto_escolhido = escolha[3:].strip()
                    correta_da_vez = st.session_state.resposta_certa_atual
                    if texto_escolhido == correta_da_vez:
                        st.session_state.xp += 15
                        st.session_state.feedback_tipo = "acerto"
                        st.session_state.feedback_msg = f"Excelente! {q['explicacao']} (+15 XP)"
                    else:
                        st.session_state.xp = max(0, st.session_state.xp - 10)
                        st.session_state.feedback_tipo = "erro"
                        st.session_state.feedback_msg = f"Resposta incorreta! A correta era: {correta_da_vez} (-10 XP). {q['explicacao']}"
                    salvar_progresso(nome_heroi, esquadrao_sel)
                    st.rerun()
            with col2:
                if st.button("Próxima Pergunta", icon=":material/arrow_forward:"):
                    st.session_state.indice_q += 1
                    salvar_progresso(nome_heroi, esquadrao_sel)
                    st.rerun()

            if st.session_state.feedback_tipo == "acerto":
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.success(st.session_state.feedback_msg, icon=":material/verified:")
                with col_f2:
                    if ANIM_CERTO:
                        st_lottie(ANIM_CERTO, height=110, key=f"ok_{id_questao}")
            elif st.session_state.feedback_tipo == "erro":
                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.error(st.session_state.feedback_msg, icon=":material/warning:")
                with col_f2:
                    if ANIM_ERRADO:
                        st_lottie(ANIM_ERRADO, height=110, key=f"err_{id_questao}")
