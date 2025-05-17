import pandas as pd
from api.db_lib import get_connection, rename_df_columns, reverse_column_mapping
from datetime import datetime, timedelta
from api.utility import get_info_str, get_warn_str, to_roc, to_ad, check_date_format


def parse_date_range(date_str: str):
    """
    傳入的 date_str 是 start_date:end_date 
    格式為 'YYYY-MM-DD:YYYY-MM-DD' 或 '-N:-M'
    
    api 會自動處理兩種格式：
    1. 'YYYY-MM-DD:YYYY-MM-DD' 直接回傳 start_date, end_date
    2. '-N:-M' 以今天為基準，end_date = 今天往前 M 天 ，start_date = end_date 再往前 N 天
    
    example1: (start_date, end_date ) = process_df.parse_date_range('2025-01-01:2025-05-01')
    example2: (start_date, end_date ) = process_df.parse_date_range('-100:-0')
    """
    today_stamp = datetime.strptime(
                        str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    today = today_stamp.strftime('%Y-%m-%d')
    if ':' not in date_str:
        raise ValueError('格式錯誤，需包含冒號')
    start, end = date_str.split(':')
    if start.startswith('-') and end.startswith('-'):
        # 解析 -N:-M 格式
        end_days = int(end)
        start_days = int(start)
        end_date = (datetime.strptime(today, '%Y-%m-%d') + timedelta(days=end_days)).strftime('%Y-%m-%d')
        start_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=start_days)).strftime('%Y-%m-%d')
        return start_date, end_date
    else:
        # 解析 yyyy-mm-dd:yyyy-mm-dd 格式
        return start, end


def get_db_df(table_name: str = 'price', date_range_str: str = '-100:-0', index_name: str = 'date', column_str: str = 'stock_id, 收盤價', constraint_str: str = '') -> pd.DataFrame:
    """
    - date_range_str: date_str 格式，預設 '-100:-0' (end_date: today, start_date: today-100)
    - index_name: 欄位名稱，預設 'date'
    - column_str: 欄位名稱，預設 'stock_id, 收盤價'

    取得 table_name 資料表資料，並回傳 pivot_df。
    - table_name: 資料表名稱，預設 'price'
    - index: date
    - column_str: 欄位名稱，預設 'stock_id, 收盤價'
    
    * example: df = process_df.get_db_df(table_name='price', days_before=100, end_date='2025-05-01', index_name='date', column_str='stock_id, 收盤價')
    """

    (start_date, end_date) = parse_date_range(date_range_str)
    conn = get_connection()
    cursor = conn.cursor()

    # 判斷是否需要民國年格式
    cursor.execute(f'SELECT DISTINCT date FROM {table_name} ORDER BY date DESC LIMIT 1')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    latest_date = pd.DataFrame(rows, columns=columns).iloc[0, 0]
    date_fmt = check_date_format(latest_date)

    use_roc = date_fmt == 'YYY-MM-DD'

    if use_roc:
        start_date = to_roc(start_date)
        end_date = to_roc(end_date)

    constraint_query = ""
    if constraint_str != "":
        print (get_info_str(__name__), f"分析 constraint_str: {constraint_str}")
        if ':' in constraint_str :
            constraint_list = constraint_str.split(":")
            for constraint in constraint_list:
                if '=' not in constraint:
                    raise ValueError(f"constraint_str : {constraint_str} 格式錯誤，需包含等號")
                constraint_col = reverse_column_mapping(table_name, constraint.split("=")[0].strip())
                constraint_val = constraint.split("=")[1].strip()
                constraint_query += f" AND {constraint_col} = '{constraint_val}'"
        elif '=' in constraint_str:
            constraint_col = reverse_column_mapping(table_name, constraint_str.split("=")[0].strip())
            constraint_val = constraint_str.split("=")[1].strip()
            constraint_query += f" AND {constraint_col} = '{constraint_val}'"
        else:
            raise ValueError(f"constraint_str : {constraint_str} 格式錯誤，請包含等號或 冒號加等號")
    try:
        
        
        col_query = ""
        if ',' in column_str :
            column_list = column_str.split(",")
            for column_name in column_list:
                if col_query != "":
                    col_query += ", "
                column_name = column_name.strip()
                origin_col = reverse_column_mapping(table_name, column_name.strip())
                col_query += f" {origin_col} "
        else:
            col_query = reverse_column_mapping(table_name, column_str.strip())
        query = f'''
            SELECT {col_query}, {index_name}
            FROM {table_name}
            WHERE {index_name} BETWEEN '{start_date}' AND '{end_date}'
            {constraint_query}
            ORDER BY {index_name}
        '''
        print (get_info_str(__name__), f"SQL: {query}")
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns).set_index(index_name)
        
    finally:
        conn.close()

    # 檢查資料完整性
    if df.isnull().values.any():
        nan_info = df.isnull()
        nan_dates = df.index[nan_info.any(axis=1)].tolist()
        nan_stocks = df.columns[nan_info.any(axis=0)].tolist()
        print(get_warn_str(__name__), f"pivot_df 含有 NaN 值！\n缺漏日期: {nan_dates}\n缺漏股票: {nan_stocks}")
    
    # 統一欄位名稱
    df = rename_df_columns(df, table_name)
    # 依格式轉換查詢完的 index
    if use_roc:
        df.index = [to_ad(idx) for idx in df.index]
    return df


