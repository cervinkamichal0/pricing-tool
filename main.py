from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from data_fetcher import fetch_all_ads
from similarity import compute_similarity
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

@app.post("/similar_ads", response_model=List[AdResponse])
def get_similar_ads(user_item: UserItem):
    """API endpoint pro získání nejpodobnějších inzerátů."""
    print("Stahuji inzeráty...")
    ads = fetch_all_ads(user_item.title)
    
    print(f"Porovnávám {len(ads)} inzerátů s uživatelskou položkou...")
    results = compute_similarity(user_item.model_dump(), ads)
    
    # Vrátíme pouze top 5 výsledků
    return [
        AdResponse(
            title=result["ad"]["title"],
            price=result["ad"].get("price", 0),  # Defaultní hodnota, pokud chybí
            url=result["ad"].get("url", ""),
            similarity_score=result["similarity_score"]
        )
        for result in results[:5]
    ]

# Spuštění API (pro lokální testování)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)