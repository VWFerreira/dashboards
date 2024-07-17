import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

# Carregar imagens
imagem1 = Image.open("./image/genn.png")
imagem2 = Image.open("./image/sop.png")

# Reduzir o tamanho das imagens
imagem1 = imagem1.resize((200, 200))
imagem2 = imagem2.resize((350, 200))

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
    """, unsafe_allow_html=True
)

# Layout com colunas
col1, col3 = st.columns([2, 4,])

with col3:
    st.title("Contratos Secretária de Obras RS")
with col1:
    st.image(imagem2, caption=None, use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

# Função para carregar dados de uma URL CSV
@st.cache_data(ttl=60)
def load_data(url):
    data = pd.read_csv(url)
    return data

# URLs dos CSVs
urls = {
    "data1": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqArKQaOEijehSgxrnDUh7Pyo4VBM8ILxPnlcKTGy1zOaDS17C-2jQODUjBlhu2cEIJG59Euq0GQ5D/pub?gid=636293343&single=true&output=csv",
    "data2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqArKQaOEijehSgxrnDUh7Pyo4VBM8ILxPnlcKTGy1zOaDS17C-2jQODUjBlhu2cEIJG59Euq0GQ5D/pub?gid=1758648028&single=true&output=csv",
    "data3": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqArKQaOEijehSgxrnDUh7Pyo4VBM8ILxPnlcKTGy1zOaDS17C-2jQODUjBlhu2cEIJG59Euq0GQ5D/pub?gid=607349672&single=true&output=csv",
    "data4": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqArKQaOEijehSgxrnDUh7Pyo4VBM8ILxPnlcKTGy1zOaDS17C-2jQODUjBlhu2cEIJG59Euq0GQ5D/pub?gid=1784106199&single=true&output=csv",
}

# Carregar os dados de todas as URLs
data = {key: load_data(url) for key, url in urls.items()}

# Converter colunas relevantes para strings para garantir que sejam exibidas corretamente
for col in ["V.TOTAL LOTE 1", "V.TOTAL LOTE 4", "SALDO LOTE 1", "SALDO LOTE 4"]:
    data["data1"][col] = data["data1"][col].astype(str)

# Limpeza dos dados do segundo conjunto de dados
expected_columns = [
    "ETAPA 1 (CR.F.FINANCEIRO) 30 DIAS",
    "ETAPA 2 (CR.F.FINANCEIRO) 60 DIAS",
    "ETAPA 3 (CR.F.FINANCEIRO) 90 DIAS",
    "ETAPA 4 (CR.F.FINANCEIRO) 120 DIAS",
    "ETAPA 5 (CR.F.FINANCEIRO) 150 DIAS",
    "ETAPA 6 (CR.F.FINANCEIRO) 180 DIAS",
    "VALOR DO CONTRATO",
]

for col in expected_columns:
    if col in data["data2"].columns:
        data["data2"][col] = (
            data["data2"][col].replace("[R$ ,]", "", regex=True).astype(float)
        )

# Limpeza e conversão dos dados do terceiro conjunto de dados
def clean_and_convert(value):
    if isinstance(value, str) and "TOTAL" in value:
        return None
    try:
        return float(value.replace("R$", "").replace(".", "").replace(",", ".").strip())
    except (ValueError, AttributeError):
        return 0.0

# Extração e soma das colunas mensais
monthly_columns = [
    "MEDIÇÃO JUNHO",
    "MEDIÇÃO JULHO",
    "MEDIÇÃO AGOSTO",
    "MEDIÇÃO SETEMBRO",
    "MEDIÇÃO OUTUBRO",
    "MEDIÇÃO NOVEMBRO",
    "MEDIÇÃO DEZEMBRO",
]

monthly_totals = {}
for month in monthly_columns:
    data["data3"][month] = data["data3"][month].apply(clean_and_convert)
    # Filtrar valores None que representam linhas 'TOTAL'
    filtered_data = data["data3"][month].dropna()
    monthly_totals[month] = filtered_data.sum()

# Função para carregar CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Função principal do Streamlit
def sopoat():
    # Carregar CSS local
    local_css("./css/ois.css")

    # Título e subtítulo da página
    
    st.subheader("Ordem de Inicio de Serviços - OIS")

    # Layout da página para métricas
    st.write("## Métricas")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
                <div style="font-size: 16px; text-align: center;">V.TOTAL LOTE 1</div>
                <div style="color: #00FF00; font-size: 14px; text-align: center;">{data['data1']['V.TOTAL LOTE 1'].iloc[0]}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
                <div style="font-size: 16px; text-align: center;">SALDO LOTE 1</div>
                <div style="color: yellow; font-size: 14px; text-align: center;">{data['data1']['SALDO LOTE 1'].iloc[0]}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
                <div style="font-size: 16px; text-align: center;">V.TOTAL LOTE 4</div>
                <div style="color: #00FF00; font-size: 14px; text-align: center;">{data['data1']['V.TOTAL LOTE 4'].iloc[0]}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
                <div style="font-size: 16px; text-align: center;">SALDO LOTE 4</div>
                <div style="color: yellow; font-size: 14px; text-align: center;">{data['data1']['SALDO LOTE 4'].iloc[0]}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Opcional: Exibir a tabela de dados brutos
    if st.checkbox("Mostrar dados brutos - Métricas", key="metrics_raw"):
        st.write(data["data1"])
    st.write("---")

    # Layout da página para gráficos interativos
    st.subheader("Visualização de Dados")

    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        st.markdown(
            """
            <h5 style="text-align: right; color: #45a049;font-size: 12px;">
                Filtrar por Escola
            </h5>
            """,
            unsafe_allow_html=True,
        )
        unique_predios = data["data2"]["PREDIO"].unique().tolist()
        unique_predios.insert(0, "Todos")
        selected_predio = st.selectbox("Selecione Escola", unique_predios)

    # Filtre os dados pelo prédio selecionado
    if selected_predio == "Todos":
        filtered_data = data["data2"]
    else:
        filtered_data = data["data2"][data["data2"]["PREDIO"] == selected_predio]

    # Verifique os dados filtrados
    st.write("### Dados Filtrados", filtered_data)

    with col2:
        st.write("### Gráfico de Etapas Financeiras")
        if not filtered_data.empty:
            # Adiciona uma coluna 'Etapa' para identificar as etapas financeiras
            melted_data = filtered_data.melt(
                id_vars=["ID", "Nº CONTRATO", "STATUS"],
                value_vars=[
                    col for col in expected_columns if col in filtered_data.columns
                ],
                var_name="Etapa",
                value_name="Valor",
            )

            # Definir as cores para os status
            color_scale = alt.Scale(domain=expected_columns, range=["#6A5ACD", "#FFFF00", "#D2691E", "#008000", "#00FF00", "#8B0000", "#F5FFFA", "#FFA500"])

            chart = (
                alt.Chart(melted_data)
                .mark_bar()
                .encode(
                    x="Etapa:N",
                    y="Valor:Q",
                    color=alt.Color("Etapa:N", scale=color_scale),
                    tooltip=["Nº CONTRATO", "Etapa", "Valor", "STATUS"],
                )
                .interactive()
            )

            st.altair_chart(chart, use_container_width=True)

    with col3:
        if not filtered_data.empty:
            total_contrato = filtered_data["VALOR DO CONTRATO"].sum()
            st.write("Total contrato:", total_contrato)

    # Opcional: Exibir a tabela de dados brutos
    if st.checkbox("Mostrar dados brutos - Visualização", key="visualization_raw"):
        st.write(data["data2"])

    st.write("---")

    # Métricas dos dados do terceiro conjunto
    st.write("Medição 2024 || Prévia:")

    cols = st.columns(len(monthly_columns))

    for i, (month, total) in enumerate(monthly_totals.items()):
        col_name = f"{month}"
        with cols[i]:
            st.markdown(
                f"""
                <div style="font-size: 16px; text-align: center; margin-bottom: 20px;">
                    <div style=" font-size: 16px;">{col_name}</div>
                    <div style="color:  #00FF00; font-size: 14px;">R$ {total:,.2f}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    if st.checkbox("Mostrar dados brutos - Medições", key="mediciones_raw"):
        st.write(data["data3"])

    # Ensure the 'STATUS' column is clean and properly formatted
    data["data4"]["STATUS"] = data["data4"]["STATUS"].str.strip()

    # Define the possible status values
    status_enum = [
        "RECEBIDO",
        "EM ORÇAMENTO",
        "CANCELADO",
        "VISTORIA",
        "CORREÇÃO ORÇAMENTO",
        "APROVADO",
        "ENVIADO",
    ]

    # Filter the data to only include the defined status values
    data["data4"] = data["data4"][data["data4"]["STATUS"].isin(status_enum)]

    # Group data by status and count occurrences
    status_count = (
        data["data4"]["STATUS"]
        .value_counts()
        .reindex(status_enum, fill_value=0)
        .reset_index()
    )
    status_count.columns = ["Status", "Count"]

    # Display the metrics side by side
    st.markdown(
        "<h3 style='text-align: center;'>Status OAT</h3>", unsafe_allow_html=True
    )

    cols = st.columns(len(status_enum))
    for idx, (status, count) in status_count.iterrows():
        with cols[idx]:
            st.markdown(
                f"""
                <div style="font-size: 16px; text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 16px;">{status}</div>
                    <div style="color: #00FF00; font-size: 14px;">{count}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.write("---")

    # Novo gráfico de status com filtro de PREDIO
    st.subheader("Gráfico de Status por PREDIO")

    col1, col2 = st.columns([1, 4])

    with col1:
        unique_predios_status = data["data4"]["PREDIO"].unique().tolist()
        unique_predios_status.insert(0, "Todos")
        selected_predio_status = st.selectbox("Selecione PREDIO", unique_predios_status, key="status_predio")

    if selected_predio_status == "Todos":
        filtered_data_status = data["data4"]
    else:
        filtered_data_status = data["data4"][data["data4"]["PREDIO"] == selected_predio_status]

    with col2:
        if not filtered_data_status.empty:
            # Agrupar dados por status e contar ocorrências
            status_count_filtered = filtered_data_status["STATUS"].value_counts().reset_index()
            status_count_filtered.columns = ["Status", "Count"]

            # Definir as cores para os status
            color_scale = alt.Scale(domain=status_enum, range=["#6A5ACD", "#FFFF00", "#D2691E", "#008000", "#00FF00", "#8B0000", "#F5FFFA", "#FFA500"])

            # Criar gráfico de barras coloridas
            chart_status = (
                alt.Chart(status_count_filtered)
                .mark_bar()
                .encode(
                    x=alt.X("Status:N", title="Status"),
                    y=alt.Y("Count:Q", title="Quantidade"),
                    color=alt.Color("Status:N", scale=color_scale),
                    tooltip=["Status", "Count"],
                )
                .properties(width=600)
            )

            st.altair_chart(chart_status, use_container_width=True)

        st.write("### Dados Filtrados por PREDIO")
        st.write(filtered_data_status)

    st.write("---")

    # Gráficos de pizza para LOTE e MUNICÍPIO
    st.subheader("Gráficos de Pizza")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Gráfico de Pizza por LOTE")
        lote_count = data["data4"]["LOTE"].value_counts().reset_index()
        lote_count.columns = ["Lote", "Count"]

        chart_lote = (
            alt.Chart(lote_count)
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Lote", type="nominal", scale=alt.Scale(range=["#FFFF00", "#D2691E", "#008000"])),
                tooltip=["Lote", "Count"],
            )
        )

        st.altair_chart(chart_lote, use_container_width=True)

    with col2:
        municipio_count = data["data4"]["MUNICIPIO"].value_counts().reset_index()
        municipio_count.columns = ["Município", "Count"]

        chart_municipio = (
            alt.Chart(municipio_count)
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Município", type="nominal", scale=alt.Scale(range=["#FFFF00", "#D2691E", "#008000"])),
                tooltip=["Município", "Count"],
            )
        )

        st.altair_chart(chart_municipio, use_container_width=True)

if __name__ == "__main__":
    sopoat()
