import pandas as pd

from api import process_df

from api.indicator import (
    sma_pivot_df, ema_pivot_df, wma_pivot_df,
    k_pivot_df, d_pivot_df, macd_pivot_df, williams_pivot_df
)


DATE_RANGE_STR = '-100:-0'

def example_strategy():
    """
    示範如何呼叫六個技術指標 function，並以隨機生成的 pivot df 作為範例。
    """
    
    
    close_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='收盤價')
    volume_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='成交股數')/1000
    high_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='最高價')
    low_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='最低價')

    # 1. SMA
    sma5 = sma_pivot_df(close_pivot, 5)
    # 2. EMA
    ema5 = ema_pivot_df(close_pivot, 5)
    # 3. WMA
    wma5 = wma_pivot_df(close_pivot, volume_pivot, 5)
    # 4. K 指標
    k = k_pivot_df(close_pivot, low_pivot, high_pivot, n=9)
    # 5. D 指標
    d = d_pivot_df(k)
    # 6. MACD
    macd = macd_pivot_df(close_pivot)
    # 7. 威廉指數
    williams = williams_pivot_df(close_pivot, low_pivot, high_pivot, n=14)

    print('SMA5')
    print(sma5)
    print('EMA5')
    print(ema5)
    print('WMA5')
    print(wma5)
    print('K')
    print(k)
    print('D')
    print(d)
    print('MACD')
    print(macd)
    print('Williams %R')
    print(williams)

if __name__ == '__main__':
    example_strategy()
