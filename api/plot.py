import matplotlib.pyplot as plt
import pandas as pd
from typing import List

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 或 SimHei, PMingLiU
plt.rcParams['axes.unicode_minus'] = False

def plot_overlay(
    df: pd.DataFrame,
    indicator_cols: List[str],
    stock_id: str,
    price_col: str = '收盤價',
    volume_col: str = '成交量',
    date_col: str = 'date',
    title: str = None
):
    """
    將任意指標欄位疊加於收盤價上，並於下方繪製成交量。
    參數：
        df: 資料來源 DataFrame，需包含日期、收盤價、指標、成交量等欄位
        indicator_cols: 欲疊加的指標欄位名稱列表
        stock_id: 指定股票代號
        price_col: 收盤價欄位名稱（預設 '收盤價'）
        volume_col: 成交量欄位名稱（預設 '成交量'）
        date_col: 日期欄位名稱（預設 'date'）
        title: 主圖標題（選填）
    """
    # 若 df 有 'stock_id' 欄位才過濾，否則直接用
    if 'stock_id' in df.columns:
        df = df[df['stock_id'] == stock_id].copy()
        if df.empty:
            raise ValueError(f"查無股票代號 {stock_id} 的資料")
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(14, 8), gridspec_kw={'height_ratios': [3, 1]})
    # 主圖：收盤價與指標
    ax1.plot(df[date_col], df[price_col], label=price_col, color='black')
    for ind in indicator_cols:
        ax1.plot(df[date_col], df[ind], label=ind)
    ax1.set_ylabel('收盤價')
    ax1.legend()
    ax1.set_title(title or f"{stock_id} 收盤價與指標疊圖")
    # 成交量圖
    ax2.bar(df[date_col], df[volume_col], color='gray', width=0.8)
    ax2.set_ylabel('成交量')
    ax2.set_xlabel('日期')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()
