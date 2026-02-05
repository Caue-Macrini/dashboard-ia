# em app/modules/indicators.py

import pandas as pd

def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calcula o Índice de Força Relativa (RSI) para um dado DataFrame.

    Args:
        data (pd.DataFrame): DataFrame com uma coluna 'Fechamento'.
        period (int): O período para o cálculo do RSI (padrão é 14).

    Returns:
        pd.DataFrame: O DataFrame original com uma coluna 'RSI' adicionada.
    """
    # Calcula a diferença de preço de um dia para o outro
    delta = data['Fechamento'].diff()

    # Separa os ganhos (valores positivos) e as perdas (valores negativos)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    # Calcula a Força Relativa (RS)
    rs = gain / loss

    # Calcula o RSI
    rsi = 100 - (100 / (1 + rs))
    
    # Adiciona a coluna RSI ao DataFrame
    data['RSI'] = rsi
    
    return data
