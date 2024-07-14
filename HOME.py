import streamlit as st

# Caminho para a imagem local
image_path = './image/genn.png'

# Alternativamente, você pode usar uma URL
# image_url = 'https://url.da.sua/imagem.png'

# Adicionando a imagem ao sidebar
st.sidebar.image(image_path, use_column_width=True)

# Se estiver usando uma URL
# st.sidebar.image(image_url, use_column_width=True)

