import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# CONFIGURACAO DA PAGINA
# =========================
st.set_page_config(
    page_title="Dashboard de Reunioes",
    page_icon="📅",
    layout="wide"
)

# =========================
# ESTILO DARK THEME
# =========================
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }

        h1, h2, h3, p, span, div {
            color: #FAFAFA;
        }

        .card {
            background-color: #161B22;
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #30363D;
            margin-bottom: 18px;
        }

        .metric-card {
            background-color: #1F2937;
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #374151;
        }

        .dia-livre {
            display: inline-block;
            background-color: #1F6FEB;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 5px;
            font-weight: 600;
        }

        .aviso {
            background-color: #3B1D1D;
            color: #FFB4B4;
            padding: 14px;
            border-radius: 10px;
            border: 1px solid #7F1D1D;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# CAMINHOS DO PROJETO
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

MESES = {
    5: "Maio",
    6: "Junho",
    7: "Julho"
}

# =========================
# FUNCOES
# =========================
@st.cache_data
def carregar_dados_mes(mes_numero):
    data_path = DATA_DIR / f"dias_livres_{mes_numero}.csv"

    if not data_path.exists():
        return None

    df = pd.read_csv(data_path)

    possiveis_colunas_data = [
        "data",
        "dia",
        "data_livre",
        "dias_livres",
        "data_compromisso"
    ]

    coluna_data = None

    for coluna in possiveis_colunas_data:
        if coluna in df.columns:
            coluna_data = coluna
            break

    if coluna_data is None:
        coluna_data = df.columns[0]

    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    df = df.dropna(subset=[coluna_data])

    df["mes"] = df[coluna_data].dt.month
    df["dia"] = df[coluna_data].dt.day
    df["data_formatada"] = df[coluna_data].dt.strftime("%d/%m/%Y")

    return df


def mostrar_dias_livres(mes_numero, mes_nome):
    df_mes = carregar_dados_mes(mes_numero)

    st.markdown(f"## {mes_nome}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if df_mes is None:
            qtd_dias = 0
        else:
            df_mes = df_mes.sort_values("dia")
            qtd_dias = len(df_mes)

        st.markdown(
            f"""
            <div class="metric-card">
                <h3>Dias livres</h3>
                <h1>{qtd_dias}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Datas disponiveis")

        if df_mes is None:
            st.markdown(
                f'<div class="aviso">Arquivo nao encontrado: data/dias_livres_{mes_numero}.csv</div>',
                unsafe_allow_html=True
            )
        elif df_mes.empty:
            st.markdown(
                '<div class="aviso">Nenhum dia livre encontrado para este mes.</div>',
                unsafe_allow_html=True
            )
        else:
            dias_html = ""

            for _, row in df_mes.iterrows():
                dias_html += f'<span class="dia-livre">{row["data_formatada"]}</span>'

            st.markdown(dias_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        caminho_grafico = ASSETS_DIR / f"compromissos_{mes_numero}.png"

        st.markdown("### Grafico de compromissos do mes")

        if caminho_grafico.exists():
            st.image(str(caminho_grafico), use_container_width=True)
        else:
            st.markdown(
                f"""
                <div class="aviso">
                    Grafico nao encontrado em: assets/compromissos_{mes_numero}.png
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# DASHBOARD
# =========================
st.title("📅 Dashboard de Disponibilidade para Reunioes")

st.markdown(
    """
    Este dashboard mostra os dias disponiveis para marcar reunioes nos meses de
    **maio, junho e julho**, junto com o grafico de compromissos de cada mes.
    """
)

abas = st.tabs(["Maio", "Junho", "Julho"])

for aba, (mes_numero, mes_nome) in zip(abas, MESES.items()):
    with aba:
        mostrar_dias_livres(mes_numero, mes_nome)
