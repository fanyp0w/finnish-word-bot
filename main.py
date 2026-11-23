import os
import random
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def get_random_finnish_word():
    # 1. Берем список из 1000+ самых частых финских слов из открытого репозитория на GitHub
    words_url = "https://githubusercontent.com"
    resp = requests.get(words_url, timeout=15)
    resp.raise_for_status()
    
    # Берем топ-2000 самых полезных слов (отбрасываем слишком короткие обрывки)
    lines = resp.text.splitlines()[:2000]
    words = [line.split()[0] for line in lines if len(line.split()[0]) > 2]
    chosen_word = random.choice(words)
    
    # 2. Получаем перевод через открытый API MyMemory (не блокирует GitHub Actions)
    trans_url = "https://translated.net"
    params = {
        "q": chosen_word,
        "langpair": "fi|ru" # Можно поменять на "fi|en" для перевода на английский
    }
    trans_resp = requests.get(trans_url, params=params, timeout=15).json()
    
    # Собираем основной перевод и альтернативные варианты
    main_translation = trans_resp["responseData"]["translatedText"]
    matches = trans_resp.get("matches", [])
    
    extra = []
    for m in matches:
        t = m.get("translation", "").strip()
        if t and t.lower() != main_translation.lower() and t not in extra:
            extra.append(t)
        if len(extra) >= 2:
            break
            
    meaning = f"• **{main_translation}**"
    if extra:
        meaning += "\n• " + "\n• ".join(extra)
        
    dict_url = f"https://wiktionary.org{chosen_word}#Finnish"
    return chosen_word, meaning, dict_url

def send_telegram_message(word, meaning, url):
    text = (
        f"🇫🇮 *Päivän sana: {word}*\n\n"
        f"{meaning}\n\n"
        f"📖 [Примеры и формы в словаре]({url})"
    )
    tg_url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
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
