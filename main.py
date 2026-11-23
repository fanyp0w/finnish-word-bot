import os
import random
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Wiktionary требует указывать User-Agent в заголовках
HEADERS = {"User-Agent": "FinnishDailyWordBot/1.0 (contact@example.com)"}

def get_random_finnish_word():
    # 1. Получаем список слов из категории финских существительных/базовых слов на англ. Wiktionary
    api_url = "https://wiktionary.org"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Finnish_lemmas", # Все базовые формы финских слов
        "cmlimit": 500,
        "format": "json"
    }
    
    response = requests.get(api_url, params=params, headers=HEADERS).json()
    words = [item["title"] for item in response["query"]["categorymembers"] if ":" not in item["title"]]
    
    # Выбираем случайное слово
    chosen_word = random.choice(words)
    
    # 2. Загружаем страницу слова, чтобы забрать перевод
    page_url = f"https://wiktionary.org{chosen_word}"
    page_resp = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(page_resp.text, "html.parser")
    
    # Ищем первый блок с определением (обычно внутри тега <ol>)
    definitions = []
    finnish_section = soup.find(id="Finnish")
    if finnish_section:
        # Идем вниз по HTML после заголовка Finnish до первого списка определений <ol>
        ol_tag = finnish_section.find_next("ol")
        if ol_tag:
            for li in ol_tag.find_all("li", recursive=False)[:3]: # Берем до 3 значений
                # Очищаем текст от лишних вложенных примеров
                text = li.get_text().split("\n")[0].strip()
                if text:
                    definitions.append(f"• {text}")
                    
    meaning = "\n".join(definitions) if definitions else "Перевод не найден, посмотрите по ссылке ниже."
    return chosen_word, meaning, page_url

def send_telegram_message(word, meaning, url):
    text = (
        f"🇫🇮 **Päivän sana: {word}**\n\n"
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
    requests.post(tg_url, json=payload)

if __name__ == "__main__":
    word, meaning, url = get_random_finnish_word()
    send_telegram_message(word, meaning, url)
    print(f"Sent word: {word}")
