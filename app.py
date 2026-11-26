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

# Memória global compartilhada entre TODOS os jogadores online simultaneamente
@st.cache_resource
def obter_arena_global():
    return {
        "ranking": {},
        "recordes_relampago": []
    }

arena = obter_arena_global()

def calcular_patente(xp):
    if xp >= 500:
        return "Herói Lendário"
    elif xp >= 250:
        return "Comandante Tático"
    elif xp >= 100:
        return "Guardião Oficial"
    elif xp >= 30:
        return "Aprendiz de Herói"
    return "Recruta"

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

dados_salvos = localS.getItem("escola_herois_save")
if isinstance(dados_salvos, dict) and "dados_carregados" not in st.session_state:
    st.session_state.xp = int(dados_salvos.get("xp", 0))
    st.session_state.indice_q = int(dados_salvos.get("indice_q", 0))
    st.session_state.nome_salvo = str(dados_salvos.get("nome", "Novato"))
    st.session_state.esquadrao_salvo = str(dados_salvos.get("esquadrao", "Cadetes (6 a 10 anos)"))
    st.session_state.dados_carregados = True

for chave, valor in {
    "xp": 0,
    "combo": 0,
    "indice_q": 0,
    "nome_salvo": "Novato",
    "esquadrao_salvo": "Cadetes (6 a 10 anos)",
    "inicio_tempo": time.time(),
    "respondida": False,
    "feedback_tipo": None,
    "feedback_msg": "",
    "chave_atual": "",
    "resposta_certa_atual": "",
    "opcoes_formatadas": [],
    "relampago_ativo": False,
    "relampago_inicio": 0.0,
    "relampago_pontos": 0,
    "relampago_q": None
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
    if nome.strip():
        arena["ranking"][nome.strip()] = {
            "Herói": nome.strip(),
            "Esquadrão": "Cadetes" if "Cadetes" in esquadrao else "Guardiões",
            "Patente": calcular_patente(st.session_state.xp),
            "XP": st.session_state.xp,
            "Combo Máx": st.session_state.combo
        }

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

patente_atual = calcular_patente(st.session_state.xp)
st.sidebar.metric("Pontos de XP", st.session_state.xp, delta=f"Combo: {st.session_state.combo}x")
st.sidebar.info(f"**Patente:** {patente_atual}", icon=":material/military_tech:")

menu = st.sidebar.radio(
    "Central de Missões:",
    [
        "Arena Online: Desafio 60s",
        "Ranking Global Online",
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
    st.session_state.combo = 0
    st.session_state.indice_q = 0
    st.session_state.chave_atual = ""
    localS.deleteAll()
    st.rerun()

if menu == "Arena Online: Desafio 60s":
    st.markdown(f"# :material/sports_esports: Arena Relâmpago Online — {esquadrao_sel}")
    st.write("Responda o máximo de perguntas mistas em **60 segundos** para disputar o placar online contra outros heróis!")

    sub_esq = df_perguntas[df_perguntas["esquadrao"].str.lower().str.startswith(filtro_esq)].reset_index(drop=True)

    if sub_esq.empty:
        st.warning("Carregue os arquivos CSV para liberar a Arena.", icon=":material/info:")
    elif not st.session_state.relampago_ativo:
        with st.container(border=True):
            st.subheader("Pronto para entrar na Arena?")
            st.write("Cada acerto vale **+10 pontos** na Arena e **+10 XP** no seu perfil. Cada erro desconta **-5 pontos**.")
            if st.button("Iniciar Desafio de 60 Segundos", icon=":material/play_arrow:"):
                st.session_state.relampago_ativo = True
                st.session_state.relampago_inicio = time.time()
                st.session_state.relampago_pontos = 0
                st.session_state.relampago_q = sub_esq.sample(1).iloc[0]
                st.rerun()
    else:
        @st.fragment(run_every=1)
        def cronometro_arena():
            restante = max(0, int(60 - (time.time() - st.session_state.relampago_inicio)))
            if restante > 0:
                st.warning(f"Tempo da Arena: **{restante}s** | Pontos nesta rodada: **{st.session_state.relampago_pontos}**", icon=":material/timer:")
            else:
                st.session_state.relampago_ativo = False
                arena["recordes_relampago"].append({
                    "Herói": nome_heroi,
                    "Esquadrão": "Cadetes" if "Cadetes" in esquadrao_sel else "Guardiões",
                    "Pontos (60s)": st.session_state.relampago_pontos
                })
                salvar_progresso(nome_heroi, esquadrao_sel)
                st.rerun()

        with st.container(border=True):
            cronometro_arena()
            q_ar = st.session_state.relampago_q
            st.caption(f"Categoria sorteada: **{q_ar['missao']}**")
            st.subheader(q_ar["pergunta"])

            correta_ar = str(q_ar["correta"]).strip()
            ops_ar = [str(q_ar["opcao1"]).strip(), str(q_ar["opcao2"]).strip(), str(q_ar["opcao3"]).strip()]
            candidatas = pd.concat([sub_esq["opcao1"], sub_esq["opcao2"], sub_esq["opcao3"]]).dropna().astype(str).str.strip().unique().tolist()
            extras = [c for c in candidatas if c not in ops_ar and c != "nan"]
            ops_ar.append(random.choice(extras) if extras else "Pedir ajuda imediata a um adulto")

            random.Random(q_ar["pergunta"]).shuffle(ops_ar)
            letras = ["a)", "b)", "c)", "d)"]
            ops_fmt = [f"{letras[i]} {ops_ar[i]}" for i in range(4)]

            for op_texto in ops_fmt:
                if st.button(op_texto, key=f"ar_{q_ar['pergunta']}_{op_texto}"):
                    if op_texto[3:].strip() == correta_ar:
                        st.session_state.relampago_pontos += 10
                        st.session_state.xp += 10
                    else:
                        st.session_state.relampago_pontos = max(0, st.session_state.relampago_pontos - 5)
                        st.session_state.xp = max(0, st.session_state.xp - 5)
                    st.session_state.relampago_q = sub_esq.sample(1).iloc[0]
                    st.rerun()

elif menu == "Ranking Global Online":
    st.markdown("# :material/leaderboard: Ranking Global em Tempo Real")
    st.write("Veja a classificação dos jogadores conectados na Escola de Heróis!")

    if st.button("Atualizar Placar Online", icon=":material/refresh:"):
        salvar_progresso(nome_heroi, esquadrao_sel)
        st.rerun()

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader(":material/military_tech: Top XP Geral")
        if arena["ranking"]:
            df_rank = pd.DataFrame(list(arena["ranking"].values())).sort_values(by="XP", ascending=False).reset_index(drop=True)
            df_rank.index = df_rank.index + 1
            st.dataframe(df_rank, use_container_width=True)
        else:
            st.info("Responda a uma missão para registrar seu nome no placar!", icon=":material/info:")

    with col_r2:
        st.subheader(":material/bolt: Recordes da Arena 60s")
        if arena["recordes_relampago"]:
            df_rec = pd.DataFrame(arena["recordes_relampago"]).sort_values(by="Pontos (60s)", ascending=False).head(10).reset_index(drop=True)
            df_rec.index = df_rec.index + 1
            st.dataframe(df_rec, use_container_width=True)
        else:
            st.info("Nenhuma partida de 60s finalizada ainda. Seja o primeiro!", icon=":material/sports_esports:")

else:
    st.markdown(f"# :material/bolt: {menu} — {esquadrao_sel}")
    st.caption(f"Herói ativo: **{nome_heroi}** | Patente: **{patente_atual}** | Combo atual: **{st.session_state.combo}x**")

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
                    st.session_state.combo = 0
                    st.session_state.xp = max(0, st.session_state.xp - 10)
                    salvar_progresso(nome_heroi, esquadrao_sel)
                    st.session_state.feedback_tipo = "erro"
                    st.session_state.feedback_msg = f"Tempo esgotado! A resposta certa era: {st.session_state.resposta_certa_atual} (-10 XP)"
                    st.rerun()

            with st.container(border=True):
                col_top1, col_top2 = st.columns(2)
                with col_top1:
                    st.progress((idx + 1) / total, text=f"Desafio {idx + 1} de {total}")
                with col_top2:
                    exibir_cronometro()

                escolha = st.radio(
                    q["pergunta"],

