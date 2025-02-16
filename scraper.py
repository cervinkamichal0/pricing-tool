import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from typing import List, Dict

class BazosScraper:
    BASE_URL = "https://www.bazos.cz/search.php"

    def __init__(self, search_term: str, cena_od: int, cena_do: int):
        if cena_od >= cena_do:
            raise ValueError("Cena od musí být menší než cena do")

        self.search_term = search_term
        self.cena_od = cena_od
        self.cena_do = cena_do

    def get_listings(self) -> List[Dict]:
        """Hlavní funkce pro scrapování inzerátů na základě uživatelského vstupu."""
        listings = []
        url = f"{self.BASE_URL}?hledat={self.search_term.replace(' ', '+')}&cenaod={self.cena_od}&cenado={self.cena_do}"
        listings.extend(self._scrape_page(url))

        # Získáme počet stránek
        num_pages = self._get_page_count(url)

        # Scrapujeme další stránky (pokud jsou)
        for page in range(1, min(num_pages, 40)):  # Max 40 stránek
            next_page_url = f"{url}&crz={page * 20}"
            listings.extend(self._scrape_page(next_page_url))
            #time.sleep(2)  # Zpoždění pro prevenci blokace

        return listings

    def _scrape_page(self, url: str) -> List[Dict]:
        """Scrapuje jednu stránku s inzeráty."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            listings = []
            for ad in soup.select(".inzeraty"):
                title = ad.select_one(".nadpis").text.strip()
                price_text = ad.select_one(".inzeratycena").text.strip().replace(" Kč", "").replace(" ", "")
                price = int(price_text) if price_text.isdigit() else None
                location = ad.select_one(".inzeratylok").text.strip()
                date_text = ad.select_one(".velikost10").text.strip()
                description = ad.select_one(".popis").text.strip()

                # Datum inzerátu
                date_match = re.search(r"\[(\d{1,2}\.\d{1,2}\. \d{4})]", date_text)
                date = datetime.strptime(date_match.group(1), "%d.%m. %Y") if date_match else None

                image = ad.select_one(".obrazek img")["src"] if ad.select_one(".obrazek img") else None
                link = ad.select_one(".nadpis a")["href"] if ad.select_one(".nadpis a") else None

                listings.append({
                    "title": title,
                    "price": price,
                    "location": location,
                    "date": date.strftime("%Y-%m-%d") if date else None,
                    "image": image,
                    "url": link,
                    "description": description
                })

            return listings
        except requests.RequestException as e:
            print(f"Chyba při scrapování stránky {url}: {e}")
            return []

    def _get_page_count(self, url: str) -> int:
        """Získá počet stránek s výsledky."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            text = soup.select_one(".inzeratynadpis").text.replace(" ", "")
            match = re.search(r"inzerátůz(\d+)", text)
            total_ads = int(match.group(1)) if match else 0
            return min(total_ads // 20, 40)  # Omezíme na 40 stránek
        except requests.RequestException:
            return 1

#Testování scraperu
scraper = BazosScraper(search_term="iPhone 12", cena_od=5000, cena_do=20000)
results = scraper.get_listings()
for ad in results[:5]:  # Ukázka prvních 5 inzerátů
    print(ad)