import networkx as nx
import community as community_louvain
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd

# --- 1. Carregar o seu grafo GML ---
gml_file_path = r'\networks\rede_steam_bannerlord_group.gml'

try:
    G = nx.read_gml(gml_file_path)
    print(f"✅ Grafo '{gml_file_path}' carregado com sucesso!")
    print(f"   - Número de nós: {G.number_of_nodes()}")
    print(f"   - Número de arestas: {G.number_of_edges()}")
except FileNotFoundError:
    print(f"❌ ERRO: O arquivo não foi encontrado no caminho especificado.")
    exit()

# --- 2. Aplicar o Método de Louvain ---
if nx.is_directed(G):
    G_undirected = G.to_undirected()
else:
    G_undirected = G

print("\n🚀 Aplicando o Método de Louvain para detectar comunidades...")
partition = community_louvain.best_partition(G_undirected)
num_communities = len(set(partition.values()))
print(f"🎉 Detecção concluída! Foram encontradas {num_communities} comunidades.")
nx.set_node_attributes(G, partition, 'community_id')

# --- FILTRAR PELAS 10 MAIORES COMUNIDADES ---
print("\n🔍 Filtrando pelas 10 maiores comunidades para a visualização...")

community_series = pd.Series(partition)
community_counts = community_series.value_counts()

# Pegar o ID das 10 maiores comunidades
top_10_community_ids = community_counts.head(10).index.tolist()

nodes_to_keep = [node for node, community_id in partition.items() if community_id in top_10_community_ids]

subgraph = G.subgraph(nodes_to_keep)

print(f"✅ Subgrafo criado com as 10 maiores comunidades.")
print(f"   - Nós no subgrafo: {subgraph.number_of_nodes()}")
print(f"   - Arestas no subgrafo: {subgraph.number_of_edges()}")


# --- 3. Visualizar o SUBGRAFO ---
print("\n🎨 Gerando a visualização do SUBGRAFO...")

pos = nx.spring_layout(subgraph, iterations=50)

subgraph_partition = {node: data['community_id'] for node, data in subgraph.nodes(data=True)}
subgraph_community_ids = list(subgraph_partition.values())

cmap = cm.get_cmap('viridis', max(subgraph_community_ids) + 1)

plt.figure(figsize=(20, 20))

nx.draw_networkx_nodes(subgraph, pos, node_size=20, cmap=cmap, node_color=subgraph_community_ids)
nx.draw_networkx_edges(subgraph, pos, alpha=0.3, width=0.5)

plt.title("Visualização das 10 Maiores Comunidades (Método de Louvain)", fontsize=24)
plt.axis('off')

# Nome do arquivo de saída atualizado (MUDANÇA AQUI)
output_image_file = "visualizacao_top10_comunidades.png"
plt.savefig(output_image_file, dpi=300, bbox_inches='tight')

print(f"\n✅ Visualização das top 10 comunidades salva com sucesso no arquivo '{output_image_file}'!")