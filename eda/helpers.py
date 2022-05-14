import matplotlib.pyplot as plt
import seaborn as sns
from nltk import tokenize
import nltk
import pandas as pd


    

def pareto(palavras,filter_list,qtde):
    todas_palavras = ' '.join([' '.join([w for w in texto.split() if w not in filter_list]) for texto in palavras ])
    token_espaco = tokenize.WhitespaceTokenizer()
    token_frase = token_espaco.tokenize(todas_palavras)
    frequencia = nltk.FreqDist(token_frase)
    df_frequencias = pd.DataFrame({"Palavras": list(frequencia.keys()),
                                   "Frequencia": list(frequencia.values())})
    df_frequencias = df_frequencias.nlargest(columns = "Frequencia", n = qtde)
    total = df_frequencias['Frequencia'].sum()
    df_frequencias['Porcentagem'] = df_frequencias['Frequencia'].cumsum() / total * 100

    plt.figure(figsize=(12,8))
    plt.xticks(
        rotation=90, 
        horizontalalignment='right',
        fontweight='light',
        fontsize='x-large'  
    )   
    
    ax = sns.barplot(data=df_frequencias, x='Palavras', y='Frequencia', color='gray')
    ax2 = ax.twinx()
    sns.lineplot(data=df_frequencias, x='Palavras', y='Porcentagem', color='red', sort=False, ax=ax2)
    plt.show()