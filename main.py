from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

    # 🔹 Configuración de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permitir todas las orígenes
        allow_credentials=True,
        allow_methods=["*"],  # Permitir todos los métodos
        allow_headers=["*"],  # Permitir todos los encabezados
    )
    
def scrape_data():
    

    url = "https://www.infodolar.com.do"  # 🔹 URL de la web a scrapear
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "cotizaciones"})  # Reemplaza "cotizaciones" con la clase real de la tabla
        if table:
            rows = table.find_all("tr")
            if len(rows) > 1:
                data = rows[1].find_all("td")
                compra = float(data[1].get("data-order").replace("$", ""))
                venta = float(data[2].get("data-order").replace("$", ""))

                # 🔹 Fix for "ValueError: could not convert string to float"
                raw_variacion = data[3].text.strip().replace("%", "").replace(" ", "")
                clean_variacion = raw_variacion.lstrip("= ")  # Remove "=" if present

                try:
                    variacion = float(clean_variacion)
                except ValueError:
                    variacion = None  # Set to None or a default value like 0.00

                spread = float(data[4].text.strip().replace("$", ""))
                fecha = data[5].find("abbr").get("title")

                return {
                    "compra": compra,
                    "venta": venta,
                    "variacion": variacion,
                    "spread": spread,
                    "fecha": fecha
                }
            else:
                return {"error": "No se pudo encontrar la fila de datos"}
        else:
            return {"error": "No se pudo encontrar la tabla"}
    else:
        return {"error": "No se pudo obtener la página"}

@app.get("/scrape")
def get_scraped_data():
    return scrape_data()
