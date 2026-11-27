import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Escola de Heróis", page_icon=":material/shield:", layout="wide")

@st.cache_resource
def obter_arena():
    return {"ranking": {}, "recordes": []}

arena = obter_arena()

def patente(xp):
    if xp >= 500: return "Herói Lendário"
    if xp >= 250: return "Comandante Tático"
    if xp >= 100: return "Guardião Oficial"
    if xp >= 30: return "Aprendiz de Herói"
    return "Recruta"

def carregar_dados():
    arqs = ["defesa_pessoal.csv", "seguranca_digital.csv", "logica.csv", "argumentacao.csv", "prototipagem.csv", "outras_materias.csv"]
    dfs = []
    for a in arqs:
        for enc in ["utf-8", "utf-8-sig", "latin-1"]:
            try:
                d = pd.read_csv(a, sep=";", encoding=enc, on_bad_lines="skip")
                if "esquadrao" in [c.strip().lower() for c in d.columns]:
                    d.columns = d.columns.str.strip().str.lower()
                    for c in d.select_dtypes(include="object").columns:
                        d[c] = d[c].astype(str).str.strip()
                    dfs.append(d)
                    break
            except Exception:
                pass
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

for k, v in {
    "xp": 0, "combo": 0, "idx": 0, "t0": time.time(),
    "resp": False, "fb_tipo": None, "fb_msg": "",
    "q_id": "", "certa": "", "ops": [],
    "ar_on": False, "ar_t0": 0.0, "ar_pts": 0, "ar_q": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

df = carregar_dados()

st.sidebar.markdown("## :material/shield: Escola de Heróis")
nome = st.sidebar.text_input("Codinome:", "Novato")
esq = st.sidebar.selectbox("Esquadrão:", ["Cadetes (6 a 10 anos)", "Guardiões (11 a 16 anos)"])
f_esq = "cadet" if "Cadetes" in esq else "guard"

def salvar():
    if nome.strip():
        arena["ranking"][nome.strip()] = {
            "Herói": nome.strip(),
            "Esquadrão": "Cadetes" if "Cadetes" in esq else "Guardiões",
            "Patente": patente(st.session_state.xp),
            "XP": st.session_state.xp,
            "Combo": st.session_state.combo
        }

st.sidebar.metric("XP", st.session_state.xp, delta=f"Combo {st.session_state.combo}x")
st.sidebar.info(f"**Patente:** {patente(st.session_state.xp)}", icon=":material/military_tech:")

menu = st.sidebar.radio("Missões:", [
    "Arena Online: Desafio 60s", "Ranking Global Online",
    "Defesa Pessoal", "Segurança Digital", "Lógica",
    "Argumentação", "Prototipagem Eletrônica", "Outras Matérias"
])

if menu == "Arena Online: Desafio 60s":
    st.markdown(f"## :material/sports_esports: Arena 60s — {esq}")
    sub = df[df["esquadrao"].str.lower().str.startswith(f_esq)].reset_index(drop=True)
    if sub.empty:
        st.warning("Sem perguntas carregadas.")
    elif not st.session_state.ar_on:
        with st.container(border=True):
            st.write("Acerto: **+10 pts / +10 XP** | Erro: **-5 pts / -5 XP**")
            if st.button("Iniciar Arena 60s", icon=":material/play_arrow:"):
                st.session_state.ar_on = True
                st.session_state.ar_t0 = time.time()
                st.session_state.ar_pts = 0
                st.session_state.ar_q = next(iter(sub.sample(1).to_dict(orient="records")))
                st.rerun()
    else:
        @st.fragment(run_every=1)
        def timer_ar():
            rest = max(0, int(60 - (time.time() - st.session_state.ar_t0)))
            if rest > 0:
                st.warning(f"Tempo: **{rest}s** | Pontos: **{st.session_state.ar_pts}**", icon=":material/timer:")
            else:
                st.session_state.ar_on = False
                arena["recordes"].append({"Herói": nome, "Esquadrão": esq[:8], "Pontos": st.session_state.ar_pts})
                salvar()
                st.rerun()

        with st.container(border=True):
            timer_ar()
            q = st.session_state.ar_q
            if isinstance(q, dict):
                st.markdown(f"**[{q['missao']}]** {q['pergunta']}")
                certa = str(q["correta"]).strip()
                ops = [str(q["opcao1"]).strip(), str(q["opcao2"]).strip(), str(q["opcao3"]).strip()]
                extras = [c for c in pd.concat([sub["opcao1"], sub["opcao2"], sub["opcao3"]]).dropna().astype(str).str.strip().unique() if c not in ops and c != "nan"]
                ops.append(random.choice(extras) if extras else "Pedir ajuda a um adulto")
                random.Random(q["pergunta"]).shuffle(ops)
                c1, c2 = st.columns(2)
                for i, op in enumerate(ops):
                    with (c1 if i % 2 == 0 else c2):
                        if st.button(f"{['a)','b)','c)','d)'][i]} {op}", key=f"a_{q['pergunta']}_{i}", use_container_width=True):
                            if op == certa:
                                st.session_state.ar_pts += 10
                                st.session_state.xp += 10
                            else:
                                st.session_state.ar_pts = max(0, st.session_state.ar_pts - 5)
                                st.session_state.xp = max(0, st.session_state.xp - 5)
                            st.session_state.ar_q = next(iter(sub.sample(1).to_dict(orient="records")))
                            st.rerun()

elif menu == "Ranking Global Online":
    st.markdown("## :material/leaderboard: Ranking Global")
    salvar()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top XP")
        if arena["ranking"]:
            r = pd.DataFrame(list(arena["ranking"].values())).sort_values("XP", ascending=False).reset_index(drop=True)
            r.index += 1
            st.dataframe(r, use_container_width=True)
    with c2:
        st.subheader("Recordes 60s")
        if arena["recordes"]:
            rc = pd.DataFrame(arena["recordes"]).sort_values("Pontos", ascending=False).head(10).reset_index(drop=True)
            rc.index += 1
            st.dataframe(rc, use_container_width=True)

else:
    st.markdown(f"## :material/bolt: {menu} — {esq}")
    sub = df[(df["esquadrao"].str.lower().str.startswith(f_esq)) & (df["missao"].str.lower().str.startswith(menu[:3].lower()))].reset_index(drop=True)
    if sub.empty:
        st.warning("Sem perguntas nesta categoria.")
    else:
        tot = len(sub)
        idx = st.session_state.idx % tot
        q = sub.iloc[idx]
        qid = f"{menu}_{f_esq}_{idx}"
        if st.session_state.q_id != qid:
            st.session_state.q_id = qid
            st.session_state.t0 = time.time()
            st.session_state.resp = False
            st.session_state.fb_tipo = None
            certa = str(q["correta"]).strip()
            ops = [str(q["opcao1"]).strip(), str(q["opcao2"]).strip(), str(q["opcao3"]).strip()]
            err = [o for o in ops if o != certa and o != "nan"]
            extras = [c for c in pd.concat([sub["opcao1"], sub["opcao2"], sub["opcao3"]]).dropna().astype(str).str.strip().unique() if c not in ops and c != "nan"]
            lista = [certa] + err[:2] + [random.choice(extras) if extras else "Consultar um adulto responsável"]
            random.shuffle(lista)
            st.session_state.certa = certa
            st.session_state.ops = [f"{['a)','b)','c)','d)'][i]} {lista[i]}" for i in range(4)]

        @st.fragment(run_every=1)
        def timer_q():
            rest = max(0, int(30 - (time.time() - st.session_state.t0)))
            if rest > 0 and not st.session_state.resp:
                st.info(f"Tempo: **{rest}s**", icon=":material/timer:")
            elif rest == 0 and not st.session_state.resp:
                st.session_state.resp = True
                st.session_state.combo = 0
                st.session_state.xp = max(0, st.session_state.xp - 10)
                salvar()
                st.session_state.fb_tipo = "erro"
                st.session_state.fb_msg = f"Tempo esgotado! Correta: {st.session_state.certa} (-10 XP)"
                st.rerun()

        with st.container(border=True):
            t1, t2 = st.columns([3, 1])
            with t1: st.progress((idx + 1) / tot, text=f"Desafio {idx + 1}/{tot}")
            with t2: timer_q()
            esc = st.radio(q["pergunta"], st.session_state.ops, key=f"r_{qid}", disabled=st.session_state.resp)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Confirmar", icon=":material/check_circle:", disabled=st.session_state.resp):
                    st.session_state.resp = True
                    if esc[3:].strip() == st.session_state.certa:
                        st.session_state.combo += 1
                        g = 15 + min(15, (st.session_state.combo - 1) * 3)
                        st.session_state.xp += g
                        st.session_state.fb_tipo = "acerto"
                        st.session_state.fb_msg = f"Correto! {q['explicacao']} (+{g} XP)"
                    else:
                        st.session_state.combo = 0
                        st.session_state.xp = max(0, st.session_state.xp - 10)
                        st.session_state.fb_tipo = "erro"
                        st.session_state.fb_msg = f"Errado! Correta: {st.session_state.certa} (-10 XP). {q['explicacao']}"
                    salvar()
                    st.rerun()
            with b2:
                if st.button("Próxima", icon=":material/arrow_forward:"):
                    st.session_state.idx += 1
                    salvar()
                    st.rerun()
            if st.session_state.fb_tipo == "acerto":
                st.success(st.session_state.fb_msg, icon=":material/verified:")
            elif st.session_state.fb_tipo == "erro":
                st.error(st.session_state.fb_msg, icon=":material/warning:")

st.markdown("""
<style>
@keyframes fundoHeroi { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: linear-gradient(125deg, #030A18 0%, #0B2C59 35%, #0077B6 65%, #04132B 100%) !important; background-size: 300% 300% !important; animation: fundoHeroi 10s ease infinite !important; }
[data-testid="stHeader"] { background: transparent !important; height: 1rem !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
[data-testid="stSidebar"] { background-color: rgba(4, 12, 26, 0.85) !important; border-right: 1px solid rgba(0, 240, 255, 0.35); }
div.stButton > button { background: linear-gradient(135deg, #0052D4, #0088FF); color: #FFF; border: 1px solid #00F0FF; border-radius: 12px; font-weight: bold; box-shadow: 0 0 12px rgba(0, 240, 255, 0.55); }
div.stButton > button:hover { box-shadow: 0 0 22px rgba(0, 240, 255, 0.95); transform: scale(1.02); }
div[data-testid="stVerticalBlockBorderWrapper"] { border: 1.5px solid #00F0FF !important; border-radius: 16px !important; box-shadow: 0 0 18px rgba(0, 240, 255, 0.25) !important; background-color: rgba(7, 17, 36, 0.85) !important; }
</style>
""", unsafe_allow_html=True)
