from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

print("\n--- Aplicando Análise de Sentimento com VADER ---")

# Inicializa o analisador VADER
analyzer = SentimentIntensityAnalyzer()

# Função para aplicar o VADER e retornar o score 'compound'
def get_vader_score(texto):
    return analyzer.polarity_scores(texto)['compound']

df_reviews = pd.read_csv("datasets/steam_reviews_bannerlord.csv")

# Aplica a função na coluna de texto
df_reviews['vader_score'] = df_reviews['texto_review'].apply(get_vader_score)

print("Análise com VADER concluída. Amostra dos resultados:")
print(df_reviews[['texto_review', 'foi_recomendado', 'vader_score']].head())

# Como interpretamos o score do VADER
def classificar_vader(score):
    if score >= 0.05:
        return 'pos'
    elif score <= -0.05:
        return 'neg'
    else:
        return 'neu'

df_reviews['vader_label'] = df_reviews['vader_score'].apply(classificar_vader)
print("\nDataFrame com labels do VADER:")
print(df_reviews[['texto_review', 'vader_label']].head())

print("\n--- ETAPA 6: Avaliando a Performance do VADER ---")

# --- Passo 1: Preparar os dados para comparação ---
# O VADER classifica em 'pos', 'neg' e 'neu', mas o 'foi_recomendado' é apenas True/False.
df_comparacao = df_reviews[df_reviews['vader_label'] != 'neu'].copy()

# Converte o label do VADER ('pos'/'neg') para o mesmo formato do gabarito (True/False)
df_comparacao['vader_previsao_bool'] = (df_comparacao['vader_label'] == 'pos')

# --- Passo 2: Extrair o "Gabarito" e as "Previsões" ---
y_real = df_comparacao['foi_recomendado']
y_previsto = df_comparacao['vader_previsao_bool']

# --- Passo 3: Calcular a Acurácia ---
acuracia = accuracy_score(y_real, y_previsto)
print(f"\nAcurácia do VADER: {acuracia:.2%}")
print(f"(O VADER acertou a classificação em {acuracia:.2%} das reviews não-neutras)")

# --- Passo 4: Gerar e Visualizar a Matriz de Confusão ---
cm = confusion_matrix(y_real, y_previsto)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Previsto Negativo', 'Previsto Positivo'],
            yticklabels=['Real Negativo', 'Real Positivo'])

plt.title('Matriz de Confusão - Performance do VADER', fontsize=16)
plt.ylabel('Valor Real (Avaliação do Usuário)', fontsize=12)
plt.xlabel('Previsão do VADER', fontsize=12)
plt.savefig("images/matriz_confusao_vader.png")
plt.close()

print("\nMatriz de Confusão salva em 'images/matriz_confusao_vader.png'")
print("Análise da Matriz:")
print(f"- Verdadeiros Negativos (Acerto): {cm[0][0]} reviews que eram 'Não Recomendadas' e o VADER previu como negativas.")
print(f"- Falsos Positivos (Erro): {cm[0][1]} reviews que eram 'Não Recomendadas', mas o VADER previu como positivas.")
print(f"- Falsos Negativos (Erro): {cm[1][0]} reviews que eram 'Recomendadas', mas o VADER previu como negativas.")
print(f"- Verdadeiros Positivos (Acerto): {cm[1][1]} reviews que eram 'Recomendadas' e o VADER previu como positivas.")