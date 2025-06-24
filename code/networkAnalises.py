import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


try:
    G = nx.read_gml("networks/rede_steam_bannerlord_group.gml")
    print("Grafo carregado com sucesso.")
except FileNotFoundError:
    print("Arquivo não encontrado.")


# --- Análises Originais ---

print(f"Número de vértices: {G.number_of_nodes()}")
print(f"Número de arestas: {G.number_of_edges()}")

# Distribuição de graus
graus = [grau for _, grau in G.degree()]
plt.hist(graus, bins=range(1, max(graus)+2), edgecolor='black')
plt.title("Distribuição de graus dos usuários")
plt.xlabel("Grau")
plt.ylabel("Frequência")
plt.savefig("images/Freq_dist_group.png", dpi=300, bbox_inches='tight')
plt.show()

clustering = nx.average_clustering(G)
print(f"Coeficiente médio de clustering: {clustering:.4f}")

centralidade_grau = nx.degree_centrality(G)

# Centralidade eigenvector
try:
    centralidade_eigen = nx.eigenvector_centrality(G, max_iter=1000)
except nx.NetworkXException as e:
    print(f"Erro no cálculo da centralidade eigenvector: {e}")
    centralidade_eigen = {n: 0 for n in G.nodes()} # Define como 0 se falhar

# Pega os 10 usuários com maior centralidade de eigenvector
top_eigen_nodes = sorted(centralidade_eigen.items(), key=lambda x: x[1], reverse=True)[:50]

print("\nTop 10 usuários por centralidade eigenvector:")
for steam_id, valor in top_eigen_nodes:
    print(f"   - ID do Usuário: {steam_id}, Centralidade: {valor:.4f}")


# --- Amostragem do Grafo para Visualização ---

N_PRINCIPAIS = 5

top_nodes_ids = [node_id for node_id, _ in top_eigen_nodes[:N_PRINCIPAIS]]

# Cria um subgrafo contendo os nós principais e seus vizinhos diretos (ego graph)
# Usamos nx.compose_all para unir os ego graphs de cada um dos nós principais
ego_graphs = [nx.ego_graph(G, node) for node in top_nodes_ids]
H = nx.compose_all(ego_graphs)

print(f"\nCriando um subgrafo para visualização a partir dos {N_PRINCIPAIS} nós mais centrais.")
print(f"   - O subgrafo tem {H.number_of_nodes()} nós e {H.number_of_edges()} arestas.")


# --- Visualização do Subgrafo ---

print("\nGerando a visualização do subgrafo... Isso pode levar alguns segundos.")

# Define o tamanho dos nós no novo grafo baseado na sua centralidade de grau no grafo ORIGINAL
# Isso mantém a proporção de importância original
tamanhos_subgraph = [centralidade_grau.get(n, 0) * 3000 for n in H.nodes()]

# Os top nós vão ser vermelhos
cores_nos = ['#ff4747' if n in top_nodes_ids else '#3b7dd8' for n in H.nodes()]

pos_subgraph = nx.spring_layout(H, seed=42, k=0.7) # Ajuste 'k' para afastar/aproximar os nós

plt.figure(figsize=(16, 12))
nx.draw(H,
        pos_subgraph,
        node_size=tamanhos_subgraph,
        node_color=cores_nos,
        edge_color='#cccccc',
        with_labels=False,
        width=0.7)


labels = {}
nx.draw_networkx_labels(H, pos_subgraph, labels=labels, font_size=12, font_color='black', font_weight='bold')

plt.title(f"Subgrafo da Rede Steam (Baseado nos {N_PRINCIPAIS} Usuários Mais Centrais)", fontsize=20)
plt.figtext(0.5, 0.01, 'Nós vermelhos são os usuários mais centrais. O tamanho dos nós é proporcional à sua centralidade de grau.', ha='center', fontsize=12)
plt.savefig("images/subgrafo_steam_visualizacao.png", dpi=300, bbox_inches='tight')
plt.show()

print("\nGráfico do subgrafo salvo como 'subgrafo_steam_visualizacao.png'")