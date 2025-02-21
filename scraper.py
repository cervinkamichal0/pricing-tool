import requests
import json

def get_bazos_ads(query, limit=80):
    url = "https://www.bazos.cz/api/v1/ads.php"

    params = {"query": query, 
              "offset": 0, 
              "limit": limit
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
       return json.loads(response.text)
    else:
        print(f"Chyba při získávání inzerátů: {response.status_code}")
        return []

def fetch_bazos_ad_details(ad_id):
    url = "https://www.bazos.cz/api/v1/ad-detail-2.php"
    params = {"ad_id": ad_id}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Chyba při získávání detailu inzerátu {ad_id}: {response.status_code}")
        return None

def fetch_sbazar_ads(query, limit=80):
    url = "https://sbazar.cz/api/v1/adverts/search"
    params = {
        "limit": limit,
        "offset": 0,
        "phrase": query
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return json.loads(response.text)
        
    else:
        print(f"Chyba při získávání inzerátů: {response.status_code}")
        return []

def fetch_sbazar_ad_details(ad_id):
    url = f"https://sbazar.cz/api/v1/adverts/"
    params = {"ad_id": ad_id}

    response = requests.get(url,params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Chyba při získávání detailu inzerátu {ad_id}: {response.status_code}")
        return None

def main():
    query = "Bmw e92"
    ads_bazos = get_bazos_ads(query)
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