def get_feature_df(df: pd.DataFrame, feature_name: str, key_value: str):
    """
    取得 df 中，feature_name 為 key_value 的資料
    example: feature_df = process_df.get_feature_df(df, 'stock_id', '2330')
    """
    feature_df = df.copy()
    feature_df = feature_df[feature_df[feature_name] == key_value]
    return feature_df


def get_db_pivot_df(table_name: str = 'price', date_range_str: str = '-100:-0', column_name: str = 'stock_id', value_name: str = '收盤價') -> pd.DataFrame:
    """
    - date_range_str: date_str 格式，預設 '-100:-0' (end_date: today, start_date: today-100)
    - column_name: 欄位名稱，預設 'stock_id'
    - value_name: 欄位名稱，預設 '收盤價'

    api 會自動處理 table_name 資料表資料，並回傳 pivot_df。
    - table_name: 資料表名稱，預設 'price'
    - index: date
    - columns: stock_id
    - values: value_name (如收盤價、成交量)
    
    * example: close_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str='-100:-0', column_name='stock_id', value_name='收盤價')
    """ 
    (start_date, end_date) = parse_date_range(date_range_str)
    conn = get_connection()
    cursor = conn.cursor()

    # 判斷是否需要民國年格式
    cursor.execute(f'SELECT DISTINCT date FROM {table_name} ORDER BY date DESC LIMIT 1')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    latest_date = pd.DataFrame(rows, columns=columns).iloc[0, 0]
    date_fmt = check_date_format(latest_date)

    use_roc = date_fmt == 'YYY-MM-DD'

    if use_roc:
        start_date = to_roc(start_date)
        end_date = to_roc(end_date)
    

    origin_col = reverse_column_mapping(table_name, column_name.strip())
    origin_val = reverse_column_mapping(table_name, value_name.strip())
    #[TODO] stock_id like '____' 
    try:
        query = f'''
            SELECT stock_id, date, {origin_val}
            FROM {table_name}
            WHERE date BETWEEN '{start_date}' AND '{end_date}'
            AND stock_id like '____'
            ORDER BY {origin_col}, date
        '''
        print (get_info_str(__name__), f"SQL: {query}")
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        pivot_df = df.pivot(index='date', columns=origin_col, values=origin_val)
        # 查詢完將民國年轉回西元年
        if use_roc:
            pivot_df.index = [to_ad(idx) for idx in pivot_df.index]
    finally:
        conn.close()
    # 檢查資料完整性
    if pivot_df.isnull().values.any():
        nan_info = pivot_df.isnull()
        nan_dates = pivot_df.index[nan_info.any(axis=1)].tolist()
        nan_stocks = pivot_df.columns[nan_info.any(axis=0)].tolist()
        print(get_warn_str(__name__), f"pivot_df 含有 NaN 值！\n缺漏日期: {nan_dates}\n缺漏股票: {nan_stocks}")
    
    # 統一欄位名稱
    pivot_df = rename_df_columns(pivot_df, table_name)
    return pivot_df


