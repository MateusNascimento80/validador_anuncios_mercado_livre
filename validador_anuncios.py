import streamlit as st 
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="📦 Validador de Anúncios - Mercado Livre")
st.title("📦 Validador de Anúncios - Mercado Livre")

# Palavras proibidas e sazonais
PALAVRAS_NEGATIVAS = ["promoção", "lançamento"]
PALAVRAS_SAZONAIS = ["black friday", "natal", "dia das mães", "dia dos pais", "dia dos namorados", "fim de ano", "dia das crianças"]
PALAVRAS_PI = ["nike", "adidas", "coca-cola", "disney", "marvel", "batman", "superman", "harry potter", "star wars", "brasil", "michael jackson", "beyoncé", "barbie", "dragon ball", "naruto"]

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

        campos_opcionais = ["parent_category_id", "main_color"]
        campos_obrigatorios_tenis = [
            "material", "gênero", "genero", "modelo", "tipo de calçado", "tipo de calcado"
        ]

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
            if re.search(r"\\b(preto|branco|vermelho|azul|verde|rosa|amarelo|marrom|cinza|bege|laranja)\\b", titulo):
                erros.append("Título contém cor, o que não é permitido")

            # Campos obrigatórios (exceto os opcionais)
            for col in df.columns:
                col_lower = col.lower()
                if col_lower not in campos_opcionais:
                    valor = str(row[col]).strip().lower()
                    if valor in ["", "não se aplica"]:
                        erros.append(f"Campo '{col}' está vazio ou com 'Não se aplica'")

            # Validação específica para Código universal de produto e Marca
            cup = str(row.get(mapa_colunas.get("código universal de produto", ""), "")).strip().lower()
            if cup in ["", "outro motivo"]:
                erros.append("Código universal de produto inválido")

            marca = str(row.get(mapa_colunas.get("marca", ""), "")).strip().lower()
            if marca == "sem marca":
                erros.append("Marca inválida")

            # Validação específica por categoria
            if aba_escolhida.strip().lower() == "tênis":
                for campo in campos_obrigatorios_tenis:
                    col_real = mapa_colunas.get(campo)
                    if col_real:
                        valor = str(row.get(col_real, "")).strip().lower()
                        if valor in ["", "não se aplica"]:
                            erros.append(f"Campo obrigatório para Tênis ausente ou inválido: '{col_real}'")

            resultados.append({
                "Título": row.get(col_titulo, ""),
                "Marca": marca,
                "Código universal de produto": cup,
                "Erros": "\n".join(erros),
                "Score": max(10 - len(erros), 0)
            })

        df_resultado = pd.DataFrame(resultados)

        st.markdown("### ✅ Resultado")
        st.dataframe(df_resultado, use_container_width=True)

        def converter_df(df):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return buffer.getvalue()

        excel_bytes = converter_df(df_resultado)
        st.download_button(
            label="📥 Baixar resultado em Excel",
            data=excel_bytes,
            file_name="resultado_validacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
