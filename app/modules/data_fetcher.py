import os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import requests
from functools import partial
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st 
# A biblioteca pycoingecko não é mais necessária, mas pode deixar a importação
from pycoingecko import CoinGeckoAPI

# --- Carregamento Explícito das Variáveis de Ambiente ---
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path)

# --- MONKEY PATCH GLOBAL (A ABORDAGEM CORRETA E NECESSÁRIA) ---
# Aplicamos a correção de SSL globalmente para afetar TODAS as chamadas de rede.
requests.get = partial(requests.get, verify=False)
requests.Session.get = partial(requests.Session.get, verify=False)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
print("AVISO: Verificação de certificado SSL desabilitada globalmente para requisições de rede.")

@st.cache_data
def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """
    Busca dados históricos diários de uma ação usando a API da Alpha Vantage.
    Esta função agora depende do patch de SSL global.
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Chave da API da Alpha Vantage não encontrada.")

    try:
        ts = TimeSeries(key=api_key, output_format='pandas')
        data, meta_data = ts.get_daily(symbol=symbol)

        if data is None and meta_data and "Information" in meta_data:
             st.error(f"Limite da API Alpha Vantage atingido: {meta_data['Information']}")
             return pd.DataFrame()

        data.rename(columns={
            '1. open': 'Abertura', '2. high': 'Máxima', '3. low': 'Mínima',
            '4. close': 'Fechamento', '5. volume': 'Volume'
        }, inplace=True)

        data = data.iloc[::-1]
        print(f"Dados de {symbol} carregados com sucesso!")
        return data

    except ValueError as ve:
        st.error(f"Erro da API Alpha Vantage: {ve}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro inesperado ao buscar dados da ação {symbol}: {e}")
        return pd.DataFrame()

@st.cache_data
def fetch_crypto_data(crypto_id: str, currency: str = 'brl', days: int = 100) -> pd.DataFrame:
    """
    Busca dados históricos de uma criptomoeda usando a API da CoinGecko via chamada direta com 'requests'.
    Esta abordagem é compatível com o patch de SSL global.
    """
    try:
        # Fazendo a chamada manualmente com 'requests', que já está com o patch de SSL.
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
        params = {'vs_currency': currency, 'days': str(days )}
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Lança um erro para respostas ruins (4xx ou 5xx)
        chart_data = response.json()

        prices = chart_data['prices']
        volumes = chart_data['total_volumes']

        df_prices = pd.DataFrame(prices, columns=['timestamp', 'Fechamento'])
        df_volumes = pd.DataFrame(volumes, columns=['timestamp', 'Volume'])

        df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'], unit='ms').dt.date
        df_volumes['timestamp'] = pd.to_datetime(df_volumes['timestamp'], unit='ms').dt.date

        data = pd.merge(df_prices, df_volumes, on='timestamp')
        
        data.set_index('timestamp', inplace=True)
        data.index = pd.to_datetime(data.index)

        data['Abertura'] = data['Fechamento']
        data['Máxima'] = data['Fechamento']
        data['Mínima'] = data['Fechamento']

        print(f"Dados de {crypto_id}-{currency} carregados com sucesso via CoinGecko (requests)!")
        return data

    except Exception as e:
        st.error(f"Erro ao buscar dados da CoinGecko para '{crypto_id}': {e}")
        return pd.DataFrame()
