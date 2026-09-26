import streamlit as st
import spacy
import pandas as pd
import plotly.express as px
import os

# 1. Carregamento do modelo spaCy com tratamento de cache
@st.cache_resource
def carregar_spacy():
    try:
        return spacy.load("pt_core_news_sm")
    except OSError:
        from spacy.cli import download
        download("pt_core_news_sm")
        return spacy.load("pt_core_news_sm")

nlp = carregar_spacy()

# 2. Configuração da Interface (Streamlit)
st.set_page_config(page_title="Gestor Avançado de Reclamações", page_icon="📈", layout="wide")
st.title("📈 Sistema Inteligente de Análise e Gestão de Feedbacks")
st.markdown("Ferramenta com **Streamlit**, **spaCy** e gráficos interativos em **Plotly** para equipas de Marketing.")

# 3. Dicionários Base Expandidos (Geridos em Session State)
if "palavras_positivas" not in st.session_state:
    st.session_state.palavras_positivas = {
        "bom", "ótimo", "excelente", "maravilhoso", "gostar", "recomendar", "perfeito", 
        "rápido", "eficiente", "adorar", "feliz", "qualidade", "amei", "parabéns", 
        "satisfação", "satisfeito", "super", "top", "legal", "agil", "agilidade", 
        "atencioso", "educado", "recomendo", "fantástico", "impecável", "nota", "adorei", "cordial"
    }

if "palavras_negativas" not in st.session_state:
    st.session_state.palavras_negativas = {
        "ruim", "péssimo", "péssima", "horrível", "horrivel", "pior", "defeituoso", 
        "defeito", "falha", "falhando", "quebrado", "estragado", "danificado", 
        "viciado", "amassado", "manchado", "sujo", "imundicie", "fraquíssimo", 
        "fraco", "lixo", "porcaria", "ineficiente", "inútil", "inutilizável",
        "grosseiro", "maleducado", "arrogante", "ignorante", "ignoraram", 
        "desrespeito", "desrespeitoso", "atrasado", "atraso", "demorado", "demora", 
        "lento", "lentidão", "negligência", "negligente", "incompetente", "incompetência", 
        "sumido", "perdido", "descaso", "falsas", "promessas", "odiar", "odeio", 
        "detestar", "detestei", "frustrado", "frustrante", "decepcionado", "decepcionante", 
        "decepção", "raiva", "chateado", "irritado", "indgnado", "revoltado", 
        "arrependido", "arrependimento", "enganado", "lesado", "prejudicado", "estressante",
        "caro", "absurdo", "abusivo", "roubo", "furto", "propaganda", "enganosa", 
        "mentira", "mentiroso", "falso", "inaceitável", "lamentável", "vergonha", 
        "vergonhoso", "cancelar", "cancelamento", "problema", "problemas", "dor", 
        "cabeça", "trabalheira", "nunca", "jamais", "mal", "errado"
    }

# 4. Barra Lateral para Gestão de Dicionários
with st.sidebar:
    st.header("⚙️ Gestão de Dicionário")
    st.write("Adicione novas palavras-chave para refinar a precisão:")
    
    nova_pos = st.text_input("Adicionar Palavra Positiva:")
    if st.button("Registar Positiva"):
        if nova_pos.strip():
            st.session_state.palavras_positivas.add(nova_pos.strip().lower())
            st.success(f"'{nova_pos}' adicionada com sucesso!")
            
    nova_neg = st.text_input("Adicionar Palavra Negativa:")
    if st.button("Registar Negativa"):
        if nova_neg.strip():
            st.session_state.palavras_negativas.add(nova_neg.strip().lower())
            st.success(f"'{nova_neg}' adicionada com sucesso!")

    st.divider()
    st.markdown(f"**Total Positivas:** {len(st.session_state.palavras_positivas)}")
    st.markdown(f"**Total Negativas:** {len(st.session_state.palavras_negativas)}")

# 5. Entrada de Dados Principal
comentario = st.text_area(
    "Insira o comentário ou relatório de reclamações do cliente:",
    height=150,
    placeholder="Ex: O atendimento foi cordial e rápido, mas o produto apresentou defeito."
)

