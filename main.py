import json
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import warnings
import logging

# Disabilita avvisi indesiderati
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# ======================================
# CONFIGURAZIONE
# ======================================
PAROLE_OFFENSIVE = [
    "incapace", "vergognoso", "fa schifo",
    "inutile", "idiota", "stupido"
]

# Parole positive e negative per riconoscimento sentimento
PAROLE_POSITIVE = [
    "chiaro", "ottimo", "molto", "disponibile", "paziente", "attento",
    "utile", "bene", "bravo", "brava", "buono", "buona", "eccellente",
    "meraviglioso", "fantastico", "grande", "perfetto", "perfetta"
]

PAROLE_NEGATIVE = [
    "difficile", "troppo veloce", "velocemente", "rapido", "scortese", "sgarbato",
    "chiaro", "non capisce", "malato", "sintetiche", "non risponde", "male",
    "cattivo", "cattiva", "brutto", "brutta", "pessimo", "pessima", "orribile"
]

# Inizializza Sentiment Analyzer e modello embeddings
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ======================================
# FUNZIONI
# ======================================
def pulisci(frase):
    """Rimuove tag tipo [3A] e normalizza il testo."""
    if not isinstance(frase, str):
        frase = str(frase)
    frase = re.sub(r"\[.*?\]", "", frase)
    return frase.lower().strip()

def è_offensiva(frase):
    """Controlla se la frase contiene parole offensive o sentiment molto negativo."""
    testo = frase.lower()
    blacklist = any(p in testo for p in PAROLE_OFFENSIVE)
    sentiment_score = sia.polarity_scores(testo)["compound"]
    troppo_negativa = sentiment_score < -0.5
    return blacklist or troppo_negativa

def get_sentimento(frase):
    """Restituisce il sentimento: 'positivo', 'negativo' o 'neutro'."""
    testo = frase.lower()
    
    # Conta parole positive e negative
    positivi_count = sum(1 for p in PAROLE_POSITIVE if p in testo)
    negativi_count = sum(1 for n in PAROLE_NEGATIVE if n in testo)
    
    # Controlla negazioni che invertono il sentimento
    negazioni = ["non ", "non s", "difficile", "troppo", "male", "non sempre"]
    ha_negazione = any(neg in testo for neg in negazioni)
    
    # Se c'è una negazione, inverti il sentimento
    if ha_negazione:
        positivi_count = 0
        negativi_count = max(negativi_count, 1)
    
    # Analizza anche con VADER
    score = sia.polarity_scores(testo)["compound"]
    
    # Combina entrambi gli approcci
    if positivi_count > negativi_count or (score > 0.05 and negativi_count == 0):
        return "positivo"
    elif negativi_count > positivi_count or score < -0.05:
        return "negativo"
    else:
        return "neutro"

def cluster_frasi(frasi, distance_threshold=1.0):
    """Raggruppa frasi simili usando embeddings e clustering."""
    if not frasi:
        return {}
    print("🤖 Calcolo embeddings...")
    embeddings = model.encode(frasi)
    
    print("🔗 Clustering frasi simili...")
    clusterer = AgglomerativeClustering(n_clusters=None, distance_threshold=distance_threshold)
    labels = clusterer.fit_predict(embeddings)
    
    clusters = {}
    for label, frase in zip(labels, frasi):
        clusters.setdefault(label, []).append(frase)
    
    return clusters

def genera_riassunto(clusters):
    """Genera il riassunto prendendo una frase rappresentativa per cluster."""
    if not clusters:
        return "Nessun feedback significativo."
    
    righe = []
    for cluster in clusters.values():
        # Prendi la frase più lunga come rappresentativa
        cluster.sort(key=lambda x: len(x), reverse=True)
        righe.append(f"- {cluster[0]}")
    return "\n".join(righe)

def genera_riassunto_diviso(positivi, negativi):
    """Genera riassunto dividendo tra positivi e negativi."""
    output = []
    
    if positivi:
        output.append("📈 FEEDBACK POSITIVI:")
        output.append(genera_riassunto(positivi))
    else:
        output.append("📈 FEEDBACK POSITIVI:")
        output.append("Nessun feedback positivo.")
    
    output.append("")
    
    if negativi:
        output.append("📉 FEEDBACK NEGATIVI:")
        output.append(genera_riassunto(negativi))
    else:
        output.append("📉 FEEDBACK NEGATIVI:")
        output.append("Nessun feedback negativo.")
    
    return "\n".join(output)

# ======================================
# MAIN
# ======================================
def main():
    try:
        # Lettura del JSON
        print("📂 Lettura del file input.json...")
        with open("input.json", "r", encoding="utf-8") as f:
            dati = json.load(f)

        # Supporta liste o dizionari
        if isinstance(dati, dict):
            frasi = []
            for value in dati.values():
                if isinstance(value, list):
                    frasi.extend(value)
                else:
                    frasi.append(str(value))
        elif isinstance(dati, list) and dati and isinstance(dati[0], dict):
            # Se è lista di oggetti con "testo" e "sentimento"
            frasi = [item["testo"] if isinstance(item, dict) else str(item) for item in dati]
        else:
            frasi = dati

        print(f"✅ Caricati {len(frasi)} commenti")

        # Pulizia testo
        print("\n🧹 Pulizia del testo...")
        frasi_pulite = [pulisci(f) for f in frasi]
        print("✅ Testo pulito")

        # Filtra frasi offensive
        print("\n🚫 Filtraggio frasi offensive...")
        frasi_filtrate = [f for f in frasi_pulite if not è_offensiva(f)]
        rimosse = len(frasi_pulite) - len(frasi_filtrate)
        print(f"✅ Rimosse {rimosse} frasi offensive")
        print(f"✅ Rimaste {len(frasi_filtrate)} frasi valide")

        if not frasi_filtrate:
            print("⚠️ Nessuna frase valida dopo il filtro!")
            return

        # Separa positivi e negativi
        print("\n📊 Separazione feedback per sentimento...")
        positivi = [f for f in frasi_filtrate if get_sentimento(f) == "positivo"]
        negativi = [f for f in frasi_filtrate if get_sentimento(f) == "negativo"]
        print(f"✅ Feedback positivi: {len(positivi)}")
        print(f"✅ Feedback negativi: {len(negativi)}")

        # Clustering frasi positive
        print("\n🔍 Clustering feedback positivi...")
        clusters_positivi = cluster_frasi(positivi) if positivi else {}
        print(f"✅ Cluster positivi: {len(clusters_positivi)}")

        # Clustering frasi negative
        print("\n🔍 Clustering feedback negativi...")
        clusters_negativi = cluster_frasi(negativi) if negativi else {}
        print(f"✅ Cluster negativi: {len(clusters_negativi)}")

        # Genera riassunto diviso
        print("\n📝 Generazione riassunto...")
        riassunto = genera_riassunto_diviso(clusters_positivi, clusters_negativi)
        print("✅ Riassunto generato")

        # Stampa e salva
        print("\n" + "="*50)
        print("📋 RISULTATO FINALE:")
        print("="*50)
        print(riassunto)
        print("="*50)

        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(riassunto)
        print("\n💾 File 'output.txt' salvato con successo!")

    except FileNotFoundError as e:
        print(f"❌ ERRORE: File non trovato - {e}")
    except json.JSONDecodeError as e:
        print(f"❌ ERRORE: File JSON non valido - {e}")
    except Exception as e:
        print(f"❌ ERRORE INASPETTATO: {e}")

# ======================================
# ESECUZIONE
# ======================================
if __name__ == "__main__":
    main()
