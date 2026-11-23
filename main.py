    main_translation = trans_resp["responseData"]["translatedText"]
    matches = trans_resp.get("matches", [])
    
    extra = []
    for m in matches:
        t = m.get("translation", "").strip()
        # Берем только короткие варианты (не длиннее 3 слов), чтобы отсеять целые предложения
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
