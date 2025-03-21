import os
from openai import OpenAI

def suggest_description(ad_title):
    """Generuje strukturu popisu inzerátu pro daný název."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content":  "Vytvoř strukturu popisu pro věc, kterou chci prodat na inzerentním webu."
                            "Nepiš strukturovaně, ale stále zachovej čistě informativní formu textu."              
                            "Vůbec neuváděj konkrétní informace,ani nepředpokládej stav věci. Místo konkrétních informací použij ___ (tři podtržítka)."
                            "Popisuj věc jako její průměrný uživatel uživatel. Nepiš tedy například příliš odborně. Uváděj tedy pouze strukturu pro informace o jejím stavu."
                            "Popis inzerátu by měl být optimální pro použití se sentence_transformers pro porovnání podobnosti s ostatními inzeráty."
                            "Nijak popis nestyluj. (nepoužívěj markdown, pouze vrať text)."
                            "Předpokládej, že kontaktní informace a název se vyplňují jinde."
                            "Popis by měl být dlouhý mezi 50 až 500 znaky."
                            "Název inzerátu je: " + ad_title
            }
        ],
        model="gpt-4o-mini"
    )

    return chat_completion.choices[0].message.content