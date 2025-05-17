

import sys
import io
from api import db_lib
from api import process_df
from api import indicator
from api import plot
from api import filter
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
import matplotlib
matplotlib.use("TkAgg")

# ====== 參數與常數設定 ======
# 均線天數列表
MA_LIST = [5, 10, 20, 60]

# main 使用到的參數
TOP_BROKERS_RANK = 3  # 如果數字調整，plot_combined_chart 裡 plt.subplots(nrows=5) 的 5 也要調整
# DATE_RANGE_STR = '-100:-0' 
DATE_RANGE_STR = '2025-04-01:2025-04-15'
VIEW_DEALER_COL = '金額' 

# ====== 資料載入區 ======
def load_stock_data() -> None:
    """
    從資料庫讀取各項股價資料，存入全域變數。
    本範例會自動取得近 100 天的所有股票價格資料。
    """
    global volume_df, open_df, close_df, high_df, low_df
    close_df  = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='close').astype(float)
    open_df   = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='open').astype(float)
    high_df   = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='high').astype(float)
    low_df    = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='low').astype(float)
    volume_df = process_df.get_db_pivot_df(table_name='price', date_range_str=DATE_RANGE_STR, column_name='stock_id', value_name='成交股數').astype(float) / 1000

def plot_combined_chart(stock_id: str, stock_df: pd.DataFrame, branch_df: pd.DataFrame, top_brokers: list) -> None:
    """
    繪製多張股票分析圖：
    1. K 線圖 + 均線
    2. 成交量圖
    3. 前三大券商的買賣金額行為
    Args:
        stock_id (str):  stock_id 
        stock_df (pd.DataFrame): 單一股票 K 線資料
        branch_df (pd.DataFrame): 分點券商買賣資料
        top_brokers (list): 買賣超金額最大的券商名稱
    """
    plot_stock_df = stock_df.copy()
    plot_branch_df = branch_df.copy()
    # 僅保留有對應 K 線的日期
    plot_branch_df = plot_branch_df[plot_branch_df.index.isin(plot_stock_df.index)]
    fig, subplots = plt.subplots(nrows=(TOP_BROKERS_RANK+2), ncols=1, sharex=True,
                                gridspec_kw={'height_ratios': [4, 2, 2, 2, 2]},
                                figsize=(14, 9))
    # ====== K 線圖區 ======
    ax_candle = subplots[0]
    ax_candle.set_title(f"{stock_id} K 線圖", fontsize=14)
    x_values = plot_stock_df.index.to_numpy()
    colors = ['g' if o <= c else 'r' for o, c in zip(plot_stock_df["Open"], plot_stock_df["Close"])]
    ax_candle.bar(x_values, plot_stock_df["Close"] - plot_stock_df["Open"], bottom=plot_stock_df["Open"], color=colors, width=0.5)
    ax_candle.vlines(x_values, plot_stock_df["Low"], plot_stock_df["High"], color=colors, linewidth=1)
    # 畫均線
    ma_colors = ["blue", "orange", "purple", "brown"]
    for ma, color in zip(MA_LIST, ma_colors):
        plot_stock_df[f"MA{ma}"] = plot_stock_df["Close"].rolling(ma).mean().reindex(plot_stock_df["Close"].index, method='ffill').dropna()
        ax_candle.plot(np.array(plot_stock_df[f"MA{ma}"].index[:]), plot_stock_df[f"MA{ma}"].to_numpy(), label=f"{ma} 日均線", color=color)
    ax_candle.legend()
    ax_candle.set_ylabel("價格")
    # ====== 成交量圖區 ======
    ax_volume = subplots[1]
    volume_max = plot_stock_df["Volume"].max()
    volume_scale = ''
    if volume_max > 1000000:
        volume_scale = '(M)'
        plot_stock_df["Volume"] = plot_stock_df["Volume"] / 1000000
    elif volume_max > 1000:
        volume_scale = '(K)'
        plot_stock_df["Volume"] = plot_stock_df["Volume"] / 1000
    ax_volume.bar(x_values, plot_stock_df["Volume"], color="gray")
    ax_volume.set_ylabel(f"成交量{volume_scale}", fontsize=10)
    for ma, color in zip(MA_LIST, ma_colors):
        plot_stock_df[f"MA{ma}"] = plot_stock_df["Volume"].rolling(ma).mean().reindex(plot_stock_df["Volume"].index, method='ffill').dropna()
        ax_volume.plot(np.array(plot_stock_df[f"MA{ma}"].index[:]), plot_stock_df[f"MA{ma}"].to_numpy(), label=f"{ma} 日均線", color=color)
    ax_volume.legend()
    ax_volume.set_ylabel("價格")
    # ====== 券商分點圖區 ======
    branch_item = '金額'
    broker_axes = subplots[2:]
    for i, (broker, ax) in enumerate(zip(top_brokers, broker_axes)):
        broker_data = plot_branch_df[plot_branch_df["分點名稱"] == broker]
        x_values = broker_data.index.to_numpy()
        volume_max = broker_data[f"買進{branch_item}"].max() if not broker_data.empty else 0
        volume_scale = ''
        resize_ratio = 1
        if volume_max > 1000000:
            volume_scale = '(M)'
            resize_ratio = 1000000
        elif volume_max > 1000:
            volume_scale = '(K)'
            resize_ratio = 1000
        ax.bar(x_values, broker_data[f"買進{branch_item}"] / resize_ratio, color="black", label="買進")
        ax.bar(x_values, -broker_data[f"賣出{branch_item}"] / resize_ratio, color="gray", label="賣出")
        ax.bar(x_values, broker_data[f"買賣超{branch_item}"] / resize_ratio, color=["r" if v > 0 else "g" for v in broker_data[f"買賣超{branch_item}"]], alpha=0.5, label="買賣超")
        ax.axhline(0, color="black", linewidth=1)
        ax.legend()
        ax.set_title(f"{broker} 的買賣{branch_item}{volume_scale}行為", fontsize=12)
    # 多圖游標同步
    MultiCursor(fig.canvas, [axe for axe in subplots], color='r', lw=1, horizOn=False, vertOn=True)
    plt.show()


