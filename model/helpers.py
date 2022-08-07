import string
import re
import unidecode
import nltk 
from nltk.stem.rslp import RSLPStemmer

stemmer = RSLPStemmer()

def preprocessing(instancia):

    punct = string.punctuation
    trantab = str.maketrans(punct, len(punct)*' ')
    
    instancia = instancia.lower()
    instancia = re.sub('\d+', '', str(instancia)).replace("&gt;"," ").replace("&lt;"," ") 
    instancia = re.sub(r"https?:\/\/\S+","", instancia)
    instancia = re.sub(r"@[A-Za-z0-9\w]+","", instancia)
    instancia = re.sub(r"#[A-Za-z0-9\w]+","", instancia)
    instancia = re.sub('^RT ',' ',instancia)
    instancia = re.sub(r"http\S+", "", instancia) 
    instancia = re.sub(r'([A-Za-z])\1{2,}', r'\1', instancia)
    instancia = instancia.translate(trantab).replace("\n"," ")
    instancia = unidecode.unidecode(instancia)

    # #Lista de  stopwords no idioma portugues
    stopwords = [unidecode.unidecode(w) for w in list(set(nltk.corpus.stopwords.words('portuguese')))]

    # #guarda no objeto palavras
    palavras = [i for i in instancia.split() if not i in stopwords]
    
    palavras = [re.sub(r'(ha)\1+', r'\1',word) for word in palavras]
    palavras = [re.sub(r'(uha)\1+', r'\1',word) for word in palavras]
    palavras = [stemmer.stem(word) for word in palavras]

    palavras = " ".join(palavras) \
        .strip() \
        .replace('"','') \
        .replace('.','') \
        .replace('-','') \
        .replace('_','') \
        .replace('*','') \
        .replace('>','') \
        .replace('<','') \
        .replace('!','') \
        .replace('?','') \
        .replace('[','') \
        .replace(']','') \
        .replace('\'','') \
        .replace('rt ','')

    return "-" if palavras.strip()=="" else palavras.strip()


    