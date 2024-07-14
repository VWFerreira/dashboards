import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from PIL import Image

# Configurar layout da página para largura completa
st.set_page_config(layout="wide")

# Carregar imagens
imagem2 = Image.open("./image/inmetro.png")

# Reduzir o tamanho das imagens
imagem2 = imagem2.resize((100, 100))

# Definir estilo customizado
st.markdown(
    """
    <style>
    .container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: -20px; /* Reduzir o espaçamento do cabeçalho */
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
    .custom-header {
        font-size: 45px;
        font-weight: bold;
        text-align: center;
        margin-top: 20px; /* Ajustar o espaçamento superior */
    }
    </style>
    """, unsafe_allow_html=True
)

# Layout com colunas
st.markdown('<div class="container">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    st.image(imagem2, caption=None, use_column_width=False)

with col2:
    st.markdown('<div class="custom-header">Contrato INMETRO</div>', unsafe_allow_html=True)

