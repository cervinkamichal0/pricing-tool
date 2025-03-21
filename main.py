from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from data_fetcher import fetch_all_ads
from similarity import compute_price, compute_similarity
from open_ai import suggest_description
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

# Datový model inzerátu
class Ad(BaseModel):
    title: str
    price: int
    url: str
    similarity_score: float

# Datový model odpovědi z endpointu /similar_ads
class SimilarAdsResponse(BaseModel):
    estimated_price: Optional[int]
    estimated_quick_sale_price: Optional[int]
    similar_ads: List[Ad]

@app.post("/similar_ads", response_model=SimilarAdsResponse)
async def get_similar_ads(
    title: str = Form(...), 
    description: str = Form(...), 
    file: UploadFile = File(...)
):
    """API endpoint pro získání nejpodobnějších inzerátů podle textu a obrázku."""

    print(title,"\n", description, "\n",file.filename)
    ads = fetch_all_ads(title)

    if ads is None or len(ads) == 0:
        print ("Nebyly nalezeny žádné inzeráty.")
        return SimilarAdsResponse(
            estimated_price=None,
            estimated_quick_sale_price=None,
            similar_ads=[]
        )

    print(f"Porovnávám {len(ads)}...")

    # Uložení nahraného obrázku
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Porovnání textové podobnosti
    user_item = {"title": title, "description": description}
    text_results = compute_similarity(user_item, file_location, ads)

    # Vybereme top 3 podle textu
    top_results = text_results[:3]

    # Spočítáme průměrnou cenu top 10 inzerátů
    estimated_price = compute_price(text_results[:3])

    estimated_quick_sale_price = compute_price(top_results, quick_sale=True)

    if estimated_price < estimated_quick_sale_price:
        estimated_quick_sale_price = int(estimated_price * 0.9)  # Sleva 10 % pro quick sale

    # Sestavení odpovědi
    response = SimilarAdsResponse(
        estimated_price=estimated_price,
         estimated_quick_sale_price=estimated_quick_sale_price,
        similar_ads=[
            Ad(
                title=result["ad"]["title"],
                price=result["ad"].get("price", 0),
                url=result["ad"].get("url", ""),
                similarity_score=result["similarity_score"],
            )
            for result in top_results
        ]
    )

    print(response)
    return response

@app.post("/generate_description",response_model=str)
async def generate_description(title: str = Form(...)):
    """API endpoint pro generování popisu inzerátu."""

    result = suggest_description(title)
    print(result)
    return result

# Spuštění API (pro lokální testování)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)