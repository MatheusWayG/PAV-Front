# frontend/api_client.py
import requests

BASE_URL = "http://127.0.0.1:8000"  # Endereço do backend (Exemplo, a mudar)

def buscar_dados_do_backend():
    try:
        response = requests.get(f"{BASE_URL}/api/dados")
        if response.status_code == 200:
            return response.json()
        return {"erro": "Falha ao carregar dados do servidor"}
    except requests.exceptions.ConnectionError:
        return {"erro": "Não foi possível conectar ao backend"}