import pandas as pd
from api.indicator import (
    sma_pivot_df, ema_pivot_df, wma_pivot_df,
    n_day_high_pivot_df, n_day_low_pivot_df
)


#### 創新高/低家數

def count_n_day_high(pivot_df: pd.DataFrame, n: int) -> pd.Series:
    """
    計算每天創 n 日新高價的股票家數。
    參數：
        pivot_df (pd.DataFrame): 價格等指標的 pivot df
        n (int): 區間天數
    回傳：
        pd.Series: index 為日期，每天創 n 日新高的家數（前 n-1 天為 NaN）
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日新高
    """
    high_df = n_day_high_pivot_df(pivot_df, n)
    is_new_high = pivot_df == high_df
    result = is_new_high.sum(axis=1)
    result.iloc[:n-1] = pd.NA
    return result

def count_n_day_low(pivot_df: pd.DataFrame, n: int) -> pd.Series:
    """
    計算每天創 n 日新低價的股票家數。
    參數：
        pivot_df (pd.DataFrame): 價格等指標的 pivot df
        n (int): 區間天數
    回傳：
        pd.Series: index 為日期，每天創 n 日新低的家數（前 n-1 天為 NaN）
        前 n-1 天為 NaN 是因為沒有辦法計算前 n-1 天的 n 日新低
    """
    low_df = n_day_low_pivot_df(pivot_df, n)
    is_new_low = pivot_df == low_df
    result = is_new_low.sum(axis=1)
    result.iloc[:n-1] = pd.NA
    return result



#### 上漲、持平、下跌家數

def get_total_count_per_date(close_pivot_df: pd.DataFrame) -> pd.Series:
    """
    計算今天與昨天皆有收盤價的股票總家數。
    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
    回傳：
        pd.Series: index 為日期，連續兩天有收盤價的股票總家數
        第一天沒有前一交易日，因此第一天為 NaN
    """
    # 有成交價的家數
    prev_close = close_pivot_df.shift(1)
    total_count = (close_pivot_df.notna() & prev_close.notna()).sum(axis=1)
    total_count.iloc[0] = pd.NA
    return total_count


def get_close_above_count(close_pivot_df: pd.DataFrame) -> pd.Series:
    """
    計算今天與昨天皆有收盤價的股票中，今天收盤價 > 昨天收盤價（上漲家數）。
    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
    回傳：
        pd.Series: index 為日期，連續兩天有收盤價的股票中，今天收盤價 > 昨天收盤價的家數
        第一天沒有前一交易日，因此第一天為 NaN
    """
    prev_close = close_pivot_df.shift(1)
    above_count = (close_pivot_df > prev_close).sum(axis=1)
    above_count.iloc[0] = pd.NA
    return above_count

def get_close_below_count(close_pivot_df: pd.DataFrame) -> pd.Series:
    """
    計算今天與昨天皆有收盤價的股票中，今天收盤價 < 昨天收盤價（下跌家數）。
    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
    回傳：
        pd.Series: index 為日期，連續兩天有收盤價的股票中，今天收盤價 < 昨天收盤價的家數
        第一天沒有前一交易日，因此第一天為 NaN
    """
    prev_close = close_pivot_df.shift(1)
    below_count = (close_pivot_df < prev_close).sum(axis=1)
    below_count.iloc[0] = pd.NA
    return below_count

def get_close_flat_count(close_pivot_df: pd.DataFrame) -> pd.Series:
    """
    計算今天與昨天皆有收盤價的股票中，今天收盤價 = 昨天收盤價（持平家數）。
    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
    回傳：
        pd.Series: index 為日期，連續兩天有收盤價的股票中，今天收盤價 = 昨天收盤價的家數
        第一天沒有前一交易日，因此第一天為 NaN
    """
    prev_close = close_pivot_df.shift(1)
    flat_count = (close_pivot_df == prev_close).sum(axis=1)
    flat_count.iloc[0] = pd.NA
    return flat_count

#### SMA/EMA/WMA 站上家數

def count_above_ma(close_pivot_df: pd.DataFrame, volume_pivot_df: pd.DataFrame, n: int, ma_type: str = 'sma') -> pd.Series:
    """
    計算每天收盤價站上 n 日均線（SMA/EMA/WMA）的股票家數。
    參數：
        close_pivot_df (pd.DataFrame): 收盤價 pivot df
        volume_pivot_df (pd.DataFrame): 成交量 pivot df
        n (int): 均線天數
    回傳：
        pd.Series: index 為日期，每天站上 n 日均線的家數（前 n-1 天為 NaN）
    """
    if ma_type == 'sma':
        ma_df = sma_pivot_df(close_pivot_df, n)
    elif ma_type == 'ema':
        ma_df = ema_pivot_df(close_pivot_df, n)
    elif ma_type == 'wma':
        ma_df = wma_pivot_df(close_pivot_df, volume_pivot_df, n)
    result = (close_pivot_df > ma_df).sum(axis=1)
    result.iloc[:n-1] = pd.NA
    return result
