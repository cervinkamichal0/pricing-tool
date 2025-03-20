from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import requests
from io import BytesIO

# Modely pro text a obrázky
text_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", cache_folder="./models")
image_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Transformace obrázků pro CLIP


def preprocess_image(image_path_or_url):
    # Pokud je argument URL, stáhneme obrázek
    if image_path_or_url.startswith("http") | image_path_or_url.startswith("https"):
        response = requests.get(image_path_or_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        # Pokud je to lokální cesta, stahovat ho nemusíme
        image = Image.open(image_path_or_url).convert("RGB")
    
    return processor(images=image, return_tensors="pt")["pixel_values"]


def compute_similarity(user_item, user_image_path, ads):
    """
    Porovnání textu a obrázku s existujícími inzeráty.
    user_item: {"title": ..., "description": ...}
    user_image_path: cesta k nahranému obrázku
    ads: seznam inzerátů ze `data_fetcher.py`
    """

    results = []

    #1) Porovnání textu
    user_text = user_item["title"] + " " + (user_item["description"] if user_item["description"] else "")
    ad_texts = [ad["title"] + " " + (ad["description"] if ad["description"] else "") for ad in ads]

    all_texts = [user_text] + ad_texts
    text_embeddings = text_model.encode(all_texts, convert_to_tensor=True)

    text_similarities = cosine_similarity(text_embeddings[0].cpu().reshape(1, -1), text_embeddings[1:]).flatten()

    #2) Porovnání obrázků
    user_image_embedding = image_model.get_image_features(preprocess_image(user_image_path)).detach().numpy()

    image_similarities = []
    for ad in ads:
        if "images" in ad and len(ad["images"]) > 0:  # Kontrola, zda seznam obrázků není prázdný
            ad_image_embedding = image_model.get_image_features(preprocess_image(ad["images"][0])).detach().numpy()
            similarity = cosine_similarity(user_image_embedding.reshape(1, -1), ad_image_embedding.reshape(1, -1)).flatten()[0]
        else:
            similarity = 0  # Pokud inzerát nemá obrázek

        image_similarities.append(similarity)

    #3) Kombinace textu a obrázku
    for i, ad in enumerate(ads):
        combined_similarity = (text_similarities[i] * 0.7) + (image_similarities[i] * 0.3)  # 70 % text, 30 % obrázek
        results.append({
            "ad": ad,
            "similarity_score": combined_similarity
        })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results

def parse_date(date_str):
    """Detekuje a správně naparsuje datum podle formátu"""
    try:
        # ISO 8601 (např. '2025-02-28T17:24:13')
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        pass  # Pokračujeme na RFC 2822

    try:
        # RFC 2822 (např. 'Mon, 10 Mar 2025 21:10:44 +0000')
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").date()
    except ValueError:
        pass  # Pokud nevyhovuje žádný formát, vrátíme None

    return None  # Neplatné datu

def compute_price(similar_ads, quick_sale=False):
    """
    Vypočítá odhadovanou cenu na základě podobných inzerátů.
    Pokud je quick_sale=True, starší inzeráty budou mít nižší váhu.
    """
    prices = []
    weights = []

    for ad in similar_ads:
        if "price" in ad["ad"] and "date" in ad["ad"]:
            price = ad["ad"]["price"]

            date_str = ad["ad"]["date"]
            date_posted = parse_date(date_str)
            
            if date_posted is None:
                print(f"v inzerátu je špatný formát data: {ad['date']}")
                continue  # Pokud je datum nevalidní, přeskočíme záznam

            days_listed = (datetime.today().date() - date_posted).days

            # Výpočet váhy na základě stáří inzerátu
            weight = max(1.0, 30 / (days_listed + 1)) if quick_sale else 1.0
            prices.append(price)
            weights.append(weight)

    if not prices:
        return None

    # Vážený průměr
    weighted_price = sum(p * w for p, w in zip(prices, weights)) / sum(weights)
    return int(weighted_price)