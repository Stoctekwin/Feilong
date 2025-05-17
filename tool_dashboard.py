# %%
import pandas as pd
import matplotlib.pyplot as plt
from api import process_df
from api.dashboard import (
    count_n_day_high, count_n_day_low, count_above_ma, get_total_count_per_date,
    get_close_flat_count, get_close_above_count, get_close_below_count
)


parse_date = '-20:-0'

# 取得近 100 日多股收盤價、成交量 pivot df
close_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=parse_date, column_name='stock_id', value_name='收盤價')
volume_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=parse_date, column_name='stock_id', value_name='成交股數') / 1000


# %%


print(close_pivot)

# %%
print(volume_pivot['2330'])

# %%

n = 5

# 1. 5日創新高家數
high_count = count_n_day_high(close_pivot, n)
# 2. 5日創新低家數
low_count = count_n_day_low(close_pivot, n)
# 3. 5日 SMA 站上家數
above_sma_count = count_above_ma(close_pivot, volume_pivot, n, ma_type='sma')
# 4. 5日 EMA 站上家數
above_ema_count = count_above_ma(close_pivot, volume_pivot, n, ma_type='ema')
# 5. 5日 WMA 站上家數
above_wma_count = count_above_ma(close_pivot, volume_pivot, n, ma_type='wma')

# 總家數與持平家數（以 SMA 為例）
total_count = get_total_count_per_date(close_pivot)
flat_count = get_close_flat_count(close_pivot)
above_count = get_close_above_count(close_pivot)
below_count = get_close_below_count(close_pivot)

# %%

print("總家數", total_count)

# %%
print("持平家數", flat_count)

# %%
print("上漲家數", above_count)

# %%
print("下跌家數", below_count)

# %%

print(high_count)

# %%

print(low_count)

# %%

print(above_sma_count)

# %%

print(above_ema_count)

# %%

print(above_wma_count)

# %%

print('總家數:')
print(total_count)
print('持平家數:')
print(flat_count)

# %%

# 畫圖
plt.figure(figsize=(12, 8))
plt.plot(high_count, label=f'{n}日新高家數')
plt.plot(low_count, label=f'{n}日新低家數')
plt.plot(above_sma_count, label=f'站上{n}日SMA家數')
plt.plot(above_ema_count, label=f'站上{n}日EMA家數')
plt.plot(above_wma_count, label=f'站上{n}日WMA家數')
plt.plot(total_count, label='總家數', linestyle='--', color='gray')
plt.plot(flat_count, label='持平家數', linestyle=':', color='brown')
plt.title(f'{n}日創新高/低與均線家數統計')
plt.xlabel('日期')
plt.ylabel('家數')
plt.legend()
plt.tight_layout()
plt.show()

