from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔹 Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scrape_data():
    url = "https://www.infodolar.com.do"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP responses
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "cotizaciones"})
        if not table:
            return {"error": "No se pudo encontrar la tabla"}

        rows = table.find_all("tr")
        if len(rows) <= 1:
            return {"error": "No se pudo encontrar la fila de datos"}

        data = rows[1].find_all("td")
        compra = float(data[1].get("data-order", "0").replace("$", ""))
        venta = float(data[2].get("data-order", "0").replace("$", ""))

        raw_variacion = data[3].text.strip().replace("%", "").replace(" ", "")
        clean_variacion = raw_variacion.lstrip("= ")
        try:
            variacion = float(clean_variacion)
        except ValueError:
            variacion = None

        spread = float(data[4].text.strip().replace("$", ""))
        fecha = data[5].find("abbr").get("title", "N/A")

        return {
            "compra": compra,
            "venta": venta,
            "variacion": variacion,
            "spread": spread,
            "fecha": fecha,
        }
    except Exception as e:
        return {"error": f"Parsing failed: {str(e)}"}

@app.get("/scrape")
def get_scraped_data():
    return scrape_data()
