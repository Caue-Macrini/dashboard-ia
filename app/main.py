import streamlit as st
import pandas as pd
from modules.data_fetcher import fetch_stock_data, fetch_crypto_data
# A função configure_ssl não é mais necessária se o patch estiver no data_fetcher
# from modules.utils import configure_ssl 
from modules.ai_analyzer import generate_gemini_analysis
from modules.indicators import calculate_rsi

@st.cache_data
def convert_df_to_csv(df):
    """Converte um DataFrame para CSV, codificado em UTF-8."""
    return df.to_csv(index=True).encode('utf-8')

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Análise com IA",
    page_icon="📊",
    layout="wide"
)

# --- Título ---
st.title("Análise de Ativos com IA Generativa 📈")

# --- Barra Lateral (Sidebar) ---
st.sidebar.header("Configurações")

# Seletor de Tipo de Ativo
tipo_ativo = st.sidebar.selectbox("Selecione o Tipo de Ativo", ["Ações", "Criptomoedas"])

# Lógica Condicional para a Interface
if tipo_ativo == "Ações":
    simbolo_ativo = st.sidebar.text_input("Digite o Símbolo da Ação (ex: PETR4.SA)", "PETR4.SA")
    dados_ativo = fetch_stock_data(simbolo_ativo)
    nome_completo_ativo = simbolo_ativo
else: # Criptomoedas
    simbolo_ativo = st.sidebar.text_input("Digite o ID da Cripto (ex: bitcoin)", "bitcoin")
    mercado_cripto = st.sidebar.text_input("Digite a Moeda (ex: brl ou usd)", "brl")
    dados_ativo = fetch_crypto_data(simbolo_ativo, mercado_cripto)
    nome_completo_ativo = f"{simbolo_ativo}-{mercado_cripto}"

# --- Corpo Principal ---
st.subheader(f"Exibindo dados para: {nome_completo_ativo}")

# --- Bloco Principal de Lógica: SÓ EXECUTA SE OS DADOS FOREM CARREGADOS ---
if not dados_ativo.empty:
    
    # --- FILTROS NA SIDEBAR ---
    st.sidebar.subheader("Filtros e Indicadores")
    
    # Filtro de Período
    data_inicio = st.sidebar.date_input("Data de Início", value=dados_ativo.index.min(), min_value=dados_ativo.index.min(), max_value=dados_ativo.index.max())
    data_fim = st.sidebar.date_input("Data de Fim", value=dados_ativo.index.max(), min_value=dados_ativo.index.min(), max_value=dados_ativo.index.max())

    # Seletor da Média Móvel
    periodo_media_movel = st.sidebar.number_input(
        "Período da Média Móvel (dias)", 
        min_value=1, 
        max_value=100,
        value=20
    )

    # --- PROCESSAMENTO DOS DADOS ---
    
    # 1. Filtra o DataFrame com base no intervalo de datas e cria uma cópia
    dados_filtrados = dados_ativo.loc[data_inicio:data_fim].copy()

    # 2. Calcula a Média Móvel
    dados_filtrados[f'SMA_{periodo_media_movel}'] = dados_filtrados['Fechamento'].rolling(window=periodo_media_movel).mean()
    
    # 3. Calcula o RSI
    dados_filtrados = calculate_rsi(dados_filtrados)
    
    # --- BOTÃO DE DOWNLOAD (AGORA NA POSIÇÃO CORRETA) ---
    csv_data = convert_df_to_csv(dados_filtrados)
    st.sidebar.download_button(
       label="📥 Baixar Dados como CSV",
       data=csv_data,
       file_name=f'{nome_completo_ativo}_dados.csv', # CORREÇÃO: Usando a variável correta
       mime='text/csv',
    )

    # --- EXIBIÇÃO DOS GRÁFICOS E DADOS ---

    # Estatísticas Chave
    st.subheader("Estatísticas do Período Selecionado")
    preco_maximo = dados_filtrados['Máxima'].max()
    preco_minimo = dados_filtrados['Mínima'].min()
    ultimo_preco = dados_filtrados['Fechamento'].iloc[-1]
    primeiro_preco = dados_filtrados['Fechamento'].iloc[0]
    variacao_periodo = ((ultimo_preco - primeiro_preco) / primeiro_preco) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Último Preço", value=f"R$ {ultimo_preco:,.2f}")
    col2.metric(label="Preço Máximo", value=f"R$ {preco_maximo:,.2f}")
    col3.metric(label="Preço Mínimo", value=f"R$ {preco_minimo:,.2f}")
    col4.metric(label="Variação no Período", value=f"{variacao_periodo:.2f}%")
    
    # Gráfico de Preço
    st.subheader("Gráfico de Preço com Média Móvel")
    dados_grafico_preco = dados_filtrados[['Fechamento', f'SMA_{periodo_media_movel}']]
    st.line_chart(dados_grafico_preco)

    # Gráfico de Volume
    st.subheader("Gráfico de Volume de Negociação")
    st.bar_chart(dados_filtrados['Volume'])
    
    # Gráfico do RSI
    st.subheader("Índice de Força Relativa (RSI)")
    rsi_chart_data = pd.DataFrame({
        'RSI': dados_filtrados['RSI'],
        'Sobrecomprado': 70,
        'Sobrevendido': 30
    })
    st.line_chart(rsi_chart_data, color=["#FFBF00", "#FF0000", "#00FF00"])

    # Análise com IA
    st.subheader("Análise com Inteligência Artificial")
    if st.button("Gerar Análise de IA"):
        with st.spinner("A IA está analisando os dados... Por favor, aguarde."):
            ultimo_rsi = dados_filtrados['RSI'].iloc[-1]
            
            analise_ia = generate_gemini_analysis(
                symbol=nome_completo_ativo, 
                data=dados_filtrados, 
                sma_period=periodo_media_movel,
                rsi_value=ultimo_rsi
            )
            st.markdown(analise_ia)

    # Tabela de Dados
    st.subheader("Dados Históricos Filtrados")
    st.dataframe(dados_filtrados)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Desenvolvido por Cauê Gaspar Macrini"
    )
    st.sidebar.markdown(
        "[LinkedIn](https://www.linkedin.com/in/caue-macrini) | "
        "[GitHub](https://github.com/Caue-Macrini)"
    )

else:
    st.warning("Não foi possível carregar os dados do ativo. Verifique os símbolos ou a conexão com a API.")