def main() -> None:
    """
    主流程說明：
    1. 顯示資料表與欄位資訊（驗證資料庫連線）
    2. 載入近 100 天所有股票資料
    3. 互動式輸入 stock_id ，顯示該股票 K 線圖
    4. 取得並分析分點券商資料，顯示前三大券商買賣行為
    """

    print('所有資料表：', db_lib.list_tables())
    print('dealer 資料表欄位：', db_lib.list_columns('dealer'))
    load_stock_data()
    stock_id = input("請輸入 stock_id : ").strip()
    if stock_id not in close_df.columns:
        print(f" stock_id {stock_id} 不存在於數據集中！")
        return
    # 取得該股票的完整 K 線數據（包含成交量、開高低收）
    observed_stock_df = pd.concat([
        volume_df[stock_id], open_df[stock_id], close_df[stock_id],
        high_df[stock_id], low_df[stock_id]
    ], axis=1)
    observed_stock_df.columns = ['Volume', 'Open', 'Close', 'High', 'Low']
    observed_stock_df.index = pd.to_datetime(observed_stock_df.index)
    # 計算多條均線
    for ma in MA_LIST:
        observed_stock_df[f"MA{ma}"] = observed_stock_df["Close"].rolling(ma).mean()
    # 畫出基本 K 線圖
    plt.figure(figsize=(10, 4))
    plt.plot(np.array(observed_stock_df.index), observed_stock_df["Close"].to_numpy(), label="close", color="b")
    plt.fill_between(observed_stock_df.index, observed_stock_df["Low"], observed_stock_df["High"], color="gray", alpha=0.3)
    plt.title(f"{stock_id} 股票 K 線圖")
    plt.xlabel("日期")
    plt.ylabel("價格")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show(block=True)
    # 取得分點券商資料
    branch_df = process_df.get_branch_data(date_range_str=DATE_RANGE_STR, stock_col='stock_id', view_dealer_col=f'買進{VIEW_DEALER_COL}, 賣出{VIEW_DEALER_COL}', constraint_str=f"stock_id = {stock_id}")
    branch_df['買賣超金額'] = branch_df['買進金額'] - branch_df['賣出金額']
    branch_df.index = pd.to_datetime(branch_df.index)
    # 找出累積買賣超金額最大的前 N 大券商
    top_brokers = branch_df.copy()
    top_brokers["買賣超金額"] = pd.to_numeric(top_brokers["買賣超金額"], errors="coerce")
    top_brokers = top_brokers.dropna(subset=["買賣超金額"])
    broker_summary = top_brokers.groupby(["分點名稱"]).agg({'買賣超金額': 'sum'})
    top_brokers_list = broker_summary.nlargest(TOP_BROKERS_RANK, "買賣超金額").reset_index()['分點名稱'].values
    print(f"前 {TOP_BROKERS_RANK} 大累積買賣金額的券商：")
    print(top_brokers_list)
    # 畫出綜合圖表
    plot_combined_chart(stock_id, observed_stock_df, branch_df, top_brokers_list)


if __name__ == "__main__":
    # ====== 程式主入口 ======
    # 執行本檔案即可啟動互動式股票分析流程
    main()
