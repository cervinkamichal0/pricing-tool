import requests
import json

def is_numeric(value):
    if isinstance(value, (int, float)):  
        return True
    if isinstance(value, str) and value.isdigit():  
        return True
    return False

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
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed fetching ads list: {response.status_code}")
            return None


class BazosAPIClient(BaseAPIClient):
    BASE_URL = "https://www.bazos.cz/api/v1/"

    @classmethod
    def fetch_ads(cls, query, limit=80):
        response_json = cls.fetch("ads.php", {"query": query, "offset": 0, "limit": limit})
        if isinstance(response_json, list):
            return [item["id"] for item in response_json]
        else:
            print("Response is not a list.")
            return []

    @classmethod
    def fetch_ad_detail(cls, ad_id):
        response_json = cls.fetch(f"ad-detail-2.php?ad_id={ad_id}", {"ad_id": ad_id})

        price = response_json.get("price", "0") if isinstance(response_json, dict) else "0"

        if is_numeric(price):  
            return {
                "title": response_json.get("title", ""),
                "price": int(price),
                "description": response_json.get("description", ""),
                "images": response_json.get("images", []),
                "url": response_json.get("url", ""),
            }
        return None


class SbazarAPIClient(BaseAPIClient):
    BASE_URL = "https://sbazar.cz/api/v1/"

    @classmethod
    def fetch_ads(cls, query, limit=80):
        response_json = cls.fetch("adverts/search", {"limit": limit, "offset": 0, "phrase": query})
        if isinstance(response_json, dict) and "results" in response_json:
            return [ad["id"] for ad in response_json["results"]]
        else:
            print("Response is not a dictionary.")
            return []

    @classmethod
    def fetch_ad_detail(cls, ad_id):
        response_json = cls.fetch(f"adverts/{ad_id}")
        result = response_json.get("result", {}) if isinstance(response_json, dict) else {}

        price = result.get("price", "0")

        if is_numeric(price):
            return {
                "title": result.get("name", ""),
                "price": int(price),
                "description": result.get("description", ""),
                "images": [image["url"] for image in result.get("images", [])],
                "url": f"https://www.sbazar.cz/name/detail/{ad_id}",
            }
        return None


def fetch_all_ads(query):
    bazos_ads = BazosAPIClient.fetch_ads(query)
    sbazar_ads = SbazarAPIClient.fetch_ads(query)

    ads = []

    for ad in bazos_ads[:30]:
        ad_detail = BazosAPIClient.fetch_ad_detail(ad)
        if ad_detail:
            ads.append(ad_detail)

    for ad in sbazar_ads[:30]:
        ad_detail = SbazarAPIClient.fetch_ad_detail(ad)
        if ad_detail:
            ads.append(ad_detail)

    return ads
