import os
import requests
import time
from collections import deque

# Obtenha a chave da variável de ambiente
API_KEY = os.getenv("STEAM_API_KEY")
if not API_KEY:
    raise ValueError("A chave da API não foi definida nas variáveis de ambiente.")

START_STEAMID = "76561198130809226"  # Substitua pelo SteamID de partida
MAX_IDS = 100

def get_friends(steam_id):
    url = "https://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {"key": API_KEY, "steamid": steam_id, "relationship": "friend"}
    
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return [f["steamid"] for f in data.get("friendslist", {}).get("friends", [])]
    except Exception as e:
        print(f"Erro ao buscar amigos de {steam_id}: {e}")
        return []

def collect_steam_ids(start_steamid, max_ids):
    visited = set()
    queue = deque([start_steamid])

    while queue and len(visited) < max_ids:
        current = queue.popleft()
        if current in visited:
            continue
        
        visited.add(current)
        print(f"[{len(visited)}/{max_ids}] Coletando amigos de {current}")
        
        friends = get_friends(current)
        for f in friends:
            if f not in visited and len(visited) + len(queue) < max_ids:
                queue.append(f)

        time.sleep(0.3)  # respeita limite da API

    return list(visited)

# 🧪 Executa e salva resultado
steam_ids = collect_steam_ids(START_STEAMID, MAX_IDS)

# Salva em arquivo
with open("steam_ids.txt", "w") as f:
    for sid in steam_ids:
        f.write(f"{sid}\n")

print(f"\n✅ Coletados {len(steam_ids)} SteamIDs válidos.")