### dealer
def get_branch_data(date_range_str: str = '-10:-0', stock_col: str = "股票名稱", view_dealer_col: str = "買進金額, 賣出金額", constraint_str: str = "") -> pd.DataFrame:
    """ 讀取券商交易數據 
    
    - date_range_str: date_str 格式，預設 '-10:-0' (end_date: today, start_date: today-10)
    - stock_col: 欄位名稱，預設 '股票名稱'
    - view_dealer_col: 欄位名稱，預設 '買進金額, 賣出金額'

    欄位可參考 : print('dealer 資料表欄位：', db_lib.list_columns('dealer'))
    
    api 會自動處理 dealer 資料表資料，並回傳 pivot_df。
    - index: date
    - columns: stock_col, 分點名稱
    - values: 買進張數, 賣出張數, 買進金額, 賣出金額
    
    * example: branch_df = process_df.get_branch_data(date_range_str='-10:-0', stock_col='股票代號', view_dealer_col='買進金額, 賣出金額', constraint_str="股票代號 = 2330")
    """
    
    branch_df = get_db_df(table_name='dealer', date_range_str=date_range_str, column_str=f"{stock_col}, 分點名稱, {view_dealer_col}", constraint_str=constraint_str)
    
    return branch_df

### price
def get_stock_data(date_range_str: str = '-10:-0', column_str: str = """stock_id, 開盤價, 收盤價, 最高價, 最低價, 成交股數""") -> pd.DataFrame:
    """ 讀取個股行情數據 
    - date_range_str: date_str 格式，預設 '-100:-0' (end_date: today, start_date: today-100)
    - column_str: 欄位名稱，預設 'stock_id, 開盤價, 收盤價, 最高價, 最低價, 成交股數'
    

    欄位可參考 : print('price 資料表欄位：', db_lib.list_columns('price'))

    api 會自動處理 price 資料表資料，並回傳 pivot_df。
    - index: date
    - columns: stock_id
    - values: 開盤價, 收盤價, 最高價, 最低價, 成交股數
    
    * example: stock_df = process_df.get_stock_data(date_range_str='-10:-0', column_str='stock_id, 開盤價, 收盤價, 最高價, 最低價, 成交股數')
    """
    stock_df = get_db_df(table_name='price', date_range_str=date_range_str, index_name='date', column_str=column_str)
    return stock_df


### monthly_revenue
def get_monthly_revenue_data(date_range_str: str = '-10:-0', column_name: str = 'stock_id', value_name: str = '當月營收') -> pd.DataFrame:
    monthly_revenue_pivot_df = get_db_pivot_df(table_name='monthly_revenue', date_range_str=date_range_str, column_name=column_name, value_name=value_name)

    # 將資料點補到每月 10 號，只保留每月 10 號
    monthly_revenue_pivot_df.index = pd.to_datetime(monthly_revenue_pivot_df.index)
    # 取每月 10 號的日期範圍
    all_10th = pd.date_range(start=monthly_revenue_pivot_df.index.min(), end=monthly_revenue_pivot_df.index.max(), freq='MS') + pd.Timedelta(days=9)
    # 只保留在 DataFrame index 範圍內的 10 號
    all_10th = all_10th[(all_10th >= monthly_revenue_pivot_df.index.min()) & (all_10th <= monthly_revenue_pivot_df.index.max())]
    # 用 forward fill 方式將每個月的資料補到 10 號
    monthly_revenue_pivot_df_ffill = monthly_revenue_pivot_df.reindex(monthly_revenue_pivot_df.index.union(all_10th)).sort_index().ffill()
    monthly_revenue_pivot_df_10th = monthly_revenue_pivot_df_ffill.loc[all_10th]
    return monthly_revenue_pivot_df_10th