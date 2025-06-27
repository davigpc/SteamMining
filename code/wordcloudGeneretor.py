from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import nltk
import spacy
import os
import string

try:
    nlp_en = spacy.load("en_core_web_sm")
    stopwords_en = nltk.corpus.stopwords.words('english')
except OSError:
    print("Modelo 'en_core_web_sm' não encontrado. Baixando agora...")
    os.system("python -m spacy download en_core_web_sm")
    nlp_en = spacy.load("en_core_web_sm")

stopwords_en.extend(['game', 'play', 'playing', 'player', 'review', 'steam', 'mount', 'blade'])


def preprocessar_texto_en(texto):
    texto = texto.lower()
    texto = ''.join([char for char in texto if char not in string.punctuation])
    tokens = nltk.word_tokenize(texto, language='english')
    tokens = [palavra for palavra in tokens if palavra not in stopwords_en and not palavra.isdigit()]
    doc = nlp_en(' '.join(tokens))
    tokens_lemmatizados = [token.lemma_ for token in doc]
    return ' '.join(tokens_lemmatizados)

df_reviews = pd.read_csv("datasets/steam_reviews_bannerlord.csv")

if 'texto_processado' not in df_reviews.columns:
    print("Realizando pré-processamento dos textos em inglês...")
    df_reviews['texto_processado'] = df_reviews['texto_review'].apply(preprocessar_texto_en)
    print("Pré-processamento concluído.")

    texto_geral = " ".join(review for review in df_reviews['texto_processado'])

wordcloud_geral = WordCloud(
    width=800, 
    height=400, 
    background_color='white', 
    colormap='viridis',
    min_font_size=10
).generate(texto_geral)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_geral, interpolation='bilinear')
plt.axis("off")
plt.title("Nuvem de Palavras Geral", fontsize=20)
plt.savefig("images/wordcloud_geral.png")
plt.close()
print("Nuvem de palavras geral salva em 'images/wordcloud_geral.png'")

df_positivas = df_reviews[df_reviews['foi_recomendado'] == True]
df_negativas = df_reviews[df_reviews['foi_recomendado'] == False]

texto_positivo = " ".join(review for review in df_positivas['texto_processado'])
texto_negativo = " ".join(review for review in df_negativas['texto_processado'])

# Criando a figura com dois subplots, lado a lado
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# Nuvem Positiva
wordcloud_pos = WordCloud(width=800, height=800, background_color='white', colormap='Greens').generate(texto_positivo)
axes[0].imshow(wordcloud_pos, interpolation='bilinear')
axes[0].set_title('Palavras em Reviews Positivas', fontsize=20)
axes[0].axis("off")

# Nuvem Negativa
wordcloud_neg = WordCloud(width=800, height=800, background_color='black', colormap='Reds').generate(texto_negativo)
axes[1].imshow(wordcloud_neg, interpolation='bilinear')
axes[1].set_title('Palavras em Reviews Negativas', fontsize=20)
axes[1].axis("off")

plt.tight_layout(pad=0)
plt.savefig("images/wordclouds_comparativas.png")
plt.close()
print("Nuvens de palavras comparativas salvas em 'images/wordclouds_comparativas.png'")