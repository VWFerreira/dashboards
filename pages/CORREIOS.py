import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from PIL import Image

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

# Carregar e redimensionar a imagem
imagem2 = Image.open("./image/corr.png")
imagem2 = imagem2.resize((200, 200))

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

# Função para carregar dados com cache de 60 segundos
@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

# Carregar dados do Google Sheets CSV
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTfXp-_Anw2MhzZAfBhLrITSzXy_AVm-K81tFSRLz4xBhuWq7KIdYDFqtdJZ9zGOJpV32H4qPeJ4BrD/pub?gid=1596975483&single=true&output=csv"
data = load_data(url)

# Remover espaços em branco ao redor dos nomes das colunas
data.columns = data.columns.str.strip()

# Converter colunas de datas para o formato datetime
data['DATA RECEBIDO'] = pd.to_datetime(data['DATA RECEBIDO'], format='%d/%m/%Y', errors='coerce')
data['DATA ORÇADO'] = pd.to_datetime(data['DATA ORÇADO'], format='%d/%m/%Y', errors='coerce')
data['DATA EXECUÇÃO (INÍCIO)'] = pd.to_datetime(data['DATA EXECUÇÃO (INÍCIO)'], format='%d/%m/%Y', errors='coerce')
data['DATA FINALIZADO'] = pd.to_datetime(data['DATA FINALIZADO'], format='%d/%m/%Y', errors='coerce')

# Remover espaços em branco ao redor dos valores nas colunas de interesse
data['ORÇAMENTISTA'] = data['ORÇAMENTISTA'].str.strip()
data['STATUS*'] = data['STATUS*'].str.strip()

# Gráfico de Altair para quantidade de OS recebidas por dia em 2023 e 2024
os_counts = data[data['DATA RECEBIDO'].dt.year.isin([2023, 2024])].groupby([data['DATA RECEBIDO'].dt.date.rename('Data'), data['DATA RECEBIDO'].dt.year.rename('Ano')]).size().reset_index(name='Contagem')

col15, col16 = st.columns([3, 1])

with col16:
    # Exibir a métrica total de OS recebidas
    total_os_2023 = os_counts[os_counts['Ano'] == 2023]['Contagem'].sum()
    total_os_2024 = os_counts[os_counts['Ano'] == 2024]['Contagem'].sum()
    total_os = total_os_2023 + total_os_2024

    st.metric(label="Total de OS Recebidas", value=total_os)

with col15:
    line_chart = alt.Chart(os_counts).mark_line().encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Contagem:Q', title='Quantidade de OS Recebidas'),
        color=alt.Color('Ano:N', title='Ano')
    ).properties(
        width=1000,
        height=400
    )
    
    st.subheader("Quantidade de OS Recebidas por Dia (2023 e 2024)")
    st.altair_chart(line_chart, use_container_width=True)

    st.write("---")
        
# Agrupar dados pela coluna STATUS* e contar ocorrências
status_counts = data['STATUS*'].value_counts().reset_index()
status_counts.columns = ['STATUS*', 'Contagem']

# Criar gráfico de barras usando Altair baseado na coluna STATUS*
status_chart = alt.Chart(status_counts).mark_bar().encode(
    x=alt.X('STATUS*:N', title='Status'),
    y=alt.Y('Contagem:Q', title='Contagem'),
    color=alt.Color('STATUS*:N', legend=alt.Legend(title="Status")),
    tooltip=['STATUS*', 'Contagem']
).properties(
    title='Distribuição de Status'
)

# Adicionar rótulos de contagem sobre as barras
text = status_chart.mark_text(
    align='center',
    baseline='middle',
    dy=-10  # Deslocar texto para cima das barras
).encode(
    text='Contagem:Q'
)

# Combinar gráfico de barras e rótulos de texto
final_chart = (status_chart + text).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16
)

# Exibir o gráfico
st.write("## Distribuição de Status")
st.altair_chart(final_chart, use_container_width=True)

# Inicializar estado da sessão para controlar a visibilidade da tabela
if 'show_table' not in st.session_state:
    st.session_state.show_table = False

