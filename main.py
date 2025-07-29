import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_PROB = float(os.getenv("MIN_PROB", 0.70))
MIN_ODDS = float(os.getenv("MIN_ODDS", 1.60))
MIN_EV = float(os.getenv("MIN_EV", 0.01))

def calcular_ev(prob, cuota):
    return (prob * cuota) - 1

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": texto}
    requests.post(url, data=data)

def obtener_picks_ev_plus():
    url = "https://www.bettingpros.com/mlb/picks/"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    picks = soup.select("div.pick-card")
    resultados = []

    for pick in picks:
        try:
            nombre = pick.select_one(".pick-meta").get_text(strip=True)
            cuota_texto = pick.select_one(".pick-odds").get_text(strip=True).replace("+", "")
            cuota = 1 + int(cuota_texto) / 100 if cuota_texto.isdigit() else 2.00

            prob_texto = pick.select_one(".probability").get_text(strip=True).replace("%", "")
            prob = int(prob_texto) / 100

            ev = calcular_ev(prob, cuota)

            if prob >= MIN_PROB and cuota >= MIN_ODDS and ev >= MIN_EV:
                mensaje = (
                    "📊 Nuevo Pick EV+\n\n"
                    f"🏟️ {nombre}\n"
                    f"✅ Probabilidad: {round(prob*100)}%\n"
                    f"💸 Cuota: {cuota}\n"
                    f"📈 EV+: {round(ev, 2)}"
                )
                resultados.append(mensaje)

        except Exception:
            continue

    return resultados

# Ejecutar
picks = obtener_picks_ev_plus()

for p in picks:
    enviar_mensaje(p)
