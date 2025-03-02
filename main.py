from data_fetcher import fetch_all_ads
from similarity import compute_similarity

def main():
    # Simulace uživatelského vstupu
    user_item = {
        "title": "Mercedes-Benz E 220",
        "description": "Prodám Mercedes E 220, rok výroby 2018, najeto 150 000 km. Vůz je v dobrém stavu, pravidelně servisován.",
    }

    print("📡 Stahuji inzeráty...")
    ads = fetch_all_ads(user_item["title"])

    print(f"🔍 Porovnávám {len(ads)} inzerátů s uživatelskou položkou...")
    results = compute_similarity(user_item, ads)

    print("\n📊 Top 5 nejpodobnějších inzerátů:\n")
    for i, result in enumerate(results[:5]):
        print(f"#{i+1}: {result['ad']['title']} - {result['ad']['price']} Kč")
        print(f"URL: {result['ad']['url']}")
        print(f"Similarity Score: {result['similarity_score']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main()