# Função para alternar a visibilidade da tabela
def toggle_table():
    st.session_state.show_table = not st.session_state.show_table

# Botão para alternar a tabela
if st.button('Mostrar/Ocultar Tabela de Dados', key='toggle_table'):
    toggle_table()

# Mostrar ou ocultar a tabela com base no estado
if st.session_state.show_table:
    st.write("## Dados")
    st.dataframe(data)

# Adicionar separador
st.write("---")

# Criar gráfico de barras usando Altair baseado na coluna DISCIPLINAS
disciplina_counts = data['DISCIPLINAS'].value_counts().reset_index()
disciplina_counts.columns = ['DISCIPLINAS', 'Contagem']

disciplina_chart = alt.Chart(disciplina_counts).mark_bar().encode(
    x=alt.X('DISCIPLINAS:N', title='Disciplinas'),
    y=alt.Y('Contagem:Q', title='Contagem'),
    color=alt.Color('DISCIPLINAS:N', legend=alt.Legend(title="Disciplinas")),
    tooltip=['DISCIPLINAS', 'Contagem']
).properties(
    title='Distribuição de Disciplinas'
)

# Adicionar rótulos de contagem sobre as barras
disciplina_text = disciplina_chart.mark_text(
    align='center',
    baseline='middle',
    dy=-10  # Deslocar texto para cima das barras
).encode(
    text='Contagem:Q'
)

# Combinar gráfico de barras e rótulos de texto
final_disciplina_chart = (disciplina_chart + disciplina_text).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16
)

# Exibir o gráfico de disciplinas
st.write("## Distribuição de Disciplinas")
st.altair_chart(final_disciplina_chart, use_container_width=True)

# Filtrar dados pelos diferentes status
status_list = ["ORÇADO RECEBIDO", "SOLICITAÇÃO DE MATERIAL", "COMPRAS", "EXECUÇÃO", "LEVANTAMENTO", "RECEBIDO", "FINALIZADO E ASSINADO"]

# Contar a quantidade de disciplinas para cada status
status_counts = {status: data[data['STATUS*'] == status].shape[0] for status in status_list}

# Contar a quantidade total de disciplinas com base na coluna ID
total_disciplines = data['ID'].nunique()
completed_disciplines = data[data['STATUS*'] == "EXECUÇÃO"]['ID'].nunique()
remaining_disciplines = total_disciplines - completed_disciplines