if st.button("🚀 Analisar e Gerar Gráficos", type="primary"):
    if comentario.strip():
        # Processamento via spaCy
        doc = nlp(comentario)
        
        sentencoes_analisadas = []
        pontuacao_total = 0
        qtd_positivos = 0
        qtd_negativos = 0
        qtd_neutros = 0
        
        for sent in doc.sents:
            frase_texto = sent.text.strip()
            if not frase_texto:
                continue
                
            pontuacao_frase = 0
            termos_encontrados_frase = []
            
            for token in sent:
                if token.is_punct or token.is_space:
                    continue
                
                lemma = token.lower_
                if lemma in st.session_state.palavras_positivas:
                    pontuacao_frase += 1
                    termos_encontrados_frase.append(token.text)
                elif lemma in st.session_state.palavras_negativas:
                    pontuacao_frase -= 1
                    termos_encontrados_frase.append(token.text)
            
            if pontuacao_frase > 0:
                status_frase = "Positivo 🟢"
                qtd_positivos += 1
            elif pontuacao_frase < 0:
                status_frase = "Negativo 🔴"
                qtd_negativos += 1
            else:
                status_frase = "Neutro ⚪"
                qtd_neutros += 1
                
            pontuacao_total += pontuacao_frase
            sentencoes_analisadas.append({
                "Frase": frase_texto,
                "Sentimento": status_frase,
                "Termos Chave": ", ".join(termos_encontrados_frase) if termos_encontrados_frase else "Nenhum"
            })

        # Sentimento Global
        if pontuacao_total > 0:
            sentimento_global = "POSITIVO 🟢"
        elif pontuacao_total < 0:
            sentimento_global = "NEGATIVO 🔴"
        else:
            sentimento_global = "NEUTRO ⚪"

        # Salvamento Automático em CSV
        novo_registro = pd.DataFrame({
            "Texto Analisado": [comentario],
            "Sentimento Global": [sentimento_global],
            "Frases Positivas": [qtd_positivos],
            "Frases Negativas": [qtd_negativos],
            "Frases Neutras": [qtd_neutros]
        })
        
        arquivo_csv = "historico_reclamacoes.csv"
        if os.path.exists(arquivo_csv):
            novo_registro.to_csv(arquivo_csv, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            novo_registro.to_csv(arquivo_csv, mode='w', header=True, index=False, encoding='utf-8-sig')

        # 6. Exibição de Métricas Visuais Limpas (Dashboard)
        st.divider()
        st.subheader("📊 Resumo Executivo")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sentimento Global", sentimento_global)
        col2.metric("Frases Positivas", qtd_positivos)
        col3.metric("Frases Negativas", qtd_negativos)
        col4.metric("Frases Neutras", qtd_neutros)

        # 7. Gráfico Gráfico Profissional com Plotly
        st.divider()
        st.subheader("🎨 Gráfico Interativo de Distribuição")
        
        df_grafico = pd.DataFrame({
            "Sentimento": ["Positivo", "Negativo", "Neutro"],
            "Quantidade": [qtd_positivos, qtd_negativos, qtd_neutros],
            "Cor": ["#2ecc71", "#e74c3c", "#95a5a6"]
        })
        
        # Criação do gráfico de barras estilizado via Plotly
        fig = px.bar(
            df_grafico, 
            x="Sentimento", 
            y="Quantidade", 
            color="Sentimento",
            color_discrete_map={"Positivo": "#2ecc71", "Negativo": "#e74c3c", "Neutro": "#95a5a6"},
            text="Quantidade"
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        # 8. Tabela Detalhada por Frases
        st.divider()
        st.subheader("🔍 Análise Detalhada Frase a Frase")
        st.dataframe(sentencoes_analisadas, use_container_width=True)
        
        st.success("💾 Análise guardada e processada visualmente com sucesso!")

    else:
        st.error("Por favor, insira um texto para realizar a análise.")

# 9. Histórico e Download
st.divider()
st.subheader("📁 Histórico de Reclamações Guardadas")
if os.path.exists("historico_reclamacoes.csv"):
    df_historico = pd.read_csv("historico_reclamacoes.csv")
    st.dataframe(df_historico, use_container_width=True)
    
    with open("historico_reclamacoes.csv", "rb") as f:
        st.download_button(
            label="📥 Descarregar Histórico Completo (CSV)",
            data=f,
            file_name="historico_reclamacoes.csv",
            mime="text/csv"
        )
else:
    st.info("Ainda não existem reclamações guardadas no histórico.")