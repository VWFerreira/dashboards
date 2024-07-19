import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# Função para carregar dados do Google Sheets CSV
def load_data(url):
    return pd.read_csv(url)

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

# Carregar e redimensionar a imagem
imagem2 = Image.open("image/trers.png")
imagem2 = imagem2.resize((250, 200))

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
    .text {
        display: flex;
        align-items: left;
        font-size: 50px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)

# Layout com colunas
col1, col3 = st.columns([9, 9])

with col1:
    st.markdown('<div class="images">', unsafe_allow_html=True)
    st.image(imagem2, caption=None, use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="text">Contrato Correios</div>', unsafe_allow_html=True)

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

# Limpar valores na coluna "DATA FINALIZADO" formatando as datas corretamente
data["DATA FINALIZADO"] = pd.to_datetime(
    data["DATA FINALIZADO"], format="%d/%m/%Y", errors="coerce"
)

# Adicionar coluna "DATA RECEBIDO" formatando corretamente
data["DATA RECEBIDO"] = pd.to_datetime(
    data["DATA RECEBIDO"], format="%d/%m/%Y", errors="coerce"
)

# Filtrar dados para os anos de 2023 e 2024 e calcular valor orçado por mês
data["Ano"] = data["DATA FINALIZADO"].dt.year
data["Mes"] = data["DATA FINALIZADO"].dt.strftime("%B")
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

# Definir o esquema de cores personalizado
color_scheme = ["#A9A9A9", "#87CEEB", "#66CDAA", "#F0F8FF", "#B0E0E6"]

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
            scale=alt.Scale(range=color_scheme)
        ),
        tooltip=["Ano", "Mes", "VALOR ORÇADO"],
    )
    .properties(width=600, height=400, title="Valor Orçado por Mês em 2023 e 2024")
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
            scale=alt.Scale(range=color_scheme)
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
            title="Status",
            scale=alt.Scale(range=color_scheme),
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
            title="Disciplina",
            scale=alt.Scale(range=color_scheme),
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
            "Orçamentista:N", title="Orçamentista", scale=alt.Scale(range=color_scheme)
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
        color=alt.Color(field="Orçamentista", type="nominal", scale=alt.Scale(range=color_scheme)),
        tooltip=["Orçamentista", "Quantidade"],
    )
    .properties(
        width=400, height=400, title="Distribuição de Orçamentos por Orçamentista"
    )
)

# Estilos CSS personalizados para métricas e botões
metric_css = """
    <style>
    .metric-label {
        font-size: 15px;
        font-weight: bold;
        text-align: center;
        font-family: Arial Narrow, sans-serif;
    }
    .metric-value {
        font-size: 18px;
        font-weight: bold;
        color: #FFFF00;
        text-align: center;
        font-family: Arial Narrow, sans-serif;
        font-weight: bold;
    }
    .custom-button {
        display: block;
        width: 100%;
        padding: 10px;
        font-size: 18px;
        text-align: center;
        color: white;
        background-color: #4CAF50;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-family: Arial Narrow, sans-serif;
    }
    .custom-button:hover {
        background-color: #FFFF00;
    }
    </style>
"""

# Inserir CSS personalizado na página
st.markdown(metric_css, unsafe_allow_html=True)

# Layout com gráfico de status na primeira linha
st.write("### Distribuição de Status")
st.altair_chart(chart3, use_container_width=True)

# Layout com métricas na segunda linha
metric_columns = st.columns(len(status_grouped_data) + 1)

# Adicionar métrica para total de OS
with metric_columns[0]:
    st.markdown("<div class='metric-label'>Total OS</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{total_os}</div>", unsafe_allow_html=True)

# Adicionar métricas de status com botões
for idx, row in status_grouped_data.iterrows():
    with metric_columns[idx + 1]:
        st.markdown(
            f"<div class='metric-label'>{row['Status']}</div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='metric-value'>{row['Quantidade']}</div>",
            unsafe_allow_html=True,
        )

        if st.button(row["Status"], key=f"btn_{row['Status']}"):
            status_filtered_data = data_filtered_os[
                data_filtered_os["STATUS*"] == row["Status"]
            ]
            st.write(f"Tabela - {row['Status']}")
            st.write(status_filtered_data)

