import os, requests
from flask import Flask, request, abort

app = Flask(__name__)

# Секреты берём из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")      # токен бота от BotFather
CHAT_ID   = os.getenv("CHAT_ID")        # твой chat_id
SECRET    = os.getenv("SECRET", "")     # пароль, должен совпадать с "key" в payload TradingView

TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_tg(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        return {"ok": False, "error": "BOT_TOKEN/CHAT_ID not set"}
    r = requests.post(TG_URL, data={"chat_id": CHAT_ID, "text": text, "parse_mode":"HTML"}, timeout=10)
    return r.json()

@app.get("/")
def health():
    return "OK: TV→Telegram webhook running."

@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True) or {}
    # простая защита
    if SECRET and data.get("key") != SECRET:
        abort(401)

    # поддержка разных форматов сообщения
    signal  = (data.get("signal") or data.get("type") or data.get("message") or "").upper()
    ticker  = data.get("ticker", "")
    tf      = data.get("interval", "")
    price   = data.get("price", data.get("close", ""))
    tstamp  = data.get("time", data.get("timenow", ""))

    head = "🟢 BUY" if "BUY" in signal else ("🔴 SELL" if "SELL" in signal else "📣 SIGNAL")
    text = f"{head} {ticker} {tf}\nЦена: {price}\nВремя: {tstamp}"

    res = send_tg(text)
    return {"ok": True, "telegram": res}

if __name__ == "__main__":
    # локальный запуск (для теста)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