# Adicionar CSS para personalizar métricas
st.markdown(
    """
    <style>
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
    }
    .metric {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .metric .label {
        font-size: 0.9rem;
        font-weight: normal;
    }
    .metric .value {
        font-size: 1.5rem;
        color: #007BFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibir métricas
st.write("## Métricas de Contagem")
cols = st.columns(len(status_counts))
for col, (status, count) in zip(cols, status_counts.items()):
    col.markdown(f'<div class="metric"><div class="label">{status}</div><div class="value">{count}</div></div>', unsafe_allow_html=True)

# Calcular o valor orçado por status
valor_orcado_status = data.groupby('STATUS*')['VALOR ORÇADO'].sum().reset_index()

# Adicionar CSS para personalizar métricas de valor orçado por status
st.markdown(
    """
    <style>
    .valor-container {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
    }
    .valor {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .valor .label {
        font-size: 0.9rem;
        font-weight: normal;
    }
    .valor .value {
        font-size: 1.5rem;
        color: #28a745;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Exibir métricas de valor orçado por status
st.write("## Valor Orçado por Status")
cols_valor = st.columns(len(valor_orcado_status))
for col, (status, valor) in zip(cols_valor, valor_orcado_status.itertuples(index=False, name=None)):
    col.markdown(f'<div class="valor"><div class="label">{status}</div><div class="value">R${valor:,.2f}</div></div>', unsafe_allow_html=True)

# Inicializar estado da sessão para controlar a visibilidade da tabela de dados brutos
if 'show_raw_table' not in st.session_state:
    st.session_state.show_raw_table = False

# Função para alternar a visibilidade da tabela de dados brutos
def toggle_raw_table():
    st.session_state.show_raw_table = not st.session_state.show_raw_table

# Botão para alternar a tabela de dados brutos
if st.button('Mostrar/Ocultar Tabela de Dados Brutos', key='toggle_raw_table'):
    toggle_raw_table()

# Mostrar ou ocultar a tabela de dados brutos com base no estado
if st.session_state.show_raw_table:
    st.write("## Tabela de Dados Brutos Restantes para Execução")
    selected_columns = [
        'OS', 'DISCIPLINAS', 'DESCRIÇÃO DO SERVIÇO', 'LOCAL CORREIOS', 
        'PREDIO CORREIOS', 'MUNICÍPIO', 'DATA RECEBIDO', 'PRAZO DE ATENDIMENTO', 
        'PREVISÃO DE INÍCIO', 'PREVISÃO DE FINALIZAÇÃO'
    ]
    remaining_data = data[data['STATUS*'].isin(status_list)][selected_columns]
    st.dataframe(remaining_data)

st.write("---")

# Gráfico de Pizza para Orçamentista e quantos orçamentos fizeram
orcamentista_counts = data['ORÇAMENTISTA'].value_counts().reset_index()
orcamentista_counts.columns = ['ORÇAMENTISTA', 'Contagem']

orcamentista_chart = alt.Chart(orcamentista_counts).mark_arc().encode(
    theta=alt.Theta(field="Contagem", type="quantitative"),
    color=alt.Color(field="ORÇAMENTISTA", type="nominal"),
    tooltip=['ORÇAMENTISTA', 'Contagem']
).properties(
    title='Distribuição de Orçamentos por Orçamentista'
)

# Gráfico de Pizza para Normal/Urgente
urgente_counts = data['NORMAL / URGENTE'].value_counts().reset_index()
urgente_counts.columns = ['NORMAL / URGENTE', 'Contagem']

urgente_chart = alt.Chart(urgente_counts).mark_arc().encode(
    theta=alt.Theta(field="Contagem", type="quantitative"),
    color=alt.Color(field="NORMAL / URGENTE", type="nominal"),
    tooltip=['NORMAL / URGENTE', 'Contagem']
).properties(
    title='Distribuição de Normal/Urgente'
)

# Gráfico de Barra para Orçamentos feitos no mês
data['AnoMes'] = data['DATA ORÇADO'].dt.to_period('M')

orcamento_mes_counts = data.groupby('AnoMes').size().reset_index(name='Contagem')
orcamento_mes_counts['AnoMes'] = orcamento_mes_counts['AnoMes'].astype(str)

orcamento_mes_chart = alt.Chart(orcamento_mes_counts).mark_bar().encode(
    x=alt.X('AnoMes:N', title='Mês'),
    y=alt.Y('Contagem:Q', title='Contagem de Orçamentos'),
    color=alt.Color('AnoMes:N', legend=None),
    tooltip=['AnoMes', 'Contagem']
).properties(
    title='Orçamentos Feitos no Mês'
)

col1, col2 = st.columns([3, 6])
with col1:
    st.altair_chart(urgente_chart, use_container_width=True)
with col2:
    st.altair_chart(orcamento_mes_chart, use_container_width=True)

# Filtro para selecionar o orçamentista
orcamentista_list = data['ORÇAMENTISTA'].unique().tolist()
selected_orcamentista = st.selectbox("Selecione o Orçamentista", orcamentista_list, key='orcamentista_filter_unique')

# Filtrar dados com base no orçamentista selecionado
filtered_data = data[data['ORÇAMENTISTA'] == selected_orcamentista]

# Gráfico de Colunas para mostrar orçamentos por mês para o orçamentista selecionado
orcamento_mes_orcamentista_counts = filtered_data.groupby('AnoMes').size().reset_index(name='Contagem')
orcamento_mes_orcamentista_counts['AnoMes'] = orcamento_mes_orcamentista_counts['AnoMes'].astype(str)

orcamento_mes_orcamentista_chart = alt.Chart(orcamento_mes_orcamentista_counts).mark_bar().encode(
    x=alt.X('AnoMes:N', title='Mês'),
    y=alt.Y('Contagem:Q', title='Contagem de Orçamentos'),
    color=alt.Color('AnoMes:N', legend=None),
    tooltip=['AnoMes', 'Contagem']
).properties(
    title=f'Orçamentos Feitos no Mês por {selected_orcamentista}'
)

col4, col5 = st.columns([1, 3])
with col4:
    st.altair_chart(orcamentista_chart, use_container_width=True)
with col5:
    st.altair_chart(orcamento_mes_orcamentista_chart, use_container_width=True)

st.write("---")

# Função para converter valores monetários para float
def convert_to_float(val):
    if isinstance(val, str):
        val = val.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(val) if val else 0.0
    return val

# Aplicar a função de conversão nas colunas de valores
data['VALOR INSUMO'] = data['VALOR INSUMO'].apply(convert_to_float)
data['VALOR MÃO DE OBRA'] = data['VALOR MÃO DE OBRA'].apply(convert_to_float)
data['VALOR ORÇADO'] = data['VALOR ORÇADO'].apply(convert_to_float)

# Calcular os valores mensais para insumo, mão de obra e valor orçado
monthly_values = data.groupby('AnoMes').agg({
    'VALOR INSUMO': 'sum',
    'VALOR MÃO DE OBRA': 'sum',
    'VALOR ORÇADO': 'sum'
}).reset_index()
monthly_values['AnoMes'] = monthly_values['AnoMes'].astype(str)

# Gráfico de Colunas para mostrar valores de insumo, mão de obra e valor orçado por mês
melted_values = monthly_values.melt(id_vars='AnoMes', var_name='Tipo', value_name='Valor')

monthly_chart = alt.Chart(melted_values).mark_bar().encode(
    x=alt.X('AnoMes:N', title='Mês'),
    y=alt.Y('Valor:Q', title='Valor'),
    color=alt.Color('Tipo:N', legend=alt.Legend(title="Tipo de Valor")),
    tooltip=['AnoMes', 'Tipo', 'Valor']
).properties(
    title='Valores de Insumo, Mão de Obra e Valor Orçado por Mês'
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_title(
    fontSize=16
)

# Inicializar estado da sessão para controlar a visibilidade da tabela mensal
if 'show_monthly_table' not in st.session_state:
    st.session_state.show_monthly_table = False

# Função para alternar a visibilidade da tabela mensal
def toggle_monthly_table():
    st.session_state.show_monthly_table = not st.session_state.show_monthly_table

# Botão para alternar a tabela mensal
if st.button('Mostrar/Ocultar Tabela de Valores Mensais', key='toggle_monthly_table'):
    toggle_monthly_table()

# Mostrar ou ocultar a tabela de valores mensais com base no estado
col6, col7 = st.columns([1, 3])
with col6:
    if st.session_state.show_monthly_table:
        st.write("## Tabela de Valores Mensais")
        st.dataframe(monthly_values)
with col7:
    st.write("## Valores de Insumo, Mão de Obra e Valor Orçado por Mês")
    st.altair_chart(monthly_chart, use_container_width=True)

st.write("---")

# Calcular o ticket médio por mês
ticket_medio_mes = data.groupby('AnoMes')['VALOR ORÇADO'].mean().reset_index()
ticket_medio_mes.columns = ['AnoMes', 'Ticket Médio']
ticket_medio_mes['AnoMes'] = ticket_medio_mes['AnoMes'].astype(str)

# Calcular o ticket médio por dia
ticket_medio_dia = data.groupby('DATA ORÇADO')['VALOR ORÇADO'].mean().reset_index()
ticket_medio_dia.columns = ['Data', 'Ticket Médio']

# Classificar valores para colorir barras
def classify_value(value):
    if value > 10000:
        return 'Alto'
    elif value > 5000:
        return 'Médio'
    else:
        return 'Baixo'

ticket_medio_dia['Classificação'] = ticket_medio_dia['Ticket Médio'].apply(classify_value)

# Gráfico de colunas para o ticket médio por dia com zoom
ticket_medio_dia_chart = alt.Chart(ticket_medio_dia).mark_bar().encode(
    x=alt.X('Data:T', title='Dia'),
    y=alt.Y('Ticket Médio:Q', title='Ticket Médio'),
    color=alt.Color('Classificação:N', legend=None),
    tooltip=['Data', 'Ticket Médio', 'Classificação']
).properties(
    title='Ticket Médio por Dia'
)

# Inicializar estado da sessão para controlar a visibilidade da tabela de ticket médio
if 'show_ticket_table' not in st.session_state:
    st.session_state.show_ticket_table = False

# Função para alternar a visibilidade da tabela de ticket médio
def toggle_ticket_table():
    st.session_state.show_ticket_table = not st.session_state.show_ticket_table

# Botão para alternar a tabela de ticket médio
if st.button('Mostrar/Ocultar Tabela de Ticket Médio', key='toggle_ticket_table'):
    toggle_ticket_table()

# Mostrar ou ocultar a tabela de ticket médio com base no estado
col8, col9 = st.columns([1, 3])
with col8:
    if st.session_state.show_ticket_table:
        st.dataframe(ticket_medio_mes)
with col9:
    st.altair_chart(ticket_medio_dia_chart, use_container_width=True)

st.write("---")

# Filtrar dados para os anos 2023 e 2024
df_filtered = data[(data['DATA EXECUÇÃO (INÍCIO)'].dt.year >= 2023) & (data['DATA EXECUÇÃO (INÍCIO)'].dt.year <= 2024)]

# Dividir a página em duas colunas
col10, col11 = st.columns([3, 1])

# Seleção de período (data início e fim)
with col11:
    start_date = st.date_input("Data Início", value=datetime(2023, 1, 1), key='start_date_servicos')
    end_date = st.date_input("Data Fim", value=datetime(2023, 1, 7), key='end_date_servicos')

# Converter selected_date para pd.Timestamp
start_date = pd.Timestamp(start_date).date()
end_date = pd.Timestamp(end_date).date()

# Filtrar dados pelo período selecionado
df_filtered_by_date = df_filtered[(df_filtered['DATA EXECUÇÃO (INÍCIO)'].dt.date >= start_date) & (df_filtered['DATA FINALIZADO'].dt.date <= end_date)]

# Gráfico Altair
with col10:
    chart = alt.Chart(df_filtered_by_date).mark_bar().encode(
        x=alt.X('yearmonthdate(DATA EXECUÇÃO (INÍCIO)):T', title='Data'),
        y=alt.Y('count()', title='Número de Serviços'),
        color=alt.Color('yearmonth(DATA EXECUÇÃO (INÍCIO)):N', title='Mês/Ano')  # Colorido por mês/ano
    ).properties(
        width=800,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

# Exibir tabela com os detalhes se um período for selecionado
if not df_filtered_by_date.empty:
    st.subheader("Detalhes dos Serviços")
    st.dataframe(df_filtered_by_date[[
        'ID', 'CONTRATO', 'OS', 'MCU', 'NORMAL / URGENTE', 'FISCAL', 
        'PREVENTIVA / CORRETIVA', 'DISCIPLINAS', 'DESCRIÇÃO DO SERVIÇO', 
        'DESCRIÇÃO DETALHADA', 'LOCAL CORREIOS', 'PREDIO CORREIOS', 
        'MUNICÍPIO', 'DATA RECEBIDO', 'PRAZO DE ATENDIMENTO', 
        'PREVISÃO DE INÍCIO', 'PREVISÃO DE FINALIZAÇÃO', 'STATUS*', 
        'DATA DE ATUALIZAÇÃO', 'VALOR ORÇADO', 'DATA ORÇADO', 
        'ORÇAMENTISTA', 'VALOR INSUMO', 'VALOR MÃO DE OBRA', 
        'PERCENTUAL FD', 'VALOR FD', 'VALOR GASTO', 'VALOR APROVADO', 
        'DATA APROVADO', 'LUCRO BRUTO', 'VALOR PAGO', 
        'DESCRIÇÃO DA EXECUÇÃO', 'EXECUTADO', 'EXECUTADO (%)', 
        'DATA EXECUÇÃO (INÍCIO)', 'DATA FINALIZADO', 'NOTA FISCAL', 
        'DATA DE EMISSÃO DA NF', 'GLOSA', 'MEDIÇÃO', 'QUANTIDADE DE REVISÕES', 
        'VISTORIA TECNICO', 'VISTORIA DATA', 'LEVANTAMENTO', 
        'ASSINATURA DE FINALIZAÇÃO','FD', 'RM', 
        'COMPRAS STATUS', 'PRAZO P/ ENTREGA', 'OBS: COMPRAS', 
        'SOLICITANTE', 'SC', 'OC'
    ]])
else:
    st.write("Nenhum serviço encontrado para o período selecionado.")

st.write("---")

# Contar a quantidade de serviços por "PREDIO CORREIOS"
predio_counts = data['PREDIO CORREIOS'].value_counts().reset_index()
predio_counts.columns = ['PREDIO CORREIOS', 'Quantidade']

# Dividir a página em duas colunas
col12, col13 = st.columns([2, 1])

# Gráfico de barras mostrando a quantidade de serviços por "PREDIO CORREIOS"
with col12:
    chart = alt.Chart(predio_counts).mark_bar().encode(
        x=alt.X('PREDIO CORREIOS:N', title='Prédio Correios'),
        y=alt.Y('Quantidade:Q', title='Quantidade de Serviços'),
        color=alt.Color('PREDIO CORREIOS:N', legend=None)  # Colorido por prédio
    ).properties(
        title='Quantidade de Serviços por Prédio Correios',
        width=600,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

# Botão para mostrar/ocultar a tabela
if 'show_table' not in st.session_state:
    st.session_state.show_table = False

def toggle_table():
    st.session_state.show_table = not st.session_state.show_table

with col13:
    if st.button('Mostrar/Ocultar Tabela'):
        toggle_table()

    # Mostrar ou ocultar a tabela com base no estado
    if st.session_state.show_table:
        st.write("Tabela de Quantidade de Serviços por Prédio Correios")
        st.dataframe(predio_counts)

st.write("---")

# Calcular a média de serviços atendidos por dia para 2023 e 2024
daily_avg = data[data['DATA EXECUÇÃO (INÍCIO)'].dt.year.isin([2023, 2024])].groupby([data['DATA EXECUÇÃO (INÍCIO)'].dt.date.rename('Data'), data['DATA EXECUÇÃO (INÍCIO)'].dt.year.rename('Ano')]).size().reset_index(name='Contagem')

# Calcular a média para cada ano
avg_2023 = daily_avg[daily_avg['Ano'] == 2023]['Contagem'].mean()
avg_2024 = daily_avg[daily_avg['Ano'] == 2024]['Contagem'].mean()

# Dividir a página em duas colunas
col14, col15 = st.columns([3, 1])

# Gráfico de linhas mostrando a média de serviços atendidos por dia em 2023 e 2024
with col14:
    line_chart = alt.Chart(daily_avg).mark_line(point=True).encode(
        x=alt.X('Data:T', title='Data'),
        y=alt.Y('Contagem:Q', title='Média de Serviços Atendidos por Dia'),
        color=alt.Color('Ano:N', title='Ano')
    ).properties(
        title='Média de Serviços Atendidos por Dia (2023 e 2024)',
        width=800,
        height=400
    )
    st.altair_chart(line_chart, use_container_width=True)

# Exibir cartões de métricas para a média de serviços atendidos por dia em 2023 e 2024
with col15:
    st.metric(label="Média de Serviços por Dia em 2023", value=f"{avg_2023:.2f}")
    st.metric(label="Média de Serviços por Dia em 2024", value=f"{avg_2024:.2f}")

st.write("---")

