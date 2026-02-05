import ssl
import certifi
import os

def configure_ssl():
    """
    Configura o SSL para usar o pacote certifi, que fornece um conjunto
    atualizado de certificados de autoridade de certificação (CA).
    Isso ajuda a resolver erros de 'CERTIFICATE_VERIFY_FAILED' em alguns ambientes.
    """
    try:
        # Define as variáveis de ambiente para que a biblioteca 'requests' (usada pela alpha-vantage)
        # saiba onde encontrar o pacote de certificados correto.
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        print("Configuração SSL aplicada com sucesso usando certifi.")
    except Exception as e:
        print(f"Falha ao configurar SSL com certifi: {e}")

