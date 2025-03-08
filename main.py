from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from data_fetcher import fetch_all_ads
from similarity import compute_price, compute_similarity
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Povolí požadavky ze všech domén (změň na konkrétní doménu pro vyšší bezpečnost)
    allow_credentials=True,
    allow_methods=["*"],  # Povolí všechny HTTP metody (GET, POST, OPTIONS atd.)
    allow_headers=["*"],  # Povolí všechny hlavičky
)

# Definice datového modelu requestu
class UserItem(BaseModel):
    title: str
    description: str

# Definice datového modelu pro odpověď
class AdResponse(BaseModel):
    title: str
    price: int
    url: str
    similarity_score: float

# Datový model odpovědi API
class SimilarAdsResponse(BaseModel):
    estimated_price: Optional[int]  # Vypočítaná cena
    similar_ads: List[AdResponse]

@app.post("/similar_ads", response_model=SimilarAdsResponse)
def get_similar_ads(user_item: UserItem):
    """API endpoint pro získání nejpodobnějších inzerátů."""
    print("Stahuji inzeráty...")
    ads = fetch_all_ads(user_item.title)
    
    print(f"Porovnávám {len(ads)} inzerátů s uživatelskou položkou...")
    results = compute_similarity(user_item.model_dump(), ads)

    # Vybereme pouze top 3 výsledků
    top_results = results[:3]

    estimated_price = compute_price(top_results)
    
    response = SimilarAdsResponse(
            estimated_price=estimated_price,
            similar_ads=[
                AdResponse(
                    title=result["ad"]["title"],
                    price=result["ad"].get("price", 0),
                    url=result["ad"].get("url", ""),
                    similarity_score=result["similarity_score"]
                )
                for result in top_results
            ]
        )

    return response
    


# Spuštění API (pro lokální testování)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)