# Layout com gráfico de valor orçado por status
st.write("---")
col1, col2, col3 = st.columns([1, 4, 1])

# Selectbox para escolher o status
status_options = data["STATUS*"].unique()
selected_status = col1.selectbox("Selecione o Status", status_options)

# Filtrar os dados com base no status selecionado
filtered_data_status = data[data["STATUS*"] == selected_status]

# Agrupar dados por ano e mês para o status selecionado
grouped_data_status = (
    filtered_data_status.groupby(["Ano", "Mes"])["VALOR ORÇADO"].sum().reset_index()
)

# Ordenar os meses
grouped_data_status["Mes"] = pd.Categorical(
    grouped_data_status["Mes"],
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
grouped_data_status = grouped_data_status.sort_values(["Ano", "Mes"])

# Criar gráfico de barras com Altair para o status selecionado
chart_status = (
    alt.Chart(grouped_data_status)
    .mark_bar()
    .encode(
        x=alt.X("Mes:N", title="Mês"),
        y=alt.Y("VALOR ORÇADO:Q", title="Valor Orçado"),
        color=alt.Color(
            "Ano:N",
            title="Ano",
            scale=alt.Scale(range=color_scheme)
        ),
        tooltip=["Ano", "Mes", "VALOR ORÇADO"],
    )
    .properties(
        width=600,
        height=400,
        title=f"Valor Orçado por Mês para Status '{selected_status}' em 2023 e 2024",
    )
)

col2.altair_chart(chart_status, use_container_width=True)

# Calcular métrica para o status selecionado
total_valor_orcado_status = filtered_data_status["VALOR ORÇADO"].sum()

with col3:
    st.markdown(
        f"<div class='metric-label'>Total Valor Orçado ({selected_status})</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='metric-value'>{total_valor_orcado_status:.2f}</div>",
        unsafe_allow_html=True,
    )

# Layout com gráficos e tabelas
st.write("---")
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

st.write("---")
col7, col8 = st.columns([5, 1])

with col7:
    st.altair_chart(chart4, use_container_width=True)

with col8:
    show_table4 = st.checkbox("Mostrar Tabela 4", key="table4_checkbox")
    if show_table4:
        st.write(disciplinas_grouped_data)

st.write("---")
col9, col10 = st.columns([3, 5])

with col9:
    st.altair_chart(chart6, use_container_width=True)

with col10:
    st.altair_chart(chart5, use_container_width=True)

# Filtrar dados pelos status "APROVADO", "RECEBIDO" e "EXECUÇÃO"
filtered_status_data = data_filtered_os[
    data_filtered_os["STATUS*"].isin(["APROVADO", "RECEBIDO", "EXECUÇÃO"])
]

# Agrupar dados por status, disciplinas, descrição do serviço, previsão de início, previsão de finalização e observação
grouped_status_data = (
    filtered_status_data.groupby(
        [
            "STATUS*",
            "DISCIPLINAS",
            "DESCRIÇÃO DO SERVIÇO",
            "PREVISÃO DE INÍCIO",
            "PREVISÃO DE FINALIZAÇÃO",
            "OBSERVAÇÃO",
        ]
    )
    .size()
    .reset_index(name="Quantidade")
)
st.write("---")
# Mostrar tabela totalizada
st.write("Tabela Total dos Status 'APROVADO', 'RECEBIDO' e 'EXECUÇÃO'")
st.write(grouped_status_data)

# Segunda tabela com os dados filtrados por status "APROVADO", "RECEBIDO" e "EXECUÇÃO"
st.write("### Segunda Tabela dos Status 'APROVADO', 'RECEBIDO' e 'EXECUÇÃO'")
second_table = filtered_status_data[[
    "STATUS*",
    "DISCIPLINAS",
    "DESCRIÇÃO DO SERVIÇO",
    "DATA RECEBIDO"
]].reset_index(drop=True)

st.write(second_table)

