import os
import random
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Используем стандартный User-Agent браузера, чтобы серверы не блокировали GitHub Actions
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def get_random_finnish_word():
    api_url = "https://wiktionary.org"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Finnish_lemmas",
        "cmlimit": 500,
        "format": "json"
    }
    
    resp = requests.get(api_url, params=params, headers=HEADERS, timeout=15)
    
    # Проверяем, что сервер ответил успешно, иначе выводим причину в лог
    if resp.status_code != 200:
        raise RuntimeError(f"Wiktionary API вернул код {resp.status_code}: {resp.text[:200]}")
        
    data = resp.json()
    words = [item["title"] for item in data["query"]["categorymembers"] if ":" not in item["title"]]
    chosen_word = random.choice(words)
    
    # Загружаем страницу слова
    page_url = f"https://wiktionary.org{chosen_word}"
    page_headers = {"User-Agent": HEADERS["User-Agent"]}
    page_resp = requests.get(page_url, headers=page_headers, timeout=15)
    soup = BeautifulSoup(page_resp.text, "html.parser")
    
    definitions = []
    finnish_section = soup.find(id="Finnish")
    if finnish_section:
        ol_tag = finnish_section.find_next("ol")
        if ol_tag:
            for li in ol_tag.find_all("li", recursive=False)[:3]:
                # Берем первую строку определения без вложенных примеров
                text = li.get_text().split("\n")[0].strip()
                if text:
                    definitions.append(f"• {text}")
                    
    meaning = "\n".join(definitions) if definitions else "Перевод не найден, посмотрите по ссылке ниже."
    return chosen_word, meaning, page_url

def send_telegram_message(word, meaning, url):
    text = (
        f"🇫🇮 *Päivän sana: {word}*\n\n"
        f"{meaning}\n\n"
        f"📖 [Открыть в словаре]({url})"
    )
    tg_url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    res = requests.post(tg_url, json=payload, timeout=15)
    if res.status_code != 200:
        print(f"Ошибка Telegram API: {res.text}")

if __name__ == "__main__":
    word, meaning, url = get_random_finnish_word()
    send_telegram_message(word, meaning, url)
    print(f"Успешно отправлено слово: {word}")
