import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="📦 Validador de Anúncios - Mercado Livre")
st.title("📦 Validador de Anúncios - Mercado Livre")

# Palavras proibidas e sazonais
PALAVRAS_NEGATIVAS = ["promoção", "lançamento"]
PALAVRAS_SAZONAIS = ["black friday", "natal", "dia das mães", "dia dos pais", "dia dos namorados", "fim de ano", "dia das crianças"]
PALAVRAS_PI = [
    "nike", "adidas", "coca-cola", "disney", "marvel", "batman", "superman",
    "harry potter", "star wars", "brasil", "michael jackson", "beyoncé", "barbie",
    "dragon ball", "naruto"
]

CORES_PROIBIDAS = [
    "preto", "branco", "vermelho", "azul", "verde", "rosa", "amarelo",
    "marrom", "cinza", "bege", "laranja"
]

# Campos obrigatórios por categoria
CAMPOS_OBRIGATORIOS_POR_CATEGORIA = {
    "Tênis": [
        "material", "gênero", "modelo", "tipo de calçado"
    ]
}

# Upload
uploaded_file = st.file_uploader("📤 Envie a planilha dos anúncios (.xlsx)", type="xlsx")

if uploaded_file:
    # Carregar todas as abas
    xls = pd.ExcelFile(uploaded_file)
    abas = xls.sheet_names
    aba_escolhida = st.selectbox("📂 Selecione a categoria (aba)", abas)

    if aba_escolhida:
        df = pd.read_excel(xls, sheet_name=aba_escolhida)
        colunas = df.columns.str.lower()
        mapa_colunas = {col.lower(): col for col in df.columns}

        if "título" in colunas or "title" in colunas:
            col_titulo = mapa_colunas.get("título", mapa_colunas.get("title"))
        else:
            st.error("❌ Nenhuma coluna parecida com 'Título' foi encontrada.")
            st.markdown(f"🧪 Colunas encontradas: {list(df.columns)}")
            st.stop()

        resultados = []

        for idx, row in df.iterrows():
            erros = []
            titulo = str(row.get(col_titulo, "")).lower()

            # Verificações no título
            if len(titulo) < 55:
                erros.append("Título com menos de 55 caracteres")
            if any(p in titulo for p in PALAVRAS_NEGATIVAS):
                erros.append("Título contém palavra negativa")
            if any(s in titulo for s in PALAVRAS_SAZONAIS):
                erros.append("Título contém palavra sazonal")
            if any(p in titulo for p in PALAVRAS_PI):
                erros.append("Título contém possível propriedade intelectual (marca ou famoso)")
            if any(cor in titulo for cor in CORES_PROIBIDAS):
                erros.append("Título contém cor, o que não é permitido")

            # Verificar campos obrigatórios por categoria
