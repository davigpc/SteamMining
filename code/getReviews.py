import requests
import pandas as pd
import time
from urllib.parse import quote_plus

print("Iniciando a coleta de reviews da Steam...")

# --- Configurações ---
app_id = 261550  # Bannerlord
target_reviews = 50000  # Quantos reviews queremos coletar?
reviews_por_pagina = 100 # A API permite até 100 por página

# --- Coleta com Paginação ---
reviews_coletadas = []
cursor = '*'  # O cursor inicial é um asterisco

while len(reviews_coletadas) < target_reviews:
    params = {
        "json": 1,
        "language": "english",
        "filter": "all",  # Você pode mudar para 'all', 'updated', etc.
        "num_per_page": reviews_por_pagina,
        "cursor": quote_plus(cursor) # O cursor precisa ser URL-encoded
    }
    
    try:
        url = f"https://store.steampowered.com/appreviews/{app_id}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Adiciona os reviews desta página à nossa lista
        reviews_lote_atual = data.get("reviews", [])
        if not reviews_lote_atual:
            print("Não há mais reviews para coletar.")
            break # Interrompe o loop se não vierem mais reviews
            
        for review in reviews_lote_atual:
            reviews_coletadas.append({
                'steamid': review['author']['steamid'],
                'texto_review': review['review'],
                'foi_recomendado': review['voted_up'], # True ou False
                'votos_uteis': review['votes_up'],
                'data_postagem': review['timestamp_created']
            })

        # Prepara o cursor para a próxima página
        cursor = data.get("cursor", "*")
        
        print(f"Coletados {len(reviews_coletadas)} de {target_reviews} reviews...")

        # Pausa para ser gentil com a API
        time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")
        break

# --- Criação do DataFrame ---
df_reviews = pd.DataFrame(reviews_coletadas)

# Salva em um CSV para não precisar coletar de novo
df_reviews.to_csv("datasets/steam_reviews_bannerlord.csv", index=False)

print("\n✅ Coleta concluída com sucesso!")
print(f"Total de {len(df_reviews)} reviews salvas em 'datasets/steam_reviews_bannerlord.csv'")
print("Amostra do DataFrame:")
print(df_reviews.head())