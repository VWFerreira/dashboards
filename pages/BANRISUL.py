import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTlBXGpJ6j2i-C6edJ-eB4X2DD-7KA7Ys1bIR-tCFeYt6B-7S30bcY_bd0TUtEbttDiMBtexpD-2C4-/pub?gid=1319816246&single=true&output=csv"


def carregar_dados(url):
    try:
        tabela = pd.read_csv(url)
        date_columns = ["DATA RECEBIDO", "DATA FINALIZADO", "DATA ORÇADO"]
        for col in date_columns:
            if col in tabela.columns:
                tabela[col] = pd.to_datetime(
                    tabela[col], format="%d/%m/%Y", dayfirst=True, errors="coerce"
                )
        return tabela

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")
        return None


def calcular_metricas(tabela, contrato, data_inicio, data_fim, data_dia):
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)
    data_dia = pd.to_datetime(data_dia)

    filtro_contrato = (
        tabela if contrato == "Todos" else tabela[tabela["CONTRATO"] == contrato]
    )
    filtro_periodo = filtro_contrato[
        (filtro_contrato["DATA RECEBIDO"] >= data_inicio)
        & (filtro_contrato["DATA RECEBIDO"] <= data_fim)
    ]

    total_os_recebidas_dia = filtro_contrato[
        filtro_contrato["DATA RECEBIDO"].dt.date == data_dia.date()
    ].shape[0]
    total_executadas_dia = filtro_contrato[
        (filtro_contrato["DATA FINALIZADO"].dt.date == data_dia.date())
        & (filtro_contrato["STATUS*"] == "EXECUTADO")
    ].shape[0]

    return {
        "total_os_recebidas": filtro_periodo.shape[0],
        "total_os_recebidas_dia": total_os_recebidas_dia,
        "total_executadas_dia": total_executadas_dia,
    }


def filtrar_ocorrencias(
    tabela, disciplinas, status_aberto, status_finalizado, contrato
):
    abertas = tabela[
        tabela["DISCIPLINAS"].isin(disciplinas)
        & tabela["STATUS*"].isin(status_aberto)
        & ((tabela["CONTRATO"] == contrato) | (contrato == "Todos"))
    ]
    finalizadas = tabela[
        tabela["DISCIPLINAS"].isin(disciplinas)
        & tabela["STATUS*"].isin(status_finalizado)
        & ((tabela["CONTRATO"] == contrato) | (contrato == "Todos"))
    ]
    return len(abertas), len(finalizadas)


def calcular_percentual(abertas, finalizadas):
    total = abertas + finalizadas
    return (finalizadas / total) * 100 if total > 0 else 0


