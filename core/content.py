import re


def description_error(value):
    normalized = re.sub(r'[\s\-().]+', '', value)
    if re.search(r'\d{7,}', normalized):
        return 'Açıqlamada telefon nömrəsi və ya əlaqə nömrəsi yazmaq qadağandır!'
    if re.search(r'(https?://|www\.|\b[\w\-]+\.(com|az|net|org|ru|info|biz|co|io|me|tv|edu|gov))\b', value, re.I):
        return 'Açıqlamada sayt adı və ya link yazmaq qadağandır!'
    return None
