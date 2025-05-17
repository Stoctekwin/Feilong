import pandas as pd


def sma_pivot_df(pivot_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    計算 n 日簡單移動平均線（SMA），適用於 pivot 結構（index: 日期, columns: 股票代碼）。

    參數：
        pivot_df (pd.DataFrame): 收盤價等指標的 pivot df
        n (int): 計算均線的天數
    回傳：
        pd.DataFrame: n 日 SMA 的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日均線
    範例：
        sma_pivot_df(收盤價_pivot_df, 5)
    """
    sma_pivot_df = pivot_df.rolling(window=n, min_periods=1).mean()
    sma_pivot_df.iloc[:n-1] = pd.NA
    return sma_pivot_df


def ema_pivot_df(pivot_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    計算 n 日指數移動平均線（EMA），適用於 pivot 結構（index: 日期, columns: 股票代碼）。

    參數：
        pivot_df (pd.DataFrame): 收盤價等指標的 pivot df
        n (int): 計算 EMA 的天數
    回傳：
        pd.DataFrame: n 日 EMA 的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日均線
    範例：
        ema_pivot_df(收盤價_pivot_df, 5)
    """
    ema_pivot_df = pivot_df.ewm(span=n, adjust=False).mean()
    ema_pivot_df.iloc[:n-1] = pd.NA
    return ema_pivot_df


def wma_pivot_df(pivot_df: pd.DataFrame, weight_pivot_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    計算 n 日加權移動平均線（WMA），以權重 pivot df 為權重。
    適用於 pivot 結構（index: 日期, columns: 股票代碼）。

    參數：
        pivot_df (pd.DataFrame): 價格等指標的 pivot df
        weight_pivot_df (pd.DataFrame): 權重（如成交量）的 pivot df
        n (int): 計算加權均線的天數
    回傳：
        pd.DataFrame: n 日加權均線的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日均線
    範例：
        wma_pivot_df(收盤價_pivot_df, 成交量_pivot_df, 5)
    """
    weighted_sum = (pivot_df * weight_pivot_df).rolling(window=n, min_periods=1).sum()
    weight_sum = weight_pivot_df.rolling(window=n, min_periods=1).sum()
    wma_pivot_df = weighted_sum / weight_sum
    wma_pivot_df.iloc[:n-1] = pd.NA
    return wma_pivot_df

def n_day_high_pivot_df(pivot_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    計算 n 日創新高價（rolling max），適用於 pivot 結構。

    參數：
        pivot_df (pd.DataFrame): 價格等指標的 pivot df
        n (int): 計算區間天數
    回傳：
        pd.DataFrame: 每天每檔股票 n 日內最高價的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日新高
    範例：
        n_day_high_pivot_df(收盤價_pivot_df, 20)
    """
    n_day_high_pivot_df = pivot_df.rolling(window=n, min_periods=1).max()
    n_day_high_pivot_df.iloc[:n-1] = pd.NA
    return n_day_high_pivot_df


def n_day_low_pivot_df(pivot_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    計算 n 日創新低價（rolling min），適用於 pivot 結構。

    參數：
        pivot_df (pd.DataFrame): 價格等指標的 pivot df
        n (int): 計算區間天數
    回傳：
        pd.DataFrame: 每天每檔股票 n 日內最低價的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日新低
    範例：
        n_day_low_pivot_df(收盤價_pivot_df, 20)
    """
    n_day_low_pivot_df = pivot_df.rolling(window=n, min_periods=1).min()
    n_day_low_pivot_df.iloc[:n-1] = pd.NA
    return n_day_low_pivot_df




def k_pivot_df(close_pivot_df: pd.DataFrame, low_pivot_df: pd.DataFrame, high_pivot_df: pd.DataFrame, n: int = 9) -> pd.DataFrame:
    """
    計算 n 日隨機指標 K 值（Stochastic K），適用於 pivot 結構。

    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
        low_pivot_df (pd.DataFrame): 當日最低價 pivot df
        high_pivot_df (pd.DataFrame): 當日最高價 pivot df
        n (int): 計算區間天數，預設 9
    回傳：
        pd.DataFrame: n 日 K 值的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日 K 值
    """
    lowest_low = low_pivot_df.rolling(window=n, min_periods=1).min()
    highest_high = high_pivot_df.rolling(window=n, min_periods=1).max()
    k = (close_pivot_df - lowest_low) / (highest_high - lowest_low) * 100
    k_pivot_df = k
    k_pivot_df.iloc[:n-1] = pd.NA
    return k_pivot_df


def d_pivot_df(k_pivot_df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """
    計算 D 值（K 值的 n 日移動平均），適用於 pivot 結構。

    參數：
        k_pivot_df (pd.DataFrame): K 值的 pivot df
        n (int): 計算 D 值的天數，預設 3
    回傳：
        pd.DataFrame: D 值的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日 D 值
    """
    d_pivot_df = k_pivot_df.rolling(window=n, min_periods=1).mean()
    d_pivot_df.iloc[:n-1] = pd.NA
    return d_pivot_df


def macd_pivot_df(pivot_df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    計算 MACD 指標（僅回傳 MACD 值），適用於 pivot 結構。

    參數：
        pivot_df (pd.DataFrame): 收盤價等指標的 pivot df
        fast (int): 快線 EMA 期數，預設 12
        slow (int): 慢線 EMA 期數，預設 26
        signal (int): 訊號線 EMA 期數，預設 9
    回傳：
        pd.DataFrame: MACD 值的 pivot df
        前 fast-1 天為 NaN 是因為沒有辦法計算前 fast-1 天的 n 日 MACD
    """
    ema_fast = pivot_df.ewm(span=fast, adjust=False).mean()
    ema_slow = pivot_df.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_pivot_df = macd
    macd_pivot_df.iloc[:fast-1] = pd.NA
    return macd_pivot_df


def williams_pivot_df(close_pivot_df: pd.DataFrame, low_pivot_df: pd.DataFrame, high_pivot_df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """
    計算 n 日威廉指數（Williams %R），適用於 pivot 結構。

    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
        low_pivot_df (pd.DataFrame): 當日最低價 pivot df
        high_pivot_df (pd.DataFrame): 當日最高價 pivot df
        n (int): 計算區間天數，預設 14
    回傳：
        pd.DataFrame: n 日 Williams %R 的 pivot df
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日 Williams %R
    """
    lowest_low = low_pivot_df.rolling(window=n, min_periods=1).min()
    highest_high = high_pivot_df.rolling(window=n, min_periods=1).max()
    williams_r = (highest_high - close_pivot_df) / (highest_high - lowest_low) * -100
    williams_r_pivot_df = williams_r
    williams_r_pivot_df.iloc[:n-1] = pd.NA
    return williams_r_pivot_df

def add_ma(df: pd.DataFrame, n: int, price_col: str = '收盤價') -> pd.DataFrame:
    """
    計算 n 日移動平均線（MA），並新增欄位 MA{n}
    """
    df = df.copy()
    df[f'MA{n}'] = df[price_col].rolling(window=n, min_periods=1).mean()
    return df


def add_ma_pivots(df: pd.DataFrame, ma_list: list) -> dict:
    """
    計算 n 日移動平均線（MA），並新增欄位 MA{n}
    """
    ma_pivots = {}
    for n in ma_list:
        ma_pivots[f'MA{n}'] = df.rolling(window=n, min_periods=1).mean()
    return ma_pivots

def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, price_col: str = '收盤價') -> pd.DataFrame:
    """
    計算 MACD 指標，並新增欄位 MACD, MACD_signal, MACD_hist
    """
    df = df.copy()
    ema_fast = df[price_col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[price_col].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    return df

