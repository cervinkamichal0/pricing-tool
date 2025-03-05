from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Použij veřejně dostupný model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./models")
# Nebo zkus přesnější model:
# model = SentenceTransformer("distiluse-base-multilingual-cased-v2")

def compute_similarity(user_item, ads):
    """
    user_item: dict obsahující {"title": ..., "description": ...}
    ads: seznam inzerátů ze `data_fetcher.py`
    """

    results = []

    # Připravíme texty (název + popis)
    user_text = user_item["title"] + " " + (user_item["description"] if user_item["description"] else "")
    ad_texts = [ad["title"] + " " + (ad["description"] if ad["description"] else "") for ad in ads]

    # Vytvoříme embeddingy
    all_texts = [user_text] + ad_texts
    embeddings = model.encode(all_texts, convert_to_tensor=True)

    # Spočítáme cosine similarity
    similarities = cosine_similarity(embeddings[0].cpu().reshape(1, -1), embeddings[1:]).flatten()

    # Seřazení výsledků
    for i, ad in enumerate(ads):
        results.append({
            "ad": ad,
            "similarity_score": similarities[i]
        })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
