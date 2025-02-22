from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(user_item, ads):
    """
    user_item: dict obsahující {"title": ..., "description": ..., 
    ads: seznam inzerátů ze `data_fetcher.py`
    """

    results = []

    # Připravíme texty pro TF-IDF (název + popis)
    user_text = user_item["title"] + " " + user_item["description"]
    ad_texts = [ad["title"] + " " + (ad["description"] if ad["description"] else "") for ad in ads]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([user_text] + ad_texts)
    
    similarities = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()

    for i, ad in enumerate(ads):
        similarity_score = similarities[i]

        final_score = similarity_score
        
        results.append({
            "ad": ad,
            "similarity_score": final_score
        })

    # Seřadíme od nejpodobnějšího
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results
