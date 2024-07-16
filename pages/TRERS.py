import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from PIL import Image
import unicodedata

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

# Carregar imagens
imagem2 = Image.open("./image/trers.png")

# Reduzir o tamanho das imagens

imagem2 = imagem2.resize((250, 150))

# Definir estilo customizado
st.markdown(
    """
    <style>
    .container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .images {
        display: flex;
        gap: 10px;
    }
    .images img {
        width: 150px;
        height: 150px;
        animation: spin 5s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Layout com colunas
col1, col2 = st.columns([1, 1])

with col2:
    st.subheader("Contrato TRERS")

with col1:
    st.image(imagem2, caption=None, use_column_width=False)
    st.markdown("</div>", unsafe_allow_html=True)


# Função para carregar dados com cache de 60 segundos
@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)


# Carregar dados do Google Sheets CSV
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2Ql1eYWomSTjyQrylSBJ2tHgslpJEmA3iXrxJWTyJMNSkYRauZrJisIgEi1wT9D4Uu7S0Eyo04Xq3/pub?gid=1846942667&single=true&output=csv"
data = load_data(url)

# Limpar valores na coluna "VALOR ORÇADO" removendo pontuação, símbolos de moeda e espaços
data["VALOR ORÇADO"] = (
    data["VALOR ORÇADO"]
    .str.replace(r"[^\d,]", "", regex=True)
    .str.replace(",", ".")
    .astype(float)
)

# Limpar valores na coluna "DATA ORÇADO" formatando as datas corretamente
data["DATA ORÇADO"] = pd.to_datetime(
    data["DATA ORÇADO"], format="%d/%m/%Y", errors="coerce"
)

# Filtrar dados para os anos de 2023 e 2024 e calcular valor orçado por mês
data["Ano"] = data["DATA ORÇADO"].dt.year
data["Mes"] = data["DATA ORÇADO"].dt.strftime("%B")
data_filtered = data[(data["Ano"] == 2023) | (data["Ano"] == 2024)]

# Agrupar dados por ano e mês
grouped_data = data_filtered.groupby(["Ano", "Mes"])["VALOR ORÇADO"].sum().reset_index()

# Ordenar os meses
grouped_data["Mes"] = pd.Categorical(
    grouped_data["Mes"],
    categories=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
    ordered=True,
)
grouped_data = grouped_data.sort_values(["Ano", "Mes"])

# Criar gráfico de barras com Altair
chart1 = (
    alt.Chart(grouped_data)
    .mark_bar()
    .encode(
        x=alt.X("Mes:N", title="Mês"),
        y=alt.Y("VALOR ORÇADO:Q", title="Valor Orçado"),
        color=alt.Color(
            "Ano:N",
            title="Ano",
            scale=alt.Scale(
                domain=[2023, 2024],
                range=[
                    "#8B0000",
                    "#00FF00",
                ],
            ),
        ),
        tooltip=["Ano", "Mes", "VALOR ORÇADO"],
    )
    .properties(width=600, height=400, title="Valor Orçado por Mês em 2023 e 2024")
)

# Adicionar coluna "DATA RECEBIDO" formatando corretamente
data["DATA RECEBIDO"] = pd.to_datetime(
    data["DATA RECEBIDO"], format="%d/%m/%Y", errors="coerce"
)

# Filtrar dados para os anos de 2023 e 2024
data_filtered_os = data[
    (data["DATA RECEBIDO"].dt.year == 2023) | (data["DATA RECEBIDO"].dt.year == 2024)
]

# Agrupar dados por dia
os_grouped_data = (
    data_filtered_os.groupby(["DATA RECEBIDO"]).size().reset_index(name="Quantidade OS")
)
os_grouped_data["Ano"] = os_grouped_data["DATA RECEBIDO"].dt.year

# Criar gráfico de barras para Quantidade de OS Recebidas por Dia
chart2 = (
    alt.Chart(os_grouped_data)
    .mark_bar()
    .encode(
        x=alt.X("DATA RECEBIDO:T", title="Data Recebido"),
        y=alt.Y("Quantidade OS:Q", title="Quantidade de OS"),
        color=alt.Color(
            "Ano:N",
            title="Ano",
            scale=alt.Scale(domain=[2023, 2024], range=["#00FF00", "#1E90FF"]),
        ),
        tooltip=["DATA RECEBIDO", "Quantidade OS"],
    )
    .properties(
        width=600, height=400, title="Quantidade de OS Recebidas por Dia (2023 e 2024)"
    )
)

# Criar métrica com total de OS
total_os = os_grouped_data["Quantidade OS"].sum()

# Gráfico de colunas para Distribuição de Status
status_grouped_data = data_filtered_os["STATUS*"].value_counts().reset_index()
status_grouped_data.columns = ["Status", "Quantidade"]

chart3 = (
    alt.Chart(status_grouped_data)
    .mark_bar()
    .encode(
        x=alt.X("Status:N", title="Status"),
        y=alt.Y("Quantidade:Q", title="Quantidade"),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(
                range=["#1E90FF", "#6A5ACD", "#8B0000", "#FFFF00", "#A8DADC", "#00FF00"]
            ),
        ),
        tooltip=["Status", "Quantidade"],
    )
    .properties(width=600, height=400, title="Distribuição de Status")
)

# Gráfico de colunas para Distribuição de Disciplinas
disciplinas_grouped_data = data_filtered_os["DISCIPLINAS"].value_counts().reset_index()
disciplinas_grouped_data.columns = ["Disciplina", "Quantidade"]

chart4 = (
    alt.Chart(disciplinas_grouped_data)
    .mark_bar()
    .encode(
        x=alt.X("Disciplina:N", title="Disciplina"),
        y=alt.Y("Quantidade:Q", title="Quantidade"),
        color=alt.Color(
            "Disciplina:N",
            scale=alt.Scale(
                range=["#1E90FF", "#6A5ACD", "#8B0000", "#FFFF00", "#A8DADC", "#00FF00"]
            ),
        ),
        tooltip=["Disciplina", "Quantidade"],
    )
    .properties(width=600, height=400, title="Distribuição de Disciplinas")
)

# Agrupar dados por orçamentista e mês
orcamentista_data = (
    data_filtered.groupby(["ORÇAMENTISTA", "Mes"])["VALOR ORÇADO"].count().reset_index()
)
orcamentista_data.columns = ["Orçamentista", "Mês", "Quantidade"]

# Gráfico de barras para orçamentista e mês
chart5 = (
    alt.Chart(orcamentista_data)
    .mark_bar()
    .encode(
        x=alt.X("Mês:N", title="Mês"),
        y=alt.Y("Quantidade:Q", title="Quantidade de Orçamentos"),
        color=alt.Color(
            "Orçamentista:N", title="Orçamentista", scale=alt.Scale(scheme="tableau20")
        ),
        tooltip=["Orçamentista", "Mês", "Quantidade"],
    )
    .properties(width=600, height=400, title="Orçamentos por Mês por Orçamentista")
)

# Gráfico de pizza para distribuição total de orçamentos por orçamentista
total_orcamentista_data = data_filtered["ORÇAMENTISTA"].value_counts().reset_index()
total_orcamentista_data.columns = ["Orçamentista", "Quantidade"]

chart6 = (
    alt.Chart(total_orcamentista_data)
    .mark_arc()
    .encode(
        theta=alt.Theta(field="Quantidade", type="quantitative"),
        color=alt.Color(field="Orçamentista", type="nominal"),
        tooltip=["Orçamentista", "Quantidade"],
    )
    .properties(
        width=400, height=400, title="Distribuição de Orçamentos por Orçamentista"
    )
)

# Layout com gráficos e tabelas
col1, col2 = st.columns([1, 6])

with col1:
    show_table1 = st.checkbox("Tabela Dados", key="table1_checkbox")
    if show_table1:
        st.write(grouped_data[["Ano", "Mes", "VALOR ORÇADO"]])

with col2:
    st.altair_chart(chart1, use_container_width=True)

st.write("---")
col3, col4 = st.columns([5, 1])

with col3:
    st.altair_chart(chart2, use_container_width=True)

with col4:
    show_table2 = st.checkbox("Mostrar Tabela 2", key="table2_checkbox")
    if show_table2:
        st.write(os_grouped_data)
    st.metric(label="Total de OS Recebidas", value=total_os)

st.write("---")
status_columns = st.columns(len(status_grouped_data))

for idx, row in status_grouped_data.iterrows():
    status_columns[idx].metric(label=row["Status"], value=row["Quantidade"])

st.write("---")
col7, col8 = st.columns([5, 1])

with col7:
    st.altair_chart(chart4, use_container_width=True)

with col8:
    show_table4 = st.checkbox("Mostrar Tabela 4", key="table4_checkbox")
    if show_table4:
        st.write(disciplinas_grouped_data)

st.write("---")
col9, col10 = st.columns([1, 5])

with col9:
    st.altair_chart(chart6, use_container_width=True)

with col10:
    st.altair_chart(chart5, use_container_width=True)

