import os
import json
from dotenv import load_dotenv
import pymysql
import pandas as pd
from typing import Dict, List
from api.utility import get_info_str, get_warn_str

DEBUG_MODE = 0

def get_connection():
    load_dotenv()
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            connect_timeout=5
        )
        print(get_info_str(__name__), "成功連線到資料庫！") if DEBUG_MODE else None
        return connection
    except Exception as e:
        print(get_info_str(__name__), f"資料庫連線失敗：{e}") if DEBUG_MODE else None
    

def list_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()
    print(get_info_str(__name__), '所有資料表：', tables) if DEBUG_MODE else None
    return tables

def list_columns(table_name: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()
    print(get_info_str(__name__), f'所有 {table_name} 資料表欄位：', columns) if DEBUG_MODE else None
    return columns

# ---- 以下為 table_column_hash_util.py 內容 ----
JSON_DIR = 'json'
RAW_HASH_PATH = os.path.join(JSON_DIR, 'raw_table_column_hash.json')
COMMON_HASH_PATH = os.path.join(JSON_DIR, 'common_table_column_hash.json')
FILTERED_HASH_PATH = os.path.join(JSON_DIR, 'filtered_table_column_hash.json')
TABLE_COLUMN_MAPPING_PATH = 'csv/table_column_mapping.csv'

def generate_raw_table_column_hash() -> Dict[str, Dict[str, str]]:
    tables = list_tables()
    table_column_hash = {}
    for table in tables:
        columns = list_columns(table)
        table_column_hash[table] = {col: col for col in columns}
    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)
    with open(RAW_HASH_PATH, 'w', encoding='utf-8') as f:
        json.dump(table_column_hash, f, ensure_ascii=False, indent=2)
    print(get_info_str(__name__), f'raw_table_column_hash.json 已產生')
    return table_column_hash

def generate_common_table_column_hash(custom_rules: List[str]):
    # custom_rules 格式: ["stock_id+個股代號:stock_id", ...]
    mapping = {}
    for rule in custom_rules:
        aliases, unified = rule.split(":")
        alias_list = aliases.split("+")
        mapping[unified] = alias_list
    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)
    with open(COMMON_HASH_PATH, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(get_info_str(__name__), f'common_table_column_hash.json 已產生')
    return mapping

def filter_raw_by_common(raw_hash: Dict[str, Dict[str, str]], common_hash: Dict[str, List[str]]):
    # 取得所有 alias
    all_aliases = set()
    for alias_list in common_hash.values():
        all_aliases.update(alias_list)
    # 遍歷 raw_hash 移除 alias，只保留 unified name
    filtered = {}
    for table, cols in raw_hash.items():
        filtered[table] = {}
        for col, val in cols.items():
            if col not in all_aliases or col in common_hash:
                filtered[table][col] = val
    return filtered



def save_column_hash(hash_path=COMMON_HASH_PATH) -> None:
    """
    讀取 hash mapping，回傳 dict: {原始欄位: 統一欄位}
    """
    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)
    
    # Step 1: 產生 raw table column hash
    raw_hash = generate_raw_table_column_hash()

    # Step 2: 自定義重複欄位規則（可改為讀檔）
    custom_rules = [
        "stock_id+股票代號:stock_id",
        "成交量+volume:volume",
        "date+日期:date",
        "開盤價:close",
        "最高價:high",
        "最低價:low",
        "收盤價:close",
    ]
    common_hash = generate_common_table_column_hash(custom_rules)

    # Step 3: 過濾 raw hash
    filtered = filter_raw_by_common(raw_hash, common_hash)
    with open(FILTERED_HASH_PATH, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(get_info_str(__name__), 'filtered_table_column_hash.json 已產生')

def load_column_hash(hash_path=COMMON_HASH_PATH) -> Dict[str, str]:
    """
    讀取 hash mapping，回傳 dict: {原始欄位: 統一欄位}
    """
    if not os.path.exists(hash_path):
        raise FileNotFoundError(f"找不到 hash 檔案: {hash_path}")
    with open(hash_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    # 轉成 {alias: unified} 格式
    alias2unified = {}
    for unified, aliases in mapping.items():
        for alias in aliases:
            alias2unified[alias] = unified
        alias2unified[unified] = unified
    return alias2unified


def rename_df_columns(df: pd.DataFrame, table: str, hash_path=COMMON_HASH_PATH) -> pd.DataFrame:
    """
    根據 hash 將 df 欄位名稱統一
    """
    alias2unified = load_column_hash(hash_path)
    # 只 rename 有 mapping 的欄位
    rename_dict = {col: alias2unified[col] for col in df.columns if col in alias2unified}
    return df.rename(columns=rename_dict)


def reverse_column_mapping(table: str, familiar_col: str, rule_path='common/table_common_col_rule.txt') -> str:
    """
    根據熟悉名稱（unified name），查回原始 table 欄位名稱。
    會根據 table 的實際欄位，優先回傳該 table 擁有的 alias 名稱。
    若都沒有 match，才回傳 alias list 第一個。
    """
    print (get_info_str(__name__), f"執行 reverse_column_mapping(table={table}, familiar_col={familiar_col})") if DEBUG_MODE else None
    if not os.path.exists(rule_path):
        raise FileNotFoundError(f"找不到對應規則檔案: {rule_path}")
    with open(rule_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    mapping = {}
    for rule in lines:
        if ':' not in rule:
            continue
        aliases, unified = rule.split(':', 1)
        alias_list = aliases.split('+')
        mapping[unified] = alias_list
    alias_list = mapping.get(familiar_col, [familiar_col])
    # 取得該 table 的所有欄位
    try:
        table_columns = list_columns(table)
    except Exception as e:
        table_columns = []
    # 優先回傳在 table 中存在的 alias
    for alias in alias_list:
        if alias in table_columns:
            if (alias != familiar_col):
                print (get_info_str(__name__), f"為您將 {familiar_col} 替名為 {alias} 欄位，在 {table} table 做查詢")
            return alias
    # fallback: 回傳 alias list 第一個
    return alias_list[0]

def get_table_column_mapping_df():
    # 取得 DB 名稱
    db_name = os.getenv('DB_NAME', 'db')
    # 讀取所有 table 和欄位
    tables = list_tables()
    # 讀取 familiar_name 規則
    rule_path = 'common/table_common_col_rule.txt'
    familiar_map = {}
    if os.path.exists(rule_path):
        with open(rule_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        for rule in lines:
            if ':' not in rule:
                continue
            aliases, unified = rule.split(':', 1)
            alias_list = aliases.split('+')
            for alias in alias_list:
                familiar_map[alias] = unified
            familiar_map[unified] = unified
    # 組成 DataFrame
    data = []
    for table in tables:
        columns = list_columns(table)
        for col in columns:
            familiar = familiar_map.get(col, col)
            data.append({
                'db': db_name,
                'table': table,
                'column': col,
                'familiar_name': familiar
            })
    df = pd.DataFrame(data)
    # 顯示美觀的表格
    try:
        from tabulate import tabulate
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        df.to_csv(TABLE_COLUMN_MAPPING_PATH, index=False)
        print(get_info_str(__name__), 'csv/table_column_mapping.csv 已產生，供您參考')
    except ImportError:
        print("請安裝 tabulate 套件")
        print(df.head(20))
    # 回傳 DataFrame
    return df



