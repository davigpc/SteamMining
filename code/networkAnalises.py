import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Carrega o grafo salvo
# Certifique-se que o arquivo "rede_steam_bannerlord_group.gml" está no mesmo diretório
try:
    G = nx.read_gml("rede_steam_bannerlord_group.gml")
    print("✅ Grafo 'rede_steam_bannerlord_group.gml' carregado com sucesso.")
except FileNotFoundError:
    print("⚠️ Arquivo 'rede_steam_bannerlord_group.gml' não encontrado.")
    print("Por favor, certifique-se de que o arquivo está no mesmo diretório que o script.")
    # Criando um grafo de exemplo para o código não quebrar
    G = nx.barabasi_albert_graph(1000, 5, seed=42) # Um exemplo maior
    print("\nUsando um grafo de exemplo para demonstração.")


# --- Análises Originais ---

# Número de nós e arestas
print(f"🔢 Número de vértices: {G.number_of_nodes()}")
print(f"🔗 Número de arestas: {G.number_of_edges()}")

# Distribuição de graus
graus = [grau for _, grau in G.degree()]
plt.hist(graus, bins=range(1, max(graus)+2), edgecolor='black')
plt.title("Distribuição de graus dos usuários")
plt.xlabel("Grau")
plt.ylabel("Frequência")
plt.show()

# Coeficiente de clustering
clustering = nx.average_clustering(G)
print(f"📈 Coeficiente médio de clustering: {clustering:.4f}")

# Centralidade de grau
centralidade_grau = nx.degree_centrality(G)

# Centralidade eigenvector (pode falhar se o grafo for desconexo)
try:
    # Aumentar o número máximo de iterações para ajudar na convergência
    centralidade_eigen = nx.eigenvector_centrality(G, max_iter=1000)
except nx.NetworkXException as e:
    print(f"⚠️ Erro no cálculo da centralidade eigenvector: {e}")
    centralidade_eigen = {n: 0 for n in G.nodes()} # Define como 0 se falhar

# Pega os 10 usuários com maior centralidade de eigenvector
top_eigen_nodes = sorted(centralidade_eigen.items(), key=lambda x: x[1], reverse=True)[:10]

print("\n🔝 Top 10 usuários por centralidade eigenvector:")
for steam_id, valor in top_eigen_nodes:
    print(f"   - ID do Usuário: {steam_id}, Centralidade: {valor:.4f}")


# --- Amostragem do Grafo para Visualização ---

# Define o número de nós principais que queremos usar como semente para o nosso subgrafo
N_PRINCIPAIS = 5

# Pega os IDs dos top N nós
top_nodes_ids = [node_id for node_id, _ in top_eigen_nodes[:N_PRINCIPAIS]]

# Cria um subgrafo contendo os nós principais e seus vizinhos diretos (ego graph)
# Usamos nx.compose_all para unir os ego graphs de cada um dos nós principais
ego_graphs = [nx.ego_graph(G, node) for node in top_nodes_ids]
H = nx.compose_all(ego_graphs)

print(f"\n📊 Criando um subgrafo para visualização a partir dos {N_PRINCIPAIS} nós mais centrais.")
print(f"   - O subgrafo tem {H.number_of_nodes()} nós e {H.number_of_edges()} arestas.")


# --- Visualização do Subgrafo ---

print("\n🎨 Gerando a visualização do subgrafo... Isso pode levar alguns segundos.")

# Define o tamanho dos nós no novo grafo baseado na sua centralidade de grau no grafo ORIGINAL
# Isso mantém a proporção de importância original
tamanhos_subgraph = [centralidade_grau.get(n, 0) * 3000 for n in H.nodes()]

# Define a cor dos nós: os "top" nós serão de uma cor diferente
cores_nos = ['#ff4747' if n in top_nodes_ids else '#3b7dd8' for n in H.nodes()]

# Usa o layout spring para a visualização
pos_subgraph = nx.spring_layout(H, seed=42, k=0.7) # Ajuste 'k' para afastar/aproximar os nós

plt.figure(figsize=(16, 12))
nx.draw(H,
        pos_subgraph,
        node_size=tamanhos_subgraph,
        node_color=cores_nos,
        edge_color='#cccccc',
        with_labels=False,
        width=0.7)

# Adiciona rótulos apenas para os nós principais para não poluir o gráfico
labels = {}
nx.draw_networkx_labels(H, pos_subgraph, labels=labels, font_size=12, font_color='black', font_weight='bold')

plt.title(f"Subgrafo da Rede Steam (Baseado nos {N_PRINCIPAIS} Usuários Mais Centrais)", fontsize=20)
plt.figtext(0.5, 0.01, 'Nós vermelhos são os usuários mais centrais. O tamanho dos nós é proporcional à sua centralidade de grau.', ha='center', fontsize=12)
plt.savefig("subgrafo_steam_visualizacao.png", dpi=300, bbox_inches='tight')
plt.show()

print("\n✅ Gráfico do subgrafo salvo como 'subgrafo_steam_visualizacao.png'")