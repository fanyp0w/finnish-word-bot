import os
import random
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_random_finnish_word():
    # Собираем URL через join, чтобы при копировании не пропадали слэши
    parts = [
        "https:/",
        "raw." + "githubusercontent." + "com",
        "hermitdave",
        "FrequencyWords",
        "master",
        "content",
        "2018",
        "fi",
        "fi_50k.txt"
    ]
    words_url = "/".join(parts)
    
    resp = requests.get(words_url, timeout=15)
    resp.raise_for_status()
    
    # Берем топ-2000 самых частых слов длиннее 2 букв
    lines = resp.text.splitlines()[:2000]
    words = [line.split() for line in lines if len(line.split()) > 2]
    chosen_word = random.choice(words)
    
    # Получаем перевод через MyMemory API
    trans_url = "https://" + "api.mymemory.translated.net" + "/get"
    params = {
        "q": chosen_word,
        "langpair": "fi|ru"
    }
    trans_resp = requests.get(trans_url, params=params, timeout=15).json()
    
    main_translation = trans_resp["responseData"]["translatedText"]
    matches = trans_resp.get("matches", [])
    
    extra = []
    for m in matches:
        t = m.get("translation", "").strip()
        if t and t.lower() != main_translation.lower() and t not in extra:
            extra.append(t)
        if len(extra) >= 2:
            break
            
    meaning = f"• *{main_translation}*"
    if extra:
        meaning += "\n• " + "\n• ".join(extra)
        
    dict_url = "https://" + "en.wiktionary.org" + f"/wiki/{chosen_word}#Finnish"
    return chosen_word, meaning, dict_url

def send_telegram_message(word, meaning, url):
    text = (
        f"🇫🇮 *Päivän sana: {word}*\n\n"
        f"{meaning}\n\n"
        f"📖 [Примеры и формы в словаре]({url})"
    )
    tg_url = "https://" + "api.telegram.org" + f"/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    res = requests.post(tg_url, json=payload, timeout=15)
    res.raise_for_status()

if __name__ == "__main__":
    word, meaning, url = get_random_finnish_word()
    send_telegram_message(word, meaning, url)
    print(f"Успешно отправлено слово: {word}")
