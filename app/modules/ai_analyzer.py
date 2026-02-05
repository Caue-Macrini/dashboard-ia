import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Carregamento da chave de API
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

def generate_gemini_analysis(symbol: str, data: pd.DataFrame, sma_period: int, rsi_value: float) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "ERRO: Chave da API do Google Gemini não encontrada."

    # --- A CORREÇÃO FINAL E COMPROVADA ---
    # Usamos o modelo que o nosso script de diagnóstico encontrou.
    model_name = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }

    # Preparação dos dados do prompt
    colunas_analise = ['Fechamento', 'Volume', f'SMA_{sma_period}']
    dados_recentes = data.get(colunas_analise, pd.DataFrame( )).tail(20).to_string()
    
    prompt = f"""
    Análise Técnica do Ativo: {symbol}

    Dados para Análise:
    - Período da Média Móvel Simples (SMA): {sma_period} dias
    - Índice de Força Relativa (RSI) atual: {rsi_value:.2f} 
    - Dados Recentes (últimos 20 dias de negociação):
    {dados_recentes}

    Sua Tarefa:
    Com base EXCLUSIVAMENTE nos dados fornecidos, escreva uma análise técnica concisa em formato Markdown.
    Responda diretamente com os seguintes tópicos:

    1.  **Análise de Preço vs. Média Móvel:** O preço de fechamento atual está acima ou abaixo da média móvel? O que isso sugere sobre a tendência de curto prazo? Houve algum "cruzamento" notável?

    2.  **Análise de Volume:** Descreva se houve picos de volume e se eles coincidiram com movimentos de preço significativos (altas ou baixas).
    
    3.  **Análise do RSI:** O RSI atual ({rsi_value:.2f}) sugere que o ativo está sobrecomprado (acima de 70), sobrevendido (abaixo de 30) ou em território neutro?

    4.  **Resumo da Tendência:** Com base nos dados, a tendência recente é de alta, baixa ou lateralização?

    5.  **Conclusão Objetiva:** Forneça uma conclusão curta e objetiva sobre o comportamento do ativo, sem fazer recomendações de compra ou venda.
    """


    # Corpo (body) da requisição
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # --- EXECUÇÃO DA CHAMADA DE API ---
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        response.raise_for_status()

        response_data = response.json()
        
        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"ERRO de rede ao contatar a API do Google Gemini: {e}\nResposta: {response.text}"
    except (KeyError, IndexError) as e:
        return f"ERRO: Estrutura de resposta inesperada da API do Gemini.\nDetalhes: {e}\nResposta: {response_data}"
    except Exception as e:
        return f"ERRO inesperado ao contatar a API do Google Gemini: {e}"

