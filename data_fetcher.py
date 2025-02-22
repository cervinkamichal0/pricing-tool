import requests
import json

class BaseAPIClient:
    BASE_URL = ""

    @classmethod
    def fetch(cls, endpoint, params=None):
        url = f"{cls.BASE_URL}{endpoint}"
        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "cs,en-US;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "X-Requested-With": "XMLHttpRequest",
            }
        response = requests.get(url, params=params,headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed fetching ads list: {response.status_code}")
            return None
    
class BazosAPIClient(BaseAPIClient):
    BASE_URL = "https://www.bazos.cz/api/v1/"

    @classmethod
    def fetch_ads(cls, query, limit=80):
        response_json =  cls.fetch("ads.php", {"query": query, "offset": 0, "limit": limit})
        if isinstance(response_json, list):  
            ids = [item['id'] for item in response_json]    
            return ids
        else:
            print("Response is not a list.")

    @classmethod
    def fetch_ad_detail(cls, ad_id):
        response_json =  cls.fetch(f"ad-detail-2.php?ad_id={ad_id}", {"ad_id": ad_id})

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
    def fetch_ads(cls, query, limit=80):
        response_json = cls.fetch("adverts/search", {"limit": limit, "offset": 0, "phrase": query}) or []
        if isinstance(response_json, dict): 
            ids = [ad['id'] for ad in response_json['results']]
            return ids
        else:
            print("Response is not a dictionary.")
    
    @classmethod
    def fetch_ad_detail(cls, ad_id):
        response_json = cls.fetch(f"adverts/{ad_id}")
        if isinstance(response_json, dict):
            return {
                "title": response_json["result"]["name"],
                "price": response_json["result"]["price"],
                "description": response_json["result"]["description"],
                "images": [image["url"] for image in response_json["result"]["images"]],
                "url": f"https://www.sbazar.cz/name/detail/{ad_id}"
            }

def fetch_all_ads(querry):
        bazos_ads = BazosAPIClient.fetch_ads(querry)
        sbazar_ads = SbazarAPIClient.fetch_ads(querry)
        
        ads = []
        for ad in bazos_ads[:30]:   
            ads.append(BazosAPIClient.fetch_ad_detail(ad))

        for ad in sbazar_ads[:30]:
            ads.append(SbazarAPIClient.fetch_ad_detail(ad))
        return ads
