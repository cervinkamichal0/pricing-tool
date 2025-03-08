from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from data_fetcher import fetch_all_ads
from similarity import compute_price, compute_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Složka pro ukládání nahraných obrázků
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Datový model odpovědi
class AdResponse(BaseModel):
    title: str
    price: int
    url: str
    similarity_score: float

class SimilarAdsResponse(BaseModel):
    estimated_price: Optional[int]
    similar_ads: List[AdResponse]

@app.post("/similar_ads", response_model=SimilarAdsResponse)
async def get_similar_ads(
    title: str = Form(...), 
    description: str = Form(...), 
    file: UploadFile = File(...)
):
    """API endpoint pro získání nejpodobnějších inzerátů podle textu a obrázku."""

    print("Stahuji inzeráty...")
    ads = fetch_all_ads(title)

    print(f"Porovnávám {len(ads)} inzerátů s uživatelskou položkou...")

    # Uložení nahraného obrázku
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Porovnání textové podobnosti
    user_item = {"title": title, "description": description}
    text_results = compute_similarity(user_item, ads)

    # Vybereme top 3 podle textu
    top_results = text_results[:3]

    # Spočítáme průměrnou cenu
    estimated_price = compute_price(top_results)

    # Sestavení odpovědi
    response = SimilarAdsResponse(
        estimated_price=estimated_price,
        similar_ads=[
            AdResponse(
                title=result["ad"]["title"],
                price=result["ad"].get("price", 0),
                url=result["ad"].get("url", ""),
                similarity_score=result["similarity_score"],
            )
            for result in top_results
        ]
    )

    return response

# Spuštění API (pro lokální testování)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)