def exibir_resultados_lote(tabela, contrato, disciplinas, titulo):
    status_aberto = [
        "RECEBIDO",
        "ORÇADO",
        "COMPRAS",
        "EXECUÇÃO",
        "VERIFICAR",
        "PREVENTIVA",
        "LEVANTAMENTO",
        "EM ORÇAMENTO",
        "EM ESPERA",
        "PROGRAMADO",
    ]
    status_finalizado = ["FINALIZADO", "NOTA FISCAL", "EXECUTADO", "MEDIÇÃO"]

    abertas, finalizadas = filtrar_ocorrencias(
        tabela, disciplinas, status_aberto, status_finalizado, contrato
    )
    percentual = calcular_percentual(abertas, finalizadas)

    st.markdown(
        f"""
        <div class='lote-card'>
            <h4 style='font-size: 1.1rem;font-family:Arial Narrow; text-align: center;'>{titulo}</h4>
            <p style='color: #1E90FF; font-size: 1.0rem; text-align: center;'>Abertas: {abertas} | Finalizadas: {finalizadas} | Percentual: {percentual:.2f}%</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_tabelas(tabela, data_inicio, data_fim, data_dia, contrato):
    data_dia = pd.to_datetime(data_dia)

    filtro_tabela = tabela[
        (tabela["DATA FINALIZADO"].dt.date == data_dia.date())
        & ((tabela["CONTRATO"] == contrato) | (contrato == "Todos"))
    ]

    total_disciplina_finalizadas = (
        filtro_tabela[["DISCIPLINAS", "CONTRATO", "RESPONSAVEL TÉCNICO"]]
        .value_counts()
        .reset_index()
    )
    total_disciplina_finalizadas.columns = [
        "Disciplina",
        "Contrato",
        "Responsavel Técnico",
        "Quantidade",
    ]

    st.markdown(
        "<h2 class='custom-subheader'>Total de Disciplinas Finalizadas Hoje</h2>",
        unsafe_allow_html=True,
    )
    st.table(total_disciplina_finalizadas)


def exibir_grafico_os_por_dia(tabela, data_inicio, data_fim, contrato):
    st.markdown(
        "<h2 class='custom-subheader'>Quantidade Ordens de Serviços recebidas por dia</h2>",
        unsafe_allow_html=True,
    )

    data_inicio = pd.to_datetime(data_inicio)
    data_fim = pd.to_datetime(data_fim)

    filtro_tabela = tabela[
        (tabela["DATA RECEBIDO"] >= data_inicio)
        & (tabela["DATA RECEBIDO"] <= data_fim)
        & ((tabela["CONTRATO"] == contrato) | (contrato == "Todos"))
    ].copy()  # Ensure we work with a copy

    filtro_tabela["MÊS"] = filtro_tabela["DATA RECEBIDO"].dt.month_name()

    os_por_dia = (
        filtro_tabela.groupby(["DATA RECEBIDO", "MÊS"])
        .size()
        .reset_index(name="Quantidade")
    )

    chart = (
        alt.Chart(os_por_dia)
        .mark_bar()
        .encode(
            x="DATA RECEBIDO:T",
            y="Quantidade:Q",
            color="MÊS:N",
            tooltip=["DATA RECEBIDO", "Quantidade", "MÊS"],
        )
        .properties(width=600, height=400)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


def exibir_metricas_lote(tabela, data_inicio, data_fim, data_dia):
    metricas_lote = {
        "Métrica": [
            "Total de OS Recebidas Hoje - Lote 01",
            "Total de OS Recebidas Julho - Lote 01",
            "Total de OS Recebidas Hoje - Lote 02",
            "Total de OS Recebidas Julho - Lote 02",
            "Total de OS Finalizadas Hoje - Lote 01",
            "Total de OS Finalizadas Hoje - Lote 02",
        ],
        "Quantidade": [
            calcular_metricas(tabela, "0100215/2023", data_inicio, data_fim, data_dia)[
                "total_os_recebidas_dia"
            ],
            calcular_metricas(
                tabela,
                "0100215/2023",
                datetime(2024, 7, 1).date(),
                datetime(2024, 7, 31).date(),
                data_dia,
            )["total_os_recebidas"],
            calcular_metricas(tabela, "0200215/2023", data_inicio, data_fim, data_dia)[
                "total_os_recebidas_dia"
            ],
            calcular_metricas(
                tabela,
                "0200215/2023",
                datetime(2024, 7, 1).date(),
                datetime(2024, 7, 31).date(),
                data_dia,
            )["total_os_recebidas"],
            calcular_metricas(tabela, "0100215/2023", data_inicio, data_fim, data_dia)[
                "total_executadas_dia"
            ],
            calcular_metricas(tabela, "0200215/2023", data_inicio, data_fim, data_dia)[
                "total_executadas_dia"
            ],
        ],
    }

    df_metricas_lote = pd.DataFrame(metricas_lote)
    st.table(df_metricas_lote)


def diario(url):
    st.markdown(
        """
        <style>
        .metric-card h4 {
            font-size: 16px;
            font-family: Arial Narrow;
        }

        .lote-card h4 {
            font-family: Arial Narrow;
        }
      
        .custom-subheader {
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
            font-family: Arial Narrow;
        }
        .custom-disciplina {
            font-weight: bold;
            font-family: Arial Narrow;
        }
        .custom-quantidade {
            font-size: 20px;
            font-family: Arial Narrow;
        }
        .horizontal-line {
            border: none;
            height: 2px;
            background-color: #ccc;
            margin: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    tabela = carregar_dados(url)
    if tabela is not None:
        contratos_interesse = ["0100215/2023", "0200215/2023"]
        filtro_contratos = tabela["CONTRATO"].isin(contratos_interesse)
        dados_filtrados = tabela[filtro_contratos]

        contagem_os = dados_filtrados["CONTRATO"].value_counts()

        total_os = contagem_os.sum()

        st.markdown(
            '<h3 style="font-size:28px; margin-bottom: 40px; font-family:Arial Narrow;">Total de Ordens de Serviços recebidas por Contrato</h3>',
            unsafe_allow_html=True,
        )

        tabela["DATA RECEBIDO"] = pd.to_datetime(
            tabela["DATA RECEBIDO"], format="%d/%m/%Y", dayfirst=True, errors="coerce"
        )

        tabela["DATA FINALIZADO"] = pd.to_datetime(
            tabela["DATA FINALIZADO"], format="%d/%m/%Y", dayfirst=True, errors="coerce"
        )

        julho_2024 = tabela[
            (tabela["DATA RECEBIDO"].dt.month == 7)
            & (tabela["DATA RECEBIDO"].dt.year == 2024)
        ]
        total_os_julho = julho_2024.shape[0]

        col1, col2, col3, col4, col5 = st.columns(5, gap="small")

        with col1:
            data_pie = pd.DataFrame(
                {
                    "Contrato": contratos_interesse,
                    "Quantidade": [
                        contagem_os.get(contratos_interesse[0], 0),
                        contagem_os.get(contratos_interesse[1], 0),
                    ],
                }
            )

            pie_chart = (
                alt.Chart(data_pie)
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta(field="Quantidade", type="quantitative"),
                    color=alt.Color(field="Contrato", type="nominal"),
                    tooltip=["Contrato", "Quantidade"],
                )
                .properties(width=150, height=150)
            )

            st.altair_chart(pie_chart, use_container_width=True)

        with col2:
            contrato_1 = contratos_interesse[0]
            count_1 = contagem_os.get(contrato_1, 0)
            st.markdown(
                f"<div style='font-size:18px; text-align:center;font-weight:bold;font-family:Arial Narrow;'>Lote1 {contrato_1}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:24px; text-align:center; color:#1E90FF;font-weight:bold;'>{count_1}</div>",
                unsafe_allow_html=True,
            )

        with col3:
            contrato_2 = contratos_interesse[1]
            count_2 = contagem_os.get(contrato_2, 0)
            st.markdown(
                f"<div style='font-size:18px; text-align:center;font-family:Arial Narrow; font-weight:bold;'>Lote2 {contrato_2}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:24px; text-align:center; color:#1E90FF; font-weight:bold;'>{count_2}</div>",
                unsafe_allow_html=True,
            )

        with col5:
            st.markdown(
                "<div style='font-size:18px; text-align:center;font-family:Arial Narrow; font-weight:bold;'>Total Geral</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:24px; text-align:center; color:#1E90FF; font-weight:bold;'>{total_os}</div>",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                "<div style='font-size:18px; text-align:center;font-family:Arial Narrow;font-weight:bold;'>Recebidas Julho 2024</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size:24px; text-align:center; color:#FFD700;font-weight:bold;'>{total_os_julho}</div>",
                unsafe_allow_html=True,
            )

        st.write(
            '<p style="font-size:24px;font-family: arial narrow; font-weight: bold; text-align: center;">Resultados Lote 01 e Lote 02</p>',
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4, gap="large")
        with col1:
            exibir_resultados_lote(
                tabela,
                "0100215/2023",
                [
                    "ALVENARIA",
                    "HIDRÁULICA",
                    "CIVIL",
                    "COBERTURA",
                    "COMUNICAÇÃO VISUAL",
                    "DRYWALL",
                    "INSUMOS E EQUIPAMENTOS",
                    "IMPERMEABILIZAÇÃO",
                    "MARCENARIA",
                    "PINTURA",
                    "SERRALHERIA",
                    "VIDRAÇARIA",
                    "PERSIANA",
                    "EXTINTOR",
                ],
                "Civil lote 1",
            )
        with col2:
            exibir_resultados_lote(
                tabela, "0100215/2023", ["ELÉTRICA"], "Elétrica lote 1"
            )
        with col3:
            exibir_resultados_lote(
                tabela,
                "0200215/2023",
                [
                    "ALVENARIA",
                    "HIDRÁULICA",
                    "CIVIL",
                    "COBERTURA",
                    "COMUNICAÇÃO VISUAL",
                    "DRYWALL",
                    "INSUMOS E EQUIPAMENTOS",
                    "IMPERMEABILIZAÇÃO",
                    "MARCENARIA",
                    "PINTURA",
                    "SERRALHERIA",
                    "VIDRAÇARIA",
                    "PERSIANA",
                    "EXTINTOR",
                ],
                "Civil Lote 2",
            )
        with col4:
            exibir_resultados_lote(
                tabela, "0200215/2023", ["ELÉTRICA"], "Elétrica Lote 2"
            )

        st.markdown("<div class='horizontal-line'></div>", unsafe_allow_html=True)

        col5, col6 = st.columns([3, 1])
        with col6:
            data_inicio = st.date_input(
                "Data de Início", value=datetime(2024, 1, 1).date(), key="data_inicio"
            )
            data_fim = st.date_input(
                "Data de Fim", value=datetime.now().date(), key="data_fim"
            )
            data_dia = st.date_input(
                "Data do Dia", value=datetime.now().date(), key="data_dia"
            )
            contrato_options = ["Todos"] + tabela["CONTRATO"].unique().tolist()
            contrato = st.selectbox("Contrato", contrato_options, key="contrato")

            st.markdown(
                """
                <div class='metric-subtitle'>
                    <h4>Métricas Consolidadas Totais</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

            total_os_recebidas_dia = (
                calcular_metricas(
                    tabela, "0100215/2023", data_inicio, data_fim, data_dia
                )["total_os_recebidas_dia"]
                + calcular_metricas(
                    tabela, "0200215/2023", data_inicio, data_fim, data_dia
                )["total_os_recebidas_dia"]
            )
            total_os_finalizadas_dia = (
                calcular_metricas(
                    tabela, "0100215/2023", data_inicio, data_fim, data_dia
                )["total_executadas_dia"]
                + calcular_metricas(
                    tabela, "0200215/2023", data_inicio, data_fim, data_dia
                )["total_executadas_dia"]
            )

            st.write(f"Debug Info: {total_os_finalizadas_dia}")  # Debug line

            metricas_totais = {
                "Métrica": [
                    "Total de OS Recebidas Hoje",
                    "Total de OS Finalizadas Hoje",
                ],
                "Quantidade": [
                    total_os_recebidas_dia,
                    total_os_finalizadas_dia,
                ],
            }

            df_metricas_totais = pd.DataFrame(metricas_totais)
            st.table(df_metricas_totais)

        with col5:
            exibir_grafico_os_por_dia(tabela, data_inicio, data_fim, contrato)

        st.markdown("<div class='horizontal-line'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class='metric-subtitle'>
                <h4>Métricas Lote 01 e Lote 02</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col7, col8 = st.columns([6, 4])
        with col7:
            exibir_metricas_lote(tabela, data_inicio, data_fim, data_dia)
        with col8:
            exibir_tabelas(tabela, data_inicio, data_fim, data_dia, contrato)

        st.markdown("<div class='horizontal-line'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    diario(url)


def carregar_dados(url):
    df = pd.read_csv(url)
    df_filtered = df[
        [
            "CONTRATO",
            "VALOR ORÇADO",
            "DATA ORÇADO",
            "VALOR INSUMO",
            "VALOR MÃO DE OBRA",
            "STATUS*",
            "ORÇAMENTISTA",
        ]
    ].copy()

    df_filtered["DATA ORÇADO"] = pd.to_datetime(
        df_filtered["DATA ORÇADO"], format="%d/%m/%Y", errors="coerce"
    )

    def convert_to_numeric(value):
        if isinstance(value, str):
            value = value.replace("R$", "").replace(".", "").replace(",", ".")
        return pd.to_numeric(value, errors="coerce")

    for col in ["VALOR ORÇADO", "VALOR INSUMO", "VALOR MÃO DE OBRA"]:
        df_filtered[col] = df_filtered[col].apply(convert_to_numeric)

    df_filtered = df_filtered[
        df_filtered["DATA ORÇADO"].dt.year.isin([2023, 2024, 2025, 2026, 2027])
    ]

    df_filtered["AnoMes"] = (
        df_filtered["DATA ORÇADO"].dt.to_period("M").dt.to_timestamp()
    )
    df_filtered["Dia"] = df_filtered["DATA ORÇADO"].dt.date

    return df_filtered


def calcular_metricas(df, contrato):
    df_contrato = df[df["CONTRATO"] == contrato]
    data_atual = datetime.now().date()
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    df_today = df_contrato[df_contrato["Dia"] == data_atual]
    df_month = df_contrato[
        (df_contrato["DATA ORÇADO"].dt.month == mes_atual)
        & (df_contrato["DATA ORÇADO"].dt.year == ano_atual)
    ]
    df_finalizado = df_contrato[
        df_contrato["STATUS*"].isin(["FINALIZADO", "EXECUTADO"])
    ]

    if not df_today.empty:
        valor_orcado_hoje = df_today["VALOR ORÇADO"].sum()
        valor_insumo_hoje = df_today["VALOR INSUMO"].sum()
        valor_mao_de_obra_hoje = df_today["VALOR MÃO DE OBRA"].sum()
        orcamentos_hoje = df_today.shape[0]
    else:
        valor_orcado_hoje = 0
        valor_insumo_hoje = 0
        valor_mao_de_obra_hoje = 0
        orcamentos_hoje = 0

    if not df_month.empty:
        valor_orcado_mes = df_month["VALOR ORÇADO"].sum()
        valor_insumo_mes = df_month["VALOR INSUMO"].sum()
        valor_mao_de_obra_mes = df_month["VALOR MÃO DE OBRA"].sum()
    else:
        valor_orcado_mes = 0
        valor_insumo_mes = 0
        valor_mao_de_obra_mes = 0

    if not df_finalizado.empty:
        valor_total_orcado = df_finalizado["VALOR ORÇADO"].sum()
    else:
        valor_total_orcado = 0

    return (
        valor_orcado_hoje,
        valor_insumo_hoje,
        valor_mao_de_obra_hoje,
        orcamentos_hoje,
        valor_orcado_mes,
        valor_insumo_mes,
        valor_mao_de_obra_mes,
        valor_total_orcado,
    )


def exibir_metricas_tabela(metrics, title):
    st.markdown(f"<div class='title'>{title}</div>", unsafe_allow_html=True)
    df_metrics = pd.DataFrame(
        {
            "Métrica": [
                "Valor Orçado Hoje",
                "Valor Insumo Hoje",
                "Valor Mão de Obra Hoje",
                "Orçamentos Hoje",
                "Valor Orçado no Mês",
                "Valor Insumo no Mês",
                "Valor Mão de Obra no Mês",
                "Valor Total Orçado",
            ],
            "Valor": [
                f"R${metrics[0]:,.2f}",
                f"R${metrics[1]:,.2f}",
                f"R${metrics[2]:,.2f}",
                metrics[3],
                f"R${metrics[4]:,.2f}",
                f"R${metrics[5]:,.2f}",
                f"R${metrics[6]:,.2f}",
                f"R${metrics[7]:,.2f}",
            ],
        }
    )
    st.table(df_metrics)


def orcamento():
    st.markdown(
        """
        <style>
        .title {
            font-size: 20px;
            font-weight: bold;
            font-family: Arial Narrow, sans-serif;
            text-align: center;
            line-height: 3.5;
        }
        .metric-label {
            font-size: 18px;
            font-weight: bold;
            font-family: Arial Narrow, sans-serif;
            text-align: center;
            line-height:2.5;
        }
        .metric-value {
            font-size: 28px;
            color: #4682B4;
            font-family: Arial Narrow, sans-serif;
            text-align: center;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTlBXGpJ6j2i-C6edJ-eB4X2DD-7KA7Ys1bIR-tCFeYt6B-7S30bcY_bd0TUtEbttDiMBtexpD-2C4-/pub?gid=1319816246&single=true&output=csv"
    df_filtered = carregar_dados(url)

    col1, col2 = st.columns([6, 1])

    with col2:
        contrato_opcoes = ["Todos"] + df_filtered["CONTRATO"].unique().tolist()
        contrato_selecionado = st.selectbox(
            "Selecione o Contrato", contrato_opcoes, key="contrato_filtro"
        )
        data_inicio = st.date_input(
            "Data de Início", df_filtered["DATA ORÇADO"].min().date()
        )
        data_fim = st.date_input("Data de Fim", df_filtered["DATA ORÇADO"].max().date())

        if contrato_selecionado != "Todos":
            df_filtered = df_filtered[df_filtered["CONTRATO"] == contrato_selecionado]

        if data_inicio and data_fim:
            df_filtered = df_filtered[
                (df_filtered["DATA ORÇADO"] >= pd.to_datetime(data_inicio))
                & (df_filtered["DATA ORÇADO"] <= pd.to_datetime(data_fim))
            ]

        total_orcamentos_periodo = df_filtered.shape[0]

        st.markdown(
            f"<div class='card'><div class='metric-label'>Total de Orçamentos no Período</div><div class='metric-value'>{total_orcamentos_periodo}</div></div>",
            unsafe_allow_html=True,
        )

    with col1:
        st.subheader("Grafico Orçamentos")

        bars = (
            alt.Chart(df_filtered)
            .mark_bar()
            .encode(
                x=alt.X("yearmonthdate(DATA ORÇADO):T", title="Data"),
                y=alt.Y("count():Q", title="Quantidade de Orçamentos"),
                color=alt.Color("yearmonth(DATA ORÇADO):N", title="Mês/Ano"),
                tooltip=["DATA ORÇADO", "count()"],
            )
        )

        text = bars.mark_text(
            align="center", baseline="middle", dy=-10, color="white"
        ).encode(text="count():Q")

        chart1 = (bars + text).properties(width=1100, height=400)

        st.altair_chart(chart1)
        st.write("---")

    metrics_lote1 = calcular_metricas(df_filtered, "0100215/2023")
    metrics_lote2 = calcular_metricas(df_filtered, "0200215/2023")

    col3, col4 = st.columns(2)
    with col3:
        exibir_metricas_tabela(
            metrics_lote1,
            "Métricas Lote 1 - Contrato 0100215/2023",
        )
    with col4:
        exibir_metricas_tabela(
            metrics_lote2,
            "Métricas Lote 2 - Contrato 0200215/2023",
        )

    st.write("---")

    st.subheader("Orçamentos Feitos no Dia")
    df_hoje = df_filtered[df_filtered["Dia"] == datetime.now().date()]
    st.table(
        df_hoje[
            [
                "ORÇAMENTISTA",
                "CONTRATO",
                "VALOR ORÇADO",
                "VALOR INSUMO",
                "VALOR MÃO DE OBRA",
            ]
        ]
    )

    st.write("---")
    col5, col6 = st.columns([1, 6])

    with col5:
        orcamentista_opcoes = ["Todos"] + df_filtered["ORÇAMENTISTA"].unique().tolist()
        orcamentista_selecionado = st.multiselect(
            "Selecione os Orçamentistas",
            orcamentista_opcoes,
            default=["Todos"],
            key="orcamentista_filtro",
        )
        data_inicio = st.date_input(
            "Data de Início",
            df_filtered["DATA ORÇADO"].min().date(),
            key="orcamentista_data_inicio",
        )
        data_fim = st.date_input(
            "Data de Fim",
            df_filtered["DATA ORÇADO"].max().date(),
            key="orcamentista_data_fim",
        )

        if "Todos" not in orcamentista_selecionado:
            df_filtered_orcamentista = df_filtered[
                df_filtered["ORÇAMENTISTA"].isin(orcamentista_selecionado)
            ]
        else:
            df_filtered_orcamentista = df_filtered

        if data_inicio and data_fim:
            df_filtered_orcamentista = df_filtered_orcamentista[
                (df_filtered_orcamentista["DATA ORÇADO"] >= pd.to_datetime(data_inicio))
                & (df_filtered_orcamentista["DATA ORÇADO"] <= pd.to_datetime(data_fim))
            ]

        total_orcamentos_orcamentista = df_filtered_orcamentista.shape[0]

        st.markdown(
            f"<div class='card'><div class='metric-label'>Total de Orçamentos</div><div class='metric-value'>{total_orcamentos_orcamentista}</div></div>",
            unsafe_allow_html=True,
        )

    with col6:
        bars2 = (
            alt.Chart(df_filtered_orcamentista)
            .mark_bar()
            .encode(
                x=alt.X("yearmonthdate(DATA ORÇADO):T", title="Data"),
                y=alt.Y("count():Q", title="Quantidade de Orçamentos"),
                color=alt.Color("ORÇAMENTISTA:N", title="Orçamentista"),
                tooltip=["DATA ORÇADO", "count()", "ORÇAMENTISTA"],
            )
        )

        text2 = bars2.mark_text(
            align="center", baseline="middle", dy=-10, color="white"
        ).encode(text="count():Q")

        chart2 = (
            (bars2 + text2)
            .properties(
                width=1000,
                height=400,
                title="Quantidade de Orçamentos por Dia por Orçamentista",
            )
            .interactive()
        )

        st.altair_chart(chart2)
    st.write("---")

    st.subheader("Valores Orçados por Mês (2023-2026)")
    col7, col8 = st.columns([6, 1])

    with col8:
        ano_opcoes = ["Todos"] + sorted(
            df_filtered["DATA ORÇADO"].dt.year.unique().tolist()
        )
        ano_selecionado = st.selectbox("Selecione o Ano", ano_opcoes, key="ano_filtro")
        contrato_opcoes = ["Todos", "0100215/2023", "0200215/2023"]
        contrato_selecionado = st.selectbox(
            "Selecione o Contrato", contrato_opcoes, key="contrato_filtro_ano"
        )

    with col7:
        if ano_selecionado != "Todos":
            df_filtered = df_filtered[
                df_filtered["DATA ORÇADO"].dt.year == int(ano_selecionado)
            ]

        if contrato_selecionado != "Todos":
            df_filtered = df_filtered[df_filtered["CONTRATO"] == contrato_selecionado]

        bars3 = (
            alt.Chart(df_filtered)
            .mark_bar()
            .encode(
                x=alt.X("yearmonth(DATA ORÇADO):T", title="Mês/Ano"),
                y=alt.Y("sum(VALOR ORÇADO):Q", title="Valor Orçado"),
                color=alt.Color("year(DATA ORÇADO):N", title="Ano"),
                tooltip=["yearmonth(DATA ORÇADO):T", "sum(VALOR ORÇADO):Q"],
            )
        )

        text3 = bars3.mark_text(
            align="center", baseline="middle", dy=-10, color="white"
        ).encode(text="sum(VALOR ORÇADO):Q")

        chart3 = (
            (bars3 + text3)
            .properties(
                width=1000, height=400, title="Valores Orçados por Mês (2023-2026)"
            )
            .interactive()
        )

        st.altair_chart(chart3)


if __name__ == "__main__":
    orcamento()
def carregar_dados(url):
    try:
        tabela = pd.read_csv(url)
        date_columns = ["DATA RECEBIDO", "DATA FINALIZADO", "DATA ORÇADO"]
        for col in date_columns:
            if col in tabela.columns:
                tabela[col] = pd.to_datetime(
                    tabela[col], format="%d/%m/%Y",
                    dayfirst=True,
                    errors="coerce"
                )

        # Convertendo colunas de valores para numérico
        valor_columns = ["VALOR ORÇADO", "VALOR INSUMO", "VALOR MÃO DE OBRA"]
        for col in valor_columns:
            if col in tabela.columns:
                tabela[col] = tabela[col].apply(lambda x: pd.to_numeric(str(x).replace("R$", "").replace(".", "").replace(",", "."), errors="coerce"))

        return tabela

    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")
        return None

def calcular_metricas(tabela, data_inicio, data_fim, contrato):
    if contrato != "Todos":
        tabela = tabela[tabela["CONTRATO"] == contrato]

    filtro_recebidas = tabela[
        (tabela["DATA RECEBIDO"] >= data_inicio) &
        (tabela["DATA RECEBIDO"] <= data_fim)
    ]
    filtro_finalizadas = tabela[
        (tabela["DATA FINALIZADO"] >= data_inicio) &
        (tabela["DATA FINALIZADO"] <= data_fim) &
        (tabela["STATUS*"].isin(["EXECUTADO", "FINALIZADO"]))
    ]
    filtro_orcamentos = tabela[
        (tabela["DATA ORÇADO"] >= data_inicio) &
        (tabela["DATA ORÇADO"] <= data_fim)
    ]
    filtro_abertas = tabela[
        (tabela["STATUS*"].isin([
            "RECEBIDO", "ORÇADO", "COMPRAS", "EXECUÇÃO",
            "VERIFICAR", "PREVENTIVA", "LEVANTAMENTO",
            "EM ORÇAMENTO", "EM ESPERA", "PROGRAMADO"
        ])) &
        (tabela["DATA RECEBIDO"] >= data_inicio) &
        (tabela["DATA RECEBIDO"] <= data_fim)
    ]

    total_recebidas = filtro_recebidas.shape[0]
    total_finalizadas = filtro_finalizadas.shape[0]
    total_orcamentos = filtro_orcamentos.shape[0]
    total_abertas = filtro_abertas.shape[0]

    valor_orcado = filtro_orcamentos["VALOR ORÇADO"].sum()
    valor_insumo = filtro_orcamentos["VALOR INSUMO"].sum()
    valor_mao_obra = filtro_orcamentos["VALOR MÃO DE OBRA"].sum()

    percentual_finalizadas = (total_finalizadas / total_recebidas * 100
                              if total_recebidas > 0 else 0)

    return {
        "total_recebidas": total_recebidas,
        "total_finalizadas": total_finalizadas,
        "total_orcamentos": total_orcamentos,
        "total_abertas": total_abertas,
        "valor_orcado": valor_orcado,
        "valor_insumo": valor_insumo,
        "valor_mao_obra": valor_mao_obra,
        "percentual_finalizadas": percentual_finalizadas
    }

def exibir_grafico(tabela, data_inicio, data_fim, contrato):
    if contrato != "Todos":
        tabela = tabela[tabela["CONTRATO"] == contrato]

    filtro_recebidas = tabela[
        (tabela["DATA RECEBIDO"] >= data_inicio) &
        (tabela["DATA RECEBIDO"] <= data_fim)
    ]

    grafico = alt.Chart(filtro_recebidas).mark_bar(color='#1E90FF').encode(
        x='DATA RECEBIDO:T',
        y='count():Q',
        tooltip=['DATA RECEBIDO:T', 'count():Q']
    ).properties(
        width=400,
        height=400
    )

    return grafico

def exibir_grafico_pizza(tabela, data_inicio, data_fim, contrato):
    if contrato != "Todos":
        tabela = tabela[tabela["CONTRATO"] == contrato]

    filtro_recebidas = tabela[
        (tabela["DATA RECEBIDO"] >= data_inicio) &
        (tabela["DATA RECEBIDO"] <= data_fim)
    ]

    pizza_data = filtro_recebidas.groupby('NORMAL / URGENTE').size().reset_index(name='count')

    grafico_pizza = alt.Chart(pizza_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="NORMAL / URGENTE", type="nominal"),
        tooltip=['NORMAL / URGENTE', 'count']
    ).properties(
        width=400,
        height=400
    ).configure_mark(
        color='#6A5ACD'
    )

    return grafico_pizza

def exibir_grafico_disciplinas(tabela, data_inicio, data_fim):
    filtro_orcamentos_julho = tabela[
        (tabela["DATA ORÇADO"] >= data_inicio) &
        (tabela["DATA ORÇADO"] <= data_fim)
    ]

    disciplina_totais = filtro_orcamentos_julho.groupby('DISCIPLINAS')['VALOR ORÇADO'].sum().reset_index()

    grafico_disciplinas = alt.Chart(disciplina_totais).mark_bar().encode(
        x='DISCIPLINAS',
        y='VALOR ORÇADO',
        color='DISCIPLINAS',
        tooltip=['DISCIPLINAS', 'VALOR ORÇADO']
    ).properties(
        width=800,
        height=400
    )

    return grafico_disciplinas

def renderizar_imagem(path):
    image = Image.open(path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f'<img src="data:image/png;base64,{img_str}" class="img-fluid" alt="Responsive image">'

def semana():
    st.markdown(
        """
        <style>
        .metric {
            font-size: 18px !important;
        }
        .metric-label {
            font-size: 16px !important;
            font-family: Arial Narrow, sans-serif;
            font-weight: bold;
            text-align: center;
        }
        .metric-value {
            font-size: 16px !important;
            color: #1E90FF!important;
            font-family: Arial Narrow, sans-serif;
            text-align: center;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .header img {
            height: 100px;
        }
        .header-title {
            font-size: 32px;
            font-family: Arial Narrow, sans-serif;
            font-weight: bold;
            text-align: center;
            flex-grow: 1;
        }
        .container {
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .spacing {
            margin-top: 50px;
        }
        .btn-primary {
            background-color: #007bff;
            border-color: #007bff;
            color: #fff;
        }
        .btn-primary:hover {
            background-color: #0056b3;
            border-color: #0056b3;
        }
        </style>
        <div class="header">
            <div class="header-title">Banrisul Semanal</div>
        </div>
        <div class="spacing"></div>
        """,
        unsafe_allow_html=True,
    )

    tabela = carregar_dados(url)
    if tabela is not None:
        contratos_interesse = ["0100215/2023", "0200215/2023", "Todos"]

        # Filtros de data e contrato na mesma linha dos gráficos
        col1, col2, col3 = st.columns([1, 3, 1])
        with col3:
            data_inicio = st.date_input("Data de Início", datetime(2024, 7, 1))
            data_fim = st.date_input("Data de Fim", datetime(2024, 7, 31))
            contrato = st.selectbox("Selecione o Contrato", contratos_interesse)

        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)

        # Exibir gráficos
        with col1:
            grafico_pizza = exibir_grafico_pizza(tabela, data_inicio, data_fim, contrato)
            st.altair_chart(grafico_pizza, use_container_width=True)
        with col2:
            grafico = exibir_grafico(tabela, data_inicio, data_fim, contrato)
            st.altair_chart(grafico, use_container_width=True)

        st.write("---")

        # Exibir métricas
        st.subheader("Métricas")
        metricas = calcular_metricas(tabela, data_inicio, data_fim, contrato)
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Total Recebidas</div>"
                f"<div class='metric-value'>{metricas['total_recebidas']}</div></div>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Total Finalizadas</div>"
                f"<div class='metric-value'>{metricas['total_finalizadas']}</div></div>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Total Orçamentos</div>"
                f"<div class='metric-value'>{metricas['total_orcamentos']}</div></div>",
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Total Abertas</div>"
                f"<div class='metric-value'>{metricas['total_abertas']}</div></div>",
                unsafe_allow_html=True
            )
        with col5:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Percentual Finalizadas</div>"
                f"<div class='metric-value'>{metricas['percentual_finalizadas']:.2f}%</div></div>",
                unsafe_allow_html=True
            )
        with col6:
            st.markdown(
                f"<div class='container'><div class='metric-label'>Total Finalizadas</div>"
                f"<div class='metric-value'>{metricas['total_finalizadas']}</div></div>",
                unsafe_allow_html=True
            )

        st.write("---")

        # Gráfico de valores por disciplina
        st.subheader("Gráfico de Valores por Disciplina")
        grafico_disciplinas = exibir_grafico_disciplinas(tabela, data_inicio, data_fim)
        st.altair_chart(grafico_disciplinas, use_container_width=True)

        # Botões para mostrar/ocultar tabelas
        st.subheader("Orçamentos Feitos no Mês de Julho")
        if "mostrar_orcamentos" not in st.session_state:
            st.session_state.mostrar_orcamentos = False

        if st.button("Mostrar/Ocultar Tabela de Orçamentos"):
            st.session_state.mostrar_orcamentos = not st.session_state.mostrar_orcamentos

        if st.session_state.mostrar_orcamentos:
            filtro_orcamentos_julho = tabela[
                (tabela["DATA ORÇADO"] >= data_inicio) &
                (tabela["DATA ORÇADO"] <= data_fim)
            ]

            st.table(
                filtro_orcamentos_julho[
                    [
                        "CONTRATO", "OS" "DISCIPLINAS", "ORÇAMENTISTA", "DATA ORÇADO", 
                        "VALOR INSUMO", "VALOR MÃO DE OBRA", "VALOR ORÇADO"
                    ]
                ]
            )

        st.subheader("Serviços Finalizados no Mês de Julho")
        if "mostrar_finalizados" not in st.session_state:
            st.session_state.mostrar_finalizados = False

        if st.button("Mostrar/Ocultar Tabela de Serviços Finalizados"):
            st.session_state.mostrar_finalizados = not st.session_state.mostrar_finalizados

        if st.session_state.mostrar_finalizados:
            filtro_finalizados_julho = tabela[
                (tabela["DATA FINALIZADO"] >= data_inicio) &
                (tabela["DATA FINALIZADO"] <= data_fim) &
                (tabela["STATUS*"].isin(["EXECUTADO", "FINALIZADO"]))
            ]

            # Calcular dias de atraso
            filtro_finalizados_julho["DIAS DE ATRASO"] = (filtro_finalizados_julho["DATA FINALIZADO"] - filtro_finalizados_julho["DATA RECEBIDO"]).dt.days - 30
            filtro_finalizados_julho["DIAS DE ATRASO"] = filtro_finalizados_julho["DIAS DE ATRASO"].apply(lambda x: x if x > 0 else 0)

            st.table(
                filtro_finalizados_julho[
                    [
                        "OS", "RESPONSAVEL TÉCNICO", "DISCIPLINAS",
                        "STATUS*", "DATA RECEBIDO", "PRAZO DE ATENDIMENTO",
                        "DATA FINALIZADO", "PRÉDIO", "DIAS DE ATRASO"
                    ]
                ]
            )

        st.markdown(
            """
            <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" crossorigin="anonymous"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" crossorigin="anonymous"></script>
            """,
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    semana()


def convert_currency(value):
    if isinstance(value, str):
        return float(value.replace("R$", "").replace(".", "").replace(",", ".").strip())
    return value

@st.cache_data(ttl=60)
def load_data(csv_url):
    df = pd.read_csv(csv_url)
    df = df[~df["VALOR"].astype(str).str.contains("nan|http")].copy()
    df["VALOR"] = df["VALOR"].apply(convert_currency)
    df["SALDO L1"] = df["SALDO L1"].apply(convert_currency)
    df["SALDO L2"] = df["SALDO L2"].apply(convert_currency)
    df["MES_ANO"] = df["MES"].astype(str) + "/" + df["ANO"].astype(str)
    return df

def saldo():
    st.markdown(
        """
        <style>
        .metric {
            font-size: 24px !important;
        }
        .metric-label {
            font-size: 20px !important;
            font-family: Arial Narrow, sans-serif;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }
        .metric-value {
            font-size: 20px !important;
            color: #1E90FF!important;
            font-family: Arial Narrow, sans-serif;
            text-align: center;
            font-family: Arial Narrow, sans-serif;
        }
        .contract-info {
            font-size: 24px;
            font-weight: bold;
            font-family: Arial Narrow, sans-serif;
            padding: 60px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    csv_url = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vSlTQoxa_YIMgRHv5x-URXirElC2efKea8CKK4U2qhqIKJPg_Zgv6IKZFVRCMNhYlohC0la69ueAyL_/pub?gid=713266789&single=true&output=csv")

    with st.spinner("Carregando dados..."):
        df = load_data(csv_url)

    summary_stats = df[["VALOR", "SALDO L1", "SALDO L2"]].describe()

    total_paid_lote1 = df[(df["LOTE"] == "LOTE 01") & (df["STATUS"] == "PAGO")][
        "VALOR"
    ].sum()
    total_paid_lote2 = df[(df["LOTE"] == "LOTE 02") & (df["STATUS"] == "PAGO")][
        "VALOR"
    ].sum()
    pending_payments_lote1 = df[(df["LOTE"] == "LOTE 01") & (df["STATUS"] != "PAGO")][
        "VALOR"
    ].sum()
    pending_payments_lote2 = df[(df["LOTE"] == "LOTE 02") & (df["STATUS"] != "PAGO")][
        "VALOR"
    ].sum()

    total_mes = pending_payments_lote1 + pending_payments_lote2

    st.markdown(
        '<div class="contract-info">CONTRATO 0100215/2023: R$ 4.500,000 ||| CONTRATO 0200215/2023: R$ 2.956.444,92</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        nota_fiscal = st.text_input("Número da Nota Fiscal")
        mes = st.selectbox("Mês", options=["Todos"] + list(df["MES_ANO"].unique()))

    filtered_df = df.copy()
    if nota_fiscal:
        filtered_df = filtered_df[
            filtered_df["NOTA FISCAL"].astype(str).str.contains(nota_fiscal)
        ]
    if mes != "Todos":
        filtered_df = filtered_df[filtered_df["MES_ANO"] == mes]

    monthly_totals_filtered = (
        filtered_df.groupby("MES_ANO")["VALOR"].sum().reset_index()
    )

    chart = (
        alt.Chart(monthly_totals_filtered)
        .mark_bar()
        .encode(
            x=alt.X("MES_ANO", title="Mês e Ano", sort=None),
            y="VALOR",
            tooltip=["MES_ANO", "VALOR"],
            color=alt.Color("MES_ANO", legend=alt.Legend(title="Mês e Ano")),
        )
        .properties(
            title="Total de Faturas por Mês",
            width=600,
            height=400,
        )
    )

    with col2:
        st.altair_chart(chart, use_container_width=True)

    col3, col4, col5, col6 = st.columns(4)
    with col3:
        st.markdown(
            f'<div class="metric-label">Total Pago Lote 1:</div> <div class="metric-value">R$ {total_paid_lote1:,.2f}</div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="metric-label">Saldo Lote 1:</div> <div class="metric-value">R$ {summary_stats.loc["mean", "SALDO L1"]:,.2f}</div>',
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f'<div class="metric-label">Total Pago Lote 2:</div> <div class="metric-value">R$ {total_paid_lote2:,.2f}</div>',
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f'<div class="metric-label">Saldo Lote 2:</div> <div class="metric-value">R$ {summary_stats.loc["mean", "SALDO L2"]:,.2f}</div>',
            unsafe_allow_html=True,
        )

    col7, col8, col9, col10 = st.columns(4)
    with col7:
        st.markdown(
            f'<div class="metric-label">Aguardando Pagamento Lote 1:</div> <div class="metric-value">R$ {pending_payments_lote1:,.2f}</div>',
            unsafe_allow_html=True,
        )
    with col8:
        st.markdown(
            f'<div class="metric-label">Aguardando Pagamento Lote 2:</div> <div class="metric-value">R$ {pending_payments_lote2:,.2f}</div>',
            unsafe_allow_html=True,
        )
    with col9:
        total_invoices = df["NOTA FISCAL"].count()
        st.markdown(
            f'<div class="metric-label">NF: Quantidade:</div> <div class="metric-value">{total_invoices}</div>',
            unsafe_allow_html=True,
        )
    with col10:
        st.markdown(
            f'<div class="metric-label">Total Mês:</div> <div class="metric-value">R$ {total_mes:,.2f}</div>',
            unsafe_allow_html=True,
        )
    st.write("---")
    st.write("Obs: O valor inicial do contrato 0200215/2023 é de 700.000,00. Foi feita uma suplementação no contrato no valor de 1.956.444,92. Desta forma, o valor total ficou em 2.656.444,92.")

if __name__ == "__main__":
    saldo()
