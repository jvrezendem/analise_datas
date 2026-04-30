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

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
ANO_DASHBOARD = 2026

MESES = {
    5: {"nome": "Maio", "arquivo": "maio"},
    6: {"nome": "Junho", "arquivo": "junho"},
    7: {"nome": "Julho", "arquivo": "julho"}
}


def identificar_coluna_dia(df):
    for coluna in ["dia", "dias_livres", "dia_livre", "data", "data_livre", "data_compromisso"]:
        if coluna in df.columns:
            return coluna
    return df.columns[0]


def extrair_dia(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto == "":
        return pd.NA

    numero = pd.to_numeric(texto, errors="coerce")

    # Se vier apenas o dia do mes, inclusive como 1.0, 2.0, 15.0 etc.
    if pd.notna(numero) and 1 <= int(numero) <= 31:
        return int(numero)

    # Se vier uma data completa ou parcial, usa apenas o DIA dela.
    data = pd.to_datetime(texto, dayfirst=True, errors="coerce")

    if pd.notna(data):
        return data.day

    return pd.NA


@st.cache_data
def carregar_dados_mes(mes_numero):
    data_path = DATA_DIR / f"dias_livres_{mes_numero}.csv"

    if not data_path.exists():
        return None

    df = pd.read_csv(data_path)
    coluna_dia = identificar_coluna_dia(df)

    df["dia"] = df[coluna_dia].apply(extrair_dia)
    df = df.dropna(subset=["dia"])
    df["dia"] = df["dia"].astype(int)

    # Monta manualmente: DIA vindo do CSV + MES do arquivo + ANO 2026.
    # Assim o dashboard fica consistente com o grafico correspondente ao mes.
    df["data_completa"] = pd.to_datetime(
        {
            "year": ANO_DASHBOARD,
            "month": mes_numero,
            "day": df["dia"]
        },
        errors="coerce"
    )

    df = df.dropna(subset=["data_completa"])
    df = df.sort_values("data_completa")

    df["mes"] = mes_numero
    df["data_formatada"] = df["data_completa"].dt.strftime("%d/%m/%Y")

    return df


def mostrar_dias_livres(mes_numero, mes_info):
    mes_nome = mes_info["nome"]
    mes_arquivo = mes_info["arquivo"]
    df_mes = carregar_dados_mes(mes_numero)

    st.markdown(f"## {mes_nome}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        qtd_dias = 0 if df_mes is None else len(df_mes)

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

        caminho_grafico = ASSETS_DIR / f"compromissos_{mes_arquivo}.png"

        st.markdown("### Grafico de compromissos do mes")

        if caminho_grafico.exists():
            st.image(str(caminho_grafico), use_container_width=True)
        else:
            st.markdown(
                f"""
                <div class="aviso">
                    Grafico nao encontrado em: assets/compromissos_{mes_arquivo}.png
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)


st.title("📅 Dashboard de Disponibilidade para Reunioes")

st.markdown(
    """
    Este dashboard mostra os dias disponiveis para marcar reunioes nos meses de
    **maio, junho e julho de 2026**, junto com o grafico de compromissos de cada mes.
    """
)

abas = st.tabs(["Maio", "Junho", "Julho"])

for aba, (mes_numero, mes_info) in zip(abas, MESES.items()):
    with aba:
        mostrar_dias_livres(mes_numero, mes_info)
