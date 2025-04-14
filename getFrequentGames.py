import requests
import time
import csv
from collections import Counter

API_KEY = "A8AD4A9C9CD3A382AEE96A3B52E140C2"

def get_owned_games(steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data.get("response", {}).get("games", [])
    except Exception as e:
        print(f"Erro com {steam_id}: {e}")
        return []

# Lê os SteamIDs
with open("steam_ids.txt", "r") as f:
    steam_ids = [line.strip() for line in f.readlines()]

jogo_freq = Counter()

for i, steamid in enumerate(steam_ids):
    print(f"[{i+1}/{len(steam_ids)}] Coletando jogos de {steamid}")
    jogos = get_owned_games(steamid)
    for jogo in jogos:
        jogo_freq[(jogo["appid"], jogo["name"])] += 1
    time.sleep(0.3)  # Espera para evitar throttling da API

# Salva no CSV
with open("jogos_mais_frequentes.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["appid", "game_name", "players_with_game"])  # Cabeçalho do CSV
    for (appid, nome), freq in jogo_freq.most_common():
        writer.writerow([appid, nome, freq])  # Escreve os dados

print("\n✅ Dados salvos em 'jogos_mais_frequentes.csv'.")
