import os
import requests
import time
import networkx as nx

# Carregar a chave da API
API_KEY = os.getenv("STEAM_API_KEY")
if not API_KEY:
    raise ValueError("A chave da API não foi definida nas variáveis de ambiente.")

# Função para pegar amigos
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

# Carregar IDs
with open("steam_ids.txt", "r") as f:
    steam_ids = [line.strip() for line in f.readlines()]

# Criar o grafo
G = nx.Graph()

# Adicionar vértices
G.add_nodes_from(steam_ids)

# Adicionar arestas com base em amizades mapeadas dentro da lista
for i, steam_id in enumerate(steam_ids):
    print(f"[{i+1}/{len(steam_ids)}] Processando {steam_id}")
    friends = get_friends(steam_id)
    for friend in friends:
        if friend in steam_ids:
            G.add_edge(steam_id, friend)  # Adiciona uma aresta se ambos estão na lista
    time.sleep(0.3)  # Evita rate limit

# Salvar grafo em arquivo (opcional)
nx.write_gml(G, "rede_steam.gml")

print(f"\n✅ Grafo criado com {G.number_of_nodes()} vértices e {G.number_of_edges()} arestas.")
