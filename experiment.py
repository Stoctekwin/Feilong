

# %%
import sys
import io
from api import db_lib
from api import process_df
from api import indicator
from api import plot
from api import filter





# %%

MONTHLY_REVENUE_DATE_RANGE_STR = '2024-03-01:2024-06-31'

# %%

if __name__ == '__main__':
    # 萬用均線篩選實驗腳本，僅需調整 ma_list 參數即可彈性應用於各種均線組合
    # 設計理念：所有條件、欄位、函式皆自動依據 ma_list 推導，便於重用與擴充

    db_lib.list_tables()
    db_lib.list_columns('price')

    # 月營收範例
    
    monthly_revenue_pivot_df = process_df.get_monthly_revenue_data(MONTHLY_REVENUE_DATE_RANGE_STR)
    print(monthly_revenue_pivot_df)


    #### Step1 : 從 Maria DB 抓取 df
    # 單股抓法 : 抓收盤價，並過濾 2330 的範例
    df = process_df.get_db_df(table_name='price', date_range_str='-100:-0', index_name='date', column_str='stock_id, 收盤價')
    feature_df = process_df.get_feature_df(df, 'stock_id', '2330')
    print(feature_df)

    
    branch_df = process_df.get_branch_data(date_range_str='-10:-0', stock_col='股票名稱', view_dealer_col='買進金額, 賣出金額', constraint_str="股票名稱 = 台積電")
    print(branch_df)

    branch_df = process_df.get_branch_data(date_range_str='-10:-0', stock_col='股票代號', view_dealer_col='買進金額, 賣出金額', constraint_str="股票代號 = 2330")

    branch_df = process_df.get_branch_data(date_range_str='-10:-0', stock_col='stock_id', view_dealer_col='買進金額, 賣出金額', constraint_str="stock_id = 2330")
    print(branch_df)


    # ---- 只需修改這一行即可更換均線組合 ----
    ma_list = [5, 10, 20, 60, 120]
    # --------------------------------------
    # 自動決定資料量，確保最大均線能正確計算
    lookback = int(max(ma_list) / 5 * 7+ 100)  # 冗餘天數以防資料缺漏

    # 多股抓法 : 取得收盤價 pivot_df：index=date, columns=stock_id
    close_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=f'-{lookback}:-0', column_name='stock_id', value_name='收盤價')


    #### Step2 : 計算 indicator
    
    # 計算各均線（每一檔股票為一欄）
    ma_pivots = indicator.add_ma_pivots(close_pivot, ma_list)


    #### Step3 : 做濾網篩選
    # 範例1：多頭排列（所有股票同時滿足多頭排列的日期）
    
    golden = filter.golden_alignment_pivot(ma_pivots, ma_list)
    print(f'--- 均線多頭排列({">=".join([f"MA{n}" for n in ma_list])}) 篩選結果 ---')
    print(golden)

    # 範例2：均線糾纏（以 ma_list 前3條為例）
    entangled = filter.ma_entangled_pivot(ma_pivots, ma_list[:3], tol=0.01)
    print(f'--- 均線糾纏({", ".join([f"MA{n}" for n in ma_list[:3]])}) 篩選結果 ---')


    #### Step4 : 驗證、畫圖

    # --- 指定股票代號進行圖像化驗證 ---
    # 可根據 golden/entangled 結果動態取得股票代號
    # 取得所有出現過的股票代號
    stock_ids = list(golden.columns.union(entangled.columns))
    # 彈性支援多檔股票疊圖
    # 假設 close_pivot 是原始收盤價 pivot_df，ma_pivots 已計算好
    # 需組合出單一股票的 DataFrame（含收盤價與所有 MA）

    plot_stock_id = '0050'

    print(f"繪製 {plot_stock_id} 多頭排列圖...")
    df = close_pivot[[plot_stock_id]].rename(columns={plot_stock_id: '收盤價'}).copy()
    # 取得成交量 pivot 並對齊合併
    volume_pivot = process_df.get_db_pivot_df(table_name='price', date_range_str=f'-{lookback}:-0', column_name='stock_id', value_name='成交股數')
    df['成交量'] = volume_pivot[plot_stock_id].values/1000 if plot_stock_id in volume_pivot.columns else 0
    ma_cols = []
    for n in ma_list:
        df[f'MA{n}'] = ma_pivots[f'MA{n}'][plot_stock_id]
        ma_cols.append(f'MA{n}')
    df = df.reset_index().rename(columns={'index': 'date'})
    if golden[plot_stock_id].any():
        plot.plot_overlay(df, ma_cols, stock_id=plot_stock_id, title=f"{plot_stock_id} 多頭排列驗證")
    print(f"繪製 {plot_stock_id} 均線糾纏圖...")
    if entangled[plot_stock_id].any():
        plot.plot_overlay(df, ma_cols, stock_id=plot_stock_id, title=f"{plot_stock_id} 均線糾纏驗證")
