import networkx as nx
import matplotlib.pyplot as plt

# Carrega o grafo salvo
G = nx.read_gml("rede_steam.gml")

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
    centralidade_eigen = nx.eigenvector_centrality(G)
except nx.NetworkXException as e:
    print(f"⚠️ Erro no cálculo da centralidade eigenvector: {e}")
    centralidade_eigen = {n: 0 for n in G.nodes()}

top_eigen = sorted(centralidade_eigen.items(), key=lambda x: x[1], reverse=True)[:10]

print("🔝 Top 10 usuários por centralidade eigenvector:")
for steam_id, valor in top_eigen:
    print(f"{steam_id}: {valor:.4f}")

# Visualização simples com centralidade de grau
tamanhos = [centralidade_grau[n] * 1000 for n in G.nodes()]
pos = nx.spring_layout(G, seed=42)  # posição fixa para visualização estável

plt.figure(figsize=(12, 8))
nx.draw(G, pos, node_size=tamanhos, node_color='skyblue', edge_color='gray', with_labels=False)
plt.title("Rede Steam - Tamanho proporcional à Centralidade de Grau")
plt.show()