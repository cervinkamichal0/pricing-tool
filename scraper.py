import requests
import json

class BaseAPIClient:
    BASE_URL = ""

    @classmethod
    def get(cls, endpoint, params=None):
        url = f"{cls.BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed fetching ads list: {response.status_code}")
            return None

class BazosAPIClient(BaseAPIClient):
    BASE_URL = "https://www.bazos.cz/api/v1/"

    @classmethod
    def get_ads(cls, query, limit=80):
        response_json =  cls.get("ads.php", {"query": query, "offset": 0, "limit": limit})
        if isinstance(response_json, list):  
            ids = [item['id'] for item in response_json]    
            return ids
        else:
            print("Response is not a list.")

    @classmethod
    def get_ad_detail(cls, ad_id):
        response_json =  cls.get("ad-detail-2.php", {"ad_id": ad_id})
        if isinstance(response_json, dict):
            return {
                "title": response_json["title"],
                "price": response_json["price"],
                "description": response_json["description"],
                "images": response_json["images"],
                "url": response_json["url"],
            }

class SbazarAPIClient(BaseAPIClient):
    BASE_URL = "https://sbazar.cz/api/v1/"

    @classmethod
    def get_ads(cls, query, limit=80):
        response_json = cls.get("adverts/search", {"limit": limit, "offset": 0, "phrase": query}) or []
        if isinstance(response_json, dict): 
            ids = [ad['id'] for ad in response_json['results']]
            return ids
        else:
            print("Response is not a dictionary.")
    
    @classmethod
    def get_ad_detail(cls, ad_id):
        response_json = cls.get(f"adverts/{ad_id}")
        if isinstance(response_json, dict):
            return {
                "title": response_json["result"]["name"],
                "price": response_json["result"]["price"],
                "description": response_json["result"]["description"],
                "images": [image["url"] for image in response_json["result"]["images"]],
                "url": f"https://www.sbazar.cz/name/detail/{ad_id}"
            }

def main():
    query = "Bmw e92"
    
    ads_bazos = BazosAPIClient.get_ads(query)
    ads_sbazar = SbazarAPIClient.get_ads(query)
    
    print(f"Nalezeno {len(ads_bazos)} inzerátů na Bazoš.")
    print(f"Nalezeno {len(ads_sbazar)} inzerátů na Sbazar.")
    
    for ad in ads_bazos[:5]:  
        print(f"\nZískávám detail pro ID {ad} na Bazoš...")
        ad_details = BazosAPIClient.get_ad_detail(ad)
        if ad_details:
            print(json.dumps(ad_details, indent=4, ensure_ascii=False))

    for ad in ads_sbazar[:5]: 
        print(f"\nZískávám detail pro ID {ad} na Sbazar...")
        ad_details = SbazarAPIClient.get_ad_detail(ad)
        if ad_details:
            print(json.dumps(ad_details, indent=4, ensure_ascii=False))
             
if __name__ == "__main__":
    main()
