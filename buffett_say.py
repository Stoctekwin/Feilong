import pandas as pd
from api import process_df
from api.indicator import sma_pivot_df

# 參數
trace_last = int(120/5*7)+100
# trace_last = 3000
DATE_RANGE_STR = f'-{trace_last}:-0'  # 可依需求調整

# 1. 取得所需 pivot df
close_pivot = process_df.get_db_pivot_df('price', DATE_RANGE_STR, 'stock_id', '收盤價')
volume_pivot = process_df.get_db_pivot_df('price', DATE_RANGE_STR, 'stock_id', '成交股數')
# pe_pivot = process_df.get_db_pivot_df('fundamental', DATE_RANGE_STR, 'stock_id', '本益比')
# pb_pivot = process_df.get_db_pivot_df('fundamental', DATE_RANGE_STR, 'stock_id', '股價淨值比')
# yield_pivot = process_df.get_db_pivot_df('fundamental', DATE_RANGE_STR, 'stock_id', '殖利率')
# eps_pivot = process_df.get_db_pivot_df('fundamental', DATE_RANGE_STR, 'stock_id', 'EPS')
# mo_revenue_pivot = process_df.get_db_pivot_df('monthly_revenue', DATE_RANGE_STR, 'stock_id', '當月營收')

# 2. 均線
sma60  = sma_pivot_df(close_pivot, 60)
sma120 = sma_pivot_df(close_pivot, 120)

# 3. 成交量大於50%（以每檔股票近100日中位數為基準）
volume_median = volume_pivot.median(axis=0)
volume_50pct = volume_pivot > (volume_median * 0.5)

# 4. EPS > 前季EPS（假設季資料為橫向，若為直向請調整 axis）
# eps_prev = eps_pivot.shift(1)
# eps_up = eps_pivot > eps_prev

# 5. 月營收 > 前年同月（月營收資料 index 為日期，columns 為股票）
# mo_revenue_prev_year = mo_revenue_pivot.shift(12)
# mo_revenue_up = mo_revenue_pivot > mo_revenue_prev_year

# 6. 條件篩選
criteria = (
    # (pe_pivot < 15) &
    # (pb_pivot < 2) &
    # (yield_pivot > 4) &
    volume_50pct &
    (close_pivot > sma60) &
    (close_pivot > sma120) #&
    # eps_up &
    # mo_revenue_up
)

# Debug: 各條件每天有多少股票符合
print("volume_50pct 每天家數:", volume_50pct.sum(axis=1).tail())
print("close_pivot > sma60 每天家數:", (close_pivot > sma60).sum(axis=1).tail())
print("close_pivot > sma120 每天家數:", (close_pivot > sma120).sum(axis=1).tail())
# print("mo_revenue_up 每天家數:", mo_revenue_up.sum(axis=1).tail())

# 7. 挑選結果
selected = criteria & criteria.notna()

# 8. 輸出最後一天的結果
latest_date = selected.index[-1]
selected_stocks = selected.loc[latest_date]
print(f"巴菲特選股條件，{latest_date} 符合的股票:")
print(selected_stocks[selected_stocks].index.tolist())

# Debug: 最後一天各條件分別符合的股票
print("\n最後一天 volume_50pct:", volume_50pct.loc[latest_date][volume_50pct.loc[latest_date]].index.tolist())
print("最後一天 close_pivot > sma60:", (close_pivot > sma60).loc[latest_date][(close_pivot > sma60).loc[latest_date]].index.tolist())
print("最後一天 close_pivot > sma120:", (close_pivot > sma120).loc[latest_date][(close_pivot > sma120).loc[latest_date]].index.tolist())
# print("最後一天 mo_revenue_up:", mo_revenue_up.loc[latest_date][mo_revenue_up.loc[latest_date]].index.tolist())

# 若需完整篩選表，請取消以下註解
selected.to_csv('buffett_selected_full.csv')

# 9. 串接回測
from api.backtest import run_backtest
# perf, returns, exit_flag = run_backtest(
#     buy_signal=selected.astype(int),
#     close_pivot=close_pivot,
#     stop_loss=0.1,      # 範例: 10% 停損
#     take_profit=0.2,    # 範例: 20% 停利
#     trailing_stop=None, # 若要動態停利請設數值
#     debug=True          # 開啟 debug 方便追蹤
# )
# print("\n回測績效 (每檔股票最大單次交易報酬率):")
# print(perf.sort_values(ascending=False).dropna())
