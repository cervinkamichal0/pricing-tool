import requests
import json

def fetch_bazos_ads(query, limit=200):
    url = f"https://www.bazos.cz/api/v1/ads.php?query={query}&offset=0&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
       return json.loads(response.text)
    else:
        print(f"Chyba při získávání inzerátů: {response.status_code}")
        return []

def fetch_bazos_ad_details(ad_id):
    url = f"https://www.bazos.cz/api/v1/ad-detail-2.php?ad_id={ad_id}"
    response = requests.get(url)
    if response.status_code == 80:
        return response.json()
    else:
        print(f"Chyba při získávání detailu inzerátu {ad_id}: {response.status_code}")
        return None

def fetch_sbazar_ads(search_query, limit=80):
    base_url = "https://sbazar.cz/api/v1/adverts/search"
    params = {
        "limit": limit,
        "offset": 0,
        "phrase": search_query
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return json.loads(response.text)
        
    else:
        print(f"Chyba při získávání inzerátů: {response.status_code}")
        return []

def fetch_sbazar_ad_details(ad_id):
    url = f"https://sbazar.cz/api/v1/adverts/{ad_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Chyba při získávání detailu inzerátu {ad_id}: {response.status_code}")
        return None

def main():
    query = "Bmw"
    ads_bazos = fetch_bazos_ads(query)
    ads_sbazar = fetch_sbazar_ads(query)
    print(f"Nalezeno {len(ads_bazos)} inzerátů.")
    print(f"Nalezeno {len(ads_sbazar)} inzerátů.")

    for ad in ads_bazos[:5]:  # Omezíme na prvních 5 pro ukázku
        ad_id = ad.get("id")
        print(f"\nZískávám detail pro ID {ad_id}...")
        ad_details = fetch_bazos_ad_details(ad_id)
        if ad_details:
            print(json.dumps(ad_details, indent=4, ensure_ascii=False))
    


if __name__ == "__main__":
    main()
