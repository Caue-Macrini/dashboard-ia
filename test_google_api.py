import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Carrega a chave de API do seu arquivo .env
project_root = Path(__file__).parent
dotenv_path = project_root / ".env"
if not dotenv_path.exists():
    print("ERRO: Arquivo .env não encontrado.")
    exit()
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERRO: Chave GEMINI_API_KEY não encontrada no .env.")
    exit()

print("--- Diagnóstico de API do Google Gemini ---")
print("Chave de API encontrada. Tentando listar modelos...")

# URL para listar os modelos disponíveis
url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

try:
    # Faz a chamada GET para listar os modelos
    response = requests.get(url )
    response.raise_for_status() # Lança erro para status 4xx/5xx

    data = response.json()
    
    print("\n--- Modelos Disponíveis para sua Chave de API ---")
    found_generative_model = False
    for model in data.get('models', []):
        # Imprime o nome de cada modelo que a sua chave pode ver
        print(f"- {model['name']}")
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            found_generative_model = True
    
    if not found_generative_model:
        print("\nAVISO: Nenhum modelo com o método 'generateContent' foi encontrado.")
        print("Isso pode indicar um problema de permissão na sua chave de API ou projeto no Google AI Studio.")
    else:
        print("\n--- Diagnóstico Concluído com Sucesso ---")
        print("Pelo menos um modelo generativo foi encontrado. Use um dos nomes da lista acima no seu código.")

except requests.exceptions.RequestException as e:
    print(f"\nERRO CRÍTICO DE REDE: {e}")
    print("Verifique sua conexão ou o patch de SSL.")
except Exception as e:
    print(f"\nERRO INESPERADO: {e}")

