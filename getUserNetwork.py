import os
import requests
import time
import networkx as nx
import xml.etree.ElementTree as ET

# Carregar a chave da API a partir das variáveis de ambiente
# Certifique-se de ter definido a variável de ambiente 'STEAM_API_KEY'
API_KEY = os.getenv("STEAM_API_KEY")
if not API_KEY:
    raise ValueError("A chave da API do Steam não foi definida na variável de ambiente 'STEAM_API_KEY'.")

GROUP_URL = "https://steamcommunity.com/groups/mountandbladeIIbannerlord"


# Função para extrair o ID de 64 bits de um grupo a partir de sua URL
def get_group_id(group_url: str) -> str:
    """
    Busca o XML da página do grupo para extrair o groupID de 64 bits.
    """
    xml_url = f"{group_url}/memberslistxml/?xml=1"
    print(f"Buscando GroupID de: {xml_url}")
    try:
        response = requests.get(xml_url)
        response.raise_for_status()  # Lança um erro para respostas HTTP ruins (4xx ou 5xx)
        root = ET.fromstring(response.content)
        group_id = root.find('groupID64').text
        if not group_id:
            raise ValueError("Não foi possível encontrar o groupID64 no XML.")
        print(f"GroupID encontrado: {group_id}")
        return group_id
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL do grupo: {e}")
        return None
    except ET.ParseError as e:
        print(f"Erro ao analisar o XML do grupo: {e}")
        return None


# Função para buscar todos os membros de um grupo
def get_group_members(group_id: str) -> list:
    """
    Busca todos os SteamIDs dos membros de um grupo, paginando os resultados.
    """
    all_member_ids = []
    current_page = 1
    total_pages = 1  # Inicia com 1 para entrar no loop

    print("Iniciando a busca de membros do grupo...")
    while current_page <= total_pages:
        url = f"https://steamcommunity.com/gid/{group_id}/memberslistxml/?xml=1&p={current_page}"
        try:
            res = requests.get(url)
            res.raise_for_status()

            root = ET.fromstring(res.content)

            # Atualiza o número total de páginas na primeira iteração
            if current_page == 1:
                total_pages = int(root.find('totalPages').text)
                member_count = root.find('memberCount').text
                print(f"O grupo tem {member_count} membros em {total_pages} páginas.")

            # Extrai os SteamIDs da página atual
            members = root.findall('members/steamID64')
            page_member_ids = [member.text for member in members]
            all_member_ids.extend(page_member_ids)

            print(f"Página {current_page}/{total_pages} processada. {len(page_member_ids)} membros encontrados.")

            current_page += 1
            time.sleep(0.5)  # Pausa para ser cortês com os servidores da Steam

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar a página {current_page} de membros: {e}")
            break  # Interrompe em caso de erro
        except ET.ParseError as e:
            print(f"Erro ao analisar o XML da página {current_page}: {e}")
            break

    print(f"\nBusca finalizada. Total de {len(all_member_ids)} membros carregados.")
    return all_member_ids


# Função para pegar a lista de amigos de um usuário
def get_friends(steam_id: str) -> list:
    """
    Busca a lista de amigos de um usuário específico usando a API do Steam.
    """
    url = "https://api.steampowered.com/ISteamUser/GetFriendList/v1/"
    params = {"key": API_KEY, "steamid": steam_id, "relationship": "friend"}

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        # Retorna uma lista vazia se o perfil for privado ou não tiver amigos
        return [f["steamid"] for f in data.get("friendslist", {}).get("friends", [])]
    except requests.exceptions.RequestException as e:
        # Erros de rede ou HTTP
        print(f"Erro de requisição ao buscar amigos de {steam_id}: {e}")
        return []
    except Exception as e:
        # Outros erros (ex: JSON inválido, perfil privado que retorna erro)
        print(f"Erro ao buscar amigos de {steam_id}: {e}")
        return []


# --- FLUXO PRINCIPAL ---

# 1. Obter o ID do grupo
group_id = get_group_id(GROUP_URL)

if group_id:
    # 2. Carregar a lista de todos os membros do grupo
    steam_ids = get_group_members(group_id)

    if steam_ids:
        # 3. Criar o grafo e adicionar os membros como vértices
        G = nx.Graph()
        G.add_nodes_from(steam_ids)

        print(f"\nIniciando a criação do grafo de amizades para {len(steam_ids)} membros...")

        # 4. Adicionar arestas com base em amizades mapeadas DENTRO do grupo
        for i, steam_id in enumerate(steam_ids):
            print(f"[{i + 1}/{len(steam_ids)}] Processando amizades de {steam_id}")
            friends = get_friends(steam_id)

            # Otimização: iterar apenas sobre amigos que também estão no grafo
            friends_in_group = [friend for friend in friends if friend in G]

            for friend_id in friends_in_group:
                # Adiciona a aresta (evita duplicatas automaticamente no Grafo não direcionado)
                G.add_edge(steam_id, friend_id)

            time.sleep(0.3)  # Evita atingir o limite de requisições da API

        # 5. Salvar o grafo em um arquivo (opcional)
        nx.write_gml(G, "rede_steam_bannerlord_group.gml")

        print(f"\n✅ Grafo criado com sucesso!")
        print(f"   - Vértices (membros do grupo): {G.number_of_nodes()}")
        print(f"   - Arestas (amizades dentro do grupo): {G.number_of_edges()}")
