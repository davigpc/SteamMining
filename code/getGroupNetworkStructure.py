import os
import sys
import time
import random
import requests
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# --- ETAPA 0: Configuração ---

API_KEY = ""
GML_FILE_PATH = "networks/rede_steam_bannerlord_group.gml"

# --- Funções Auxiliares ---

def get_owned_games(steamid, api_key):
    """Busca os jogos de um usuário na API da Steam."""
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "include_appinfo": False,
        "include_played_free_games": True,
        "format": "json"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()  # Lança um erro para respostas HTTP ruins (4xx ou 5xx)
        data = res.json()
        if "games" in data.get("response", {}):
            return data["response"]["games"]
    except requests.exceptions.RequestException as e:
        print(f"  [AVISO] Erro ao buscar jogos para o ID {steamid}: {e}")
    return []

def jaccard_similarity(set1, set2):
    """Calcula a similaridade de Jaccard entre dois conjuntos."""
    if not isinstance(set1, set) or not isinstance(set2, set):
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union != 0 else 0.0

# --- Início do Script Principal ---

if __name__ == "__main__":
    

    # Criação de pastas para os resultados
    os.makedirs("datasets", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    


# --- Início do Script Principal ---
if __name__ == "__main__":

    # --- ETAPA 1: Carregamento dos Dados ---
    print("--- ETAPA 1: Carregamento e Amostragem Híbrida dos Dados ---")
    try:
        G_full = nx.read_gml(GML_FILE_PATH)
        print(f"Grafo '{GML_FILE_PATH}' carregado com sucesso: {G_full.number_of_nodes()} nós e {G_full.number_of_edges()} arestas.")
    except FileNotFoundError:
        print(f"[ERRO] Arquivo do grafo não encontrado em: '{GML_FILE_PATH}'")
        sys.exit()

    # --- INÍCIO DA LÓGICA DE AMOSTRAGEM HÍBRIDA ---
    
    print("--- ETAPA 1: Carregamento do Grafo Completo ---")
    try:
        G_full = nx.read_gml(GML_FILE_PATH)
        print(f"Grafo '{GML_FILE_PATH}' carregado com sucesso: {G_full.number_of_nodes()} nós e {G_full.number_of_edges()} arestas.")
    except FileNotFoundError:
        print(f"[ERRO] Arquivo do grafo não encontrado em: '{GML_FILE_PATH}'")
        sys.exit()
    
    G = G_full.copy()
    print("\nAnalisando o grafo completo.")
    
    print(f"Grafo de trabalho tem {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")

    # --- ETAPA 2: Coleta e Estruturação dos Dados (KDD Passos 1 e 2) ---
    print("\n--- ETAPA 2: Coleta de Dados da API e Estruturação ---")
    
    user_data = []
    total_nodes = G.number_of_nodes()
    for i, node_id in enumerate(G.nodes()):
        print(f"Processando nó {i+1}/{total_nodes} (ID: {node_id})...")
        
        # Coleta de dados da API
        jogos_raw = get_owned_games(node_id, API_KEY)
        set_jogos = {jogo['appid'] for jogo in jogos_raw}
        
        # Cálculo das métricas da rede
        user_data.append({
            "steamid": node_id,
            "grau": G.degree(node_id),
            "centralidade_grau": nx.degree_centrality(G)[node_id],
            "coef_cluster": nx.clustering(G)[node_id],
            "total_jogos": len(set_jogos),
            "set_jogos": set_jogos
        })
        time.sleep(1.2) # Pausa para respeitar os limites da API Steam

    df_users = pd.DataFrame(user_data).set_index("steamid")
    df_users_to_save = df_users
    df_users_to_save.to_csv("datasets/steam_users_dataset.csv")
    df_users_to_save = df_users.drop(columns=['set_jogos'])
    print("\nDataset de USUÁRIOS criado e salvo em 'datasets/steam_users_dataset.csv'")
    
    # --- ETAPA 3: Análise Exploratória (KDD Passos 3 e 4) ---
    print("\n--- ETAPA 3: Análise Exploratória dos Dados dos Usuários ---")

    print("\n[PASSO 3.1] Descrição Semântica dos Atributos:")
    print(" - grau: Número de conexões diretas (amigos) que um usuário tem na rede.")
    print(" - centralidade_grau: Grau normalizado; indica a importância relativa do usuário.")
    print(" - coef_cluster: Mede o quão conectados os vizinhos de um usuário estão entre si.")
    print(" - total_jogos: Quantidade total de jogos distintos que o usuário possui.")

    print("\n[PASSO 3.2] Estatísticas Descritivas Básicas:")
    print(df_users_to_save.describe())

    print("\n[PASSO 3.3] Visualizando a distribuição dos atributos...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Distribuição dos Atributos dos Usuários', fontsize=16)
    sns.histplot(df_users_to_save['grau'], bins=20, ax=axes[0, 0], kde=True).set_title('Distribuição do Grau')
    sns.histplot(df_users_to_save['centralidade_grau'], bins=20, ax=axes[0, 1], kde=True).set_title('Distribuição da Centralidade de Grau')
    sns.histplot(df_users_to_save['coef_cluster'], bins=20, ax=axes[1, 0], kde=True).set_title('Distribuição do Coef. de Cluster')
    sns.histplot(df_users_to_save['total_jogos'], bins=20, ax=axes[1, 1], kde=True).set_title('Distribuição do Total de Jogos')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("images/distribuicao_atributos_usuarios.png")
    plt.close()
    print("Gráfico de distribuição salvo em 'images/distribuicao_atributos_usuarios.png'")

    print("\n[PASSO 3.4] Analisando correlação entre atributos do usuário...")
    correlation_matrix_users = df_users_to_save.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix_users, annot=True, cmap='viridis', fmt=".2f")
    plt.title('Mapa de Calor da Correlação (Atributos de Usuário)')
    plt.savefig("images/correlacao_atributos_usuarios.png")
    plt.close()
    print("Gráfico de correlação salvo em 'images/correlacao_atributos_usuarios.png'")


    # --- ETAPA 5: Mineração e Análise da Hipótese (KDD Passo 8) ---
    print("\n--- ETAPA 5: Análise da Hipótese (Similaridade de Jogos vs. Conexões) ---")
    
    connection_data = []
    for u, v in G.edges():
        if u in df_users.index and v in df_users.index:
            jogos_u = df_users.loc[u]['set_jogos']
            jogos_v = df_users.loc[v]['set_jogos']
            
            similaridade = jaccard_similarity(jogos_u, jogos_v)
            media_centralidade = (df_users.loc[u]['centralidade_grau'] + df_users.loc[v]['centralidade_grau']) / 2
            
            media_coef_cluster = (df_users.loc[u]['coef_cluster'] + df_users.loc[v]['coef_cluster']) / 2
            
            connection_data.append({
                "usuario_u": u,
                "usuario_v": v,
                "similaridade_jaccard": similaridade,
                "media_centralidade_grau": media_centralidade,
                "media_coef_cluster": media_coef_cluster 
            })

    df_conexoes = pd.DataFrame(connection_data)
    df_conexoes.to_csv("datasets/steam_connections_dataset.csv", index=False)
    df_conexoes = df_conexoes.drop(columns=['usuario_u'])
    df_conexoes = df_conexoes.drop(columns=['usuario_v'])
    print("Dataset de CONEXÕES criado e salvo em 'datasets/steam_connections_dataset.csv'")

    print("\n[PASSO 5.1] Analisando correlação para as conexões...")
    correlation_matrix_connections = df_conexoes.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix_connections, annot=True, cmap='magma', fmt=".2f")
    plt.title('Correlação Geral das Métricas de Conexão')
    plt.savefig("images/correlacao_geral_conexoes.png") 
    plt.close()
    print("Gráfico de correlação geral salvo em 'images/correlacao_geral_conexoes.png'")

    # --- VISUALIZAÇÃO DAS HIPÓTESES ---
    # Gráfico 1: Hipótese Original (Similaridade vs. Centralidade)
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_conexoes, x='media_centralidade_grau', y='similaridade_jaccard', 
                scatter_kws={'alpha':0.4}, line_kws={'color': 'red'})
    plt.title('Hipótese 1: Similaridade de Jogos vs. Centralidade')
    plt.xlabel('Média da Centralidade de Grau na Conexão')
    plt.ylabel('Similaridade de Jaccard dos Jogos')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("images/scatterplot_similaridade_vs_centralidade.png") 
    plt.close()

    # Gráfico 2: Nova Hipótese (Similaridade vs. Cluster)
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_conexoes, x='media_coef_cluster', y='similaridade_jaccard', 
                scatter_kws={'alpha':0.4, 'color': 'purple'}, line_kws={'color': 'black'})
    plt.title('Hipótese 2: Similaridade de Jogos vs. Coeficiente de Cluster')
    plt.xlabel('Média do Coeficiente de Cluster na Conexão')
    plt.ylabel('Similaridade de Jaccard dos Jogos')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("images/scatterplot_similaridade_vs_cluster.png") 
    plt.close()
    print("Gráficos de dispersão para as hipóteses salvos.")

else:
    print("\n[AVISO] Nenhuma conexão foi encontrada na amostra de nós selecionada.")

print("\n✅ Análise KDD concluída com sucesso!")