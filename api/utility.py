


def get_info_str(name: str):
    return f"[INFO]({name}) "
    
def get_warn_str(name: str):
    return f"[WARNING]({name}) "
    

    
def to_roc(date_str):
    # 將 YYYY-MM-DD 轉為 YYY-MM-DD（民國年）
    y, m, d = date_str.split('-')
    roc_y = str(int(y)-1911)
    return f"{roc_y}-{m}-{d}"

def to_ad(roc_str):
    # 將 YYY-MM-DD 轉回 YYYY-MM-DD
    y, m, d = roc_str.split('-')
    ad_y = str(int(y)+1911) if len(y) <= 3 else y
    return f"{ad_y}-{m}-{d}"
    
def check_date_format(try_parse_date):
    try_parse_date = str(try_parse_date)
    if '-' in try_parse_date:
        if len(try_parse_date) == 19 : # 2022-01-14 00:00:00
            return 'YYYY-MM-DD HH:MM:SS'
        elif len(try_parse_date) == 16 : # 2022-01-14 00:00
            return 'YYYY-MM-DD HH:MM'
        elif len(try_parse_date) == 13 : # 2022-01-14 00
            return 'YYYY-MM-DD HH'
        elif len(try_parse_date) == 10 : # 2021-01-07
            return 'YYYY-MM-DD'
        elif len(try_parse_date) == 9 : # 110-01-07
            return 'YYY-MM-DD'
    elif '/' in try_parse_date:
        if len(try_parse_date) == 10 : # 2021/01/07
            return 'YYYY/MM/DD'
        elif len(try_parse_date) == 9 : # 110/01/07
            return 'YYY/MM/DD'
    elif '年' in try_parse_date: 
        if '月' in try_parse_date:
            if '日' in try_parse_date:
                return 'YYYY年MM月DD日'
    elif len(try_parse_date) == 8 : # 20210107
        return 'YYYYMMDD'
    else:
        print("Date change may be failed")   