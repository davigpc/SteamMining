import pandas as pd

# Corrigido para usar a função pd.read_csv
df = pd.read_csv('jogos_mais_frequentes.csv')

# Exibe as primeiras linhas do DataFrame
print(df['players_with_game'].head(15))
