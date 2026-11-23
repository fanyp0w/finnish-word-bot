import html
import os
import random
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"].strip()
CHAT_ID = os.environ["CHAT_ID"].strip()

def get_random_finnish_word():
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
    
    lines = resp.text.splitlines()[:2000]
    words = []
    for line in lines:
        items = line.split()
        if items:
            first_word = items.pop(0)
            if len(first_word) > 2:
                words.append(first_word)
            
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
        if (
            t 
            and len(t.split()) <= 3 
            and t.lower() != main_translation.lower() 
            and t not in extra
        ):
            extra.append(t)
        if len(extra) >= 2:
            break
            
    safe_main = html.escape(main_translation)
    meaning = f"• <b>{safe_main}</b>"
    if extra:
        safe_extra = [html.escape(item) for item in extra]
        meaning += "\n• " + "\n• ".join(safe_extra)
        
    dict_url = "https://" + "en.wiktionary.org" + f"/wiki/{chosen_word}#Finnish"
    return chosen_word, meaning, dict_url

def send_telegram_message(word, meaning, url):
    safe_word = html.escape(word)
    text = (
        f"🇫🇮 <b>Päivän sana: {safe_word}</b>\n\n"
        f"{meaning}\n\n"
        f"📖 <a href=\"{url}\">Примеры и формы в словаре</a>"
    )
    tg_url = "https://" + "api.telegram.org" + f"/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    res = requests.post(tg_url, json=payload, timeout=15)
    if res.status_code != 200:
        raise RuntimeError(f"Telegram ответил {res.status_code}: {res.text}")

if __name__ == "__main__":
    word, meaning, url = get_random_finnish_word()
    send_telegram_message(word, meaning, url)
    print(f"Успешно отправлено слово: {word}")
