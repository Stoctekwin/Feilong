import pandas as pd
import numpy as np

def run_backtest(
    buy_signal: pd.DataFrame,
    close_pivot: pd.DataFrame,
    stop_loss: float = None,
    take_profit: float = None,
    trailing_stop: float = None,
    debug: bool = False
):
    """
    彈性回測：根據買進訊號 DataFrame，遇到 0 則賣出換股，可設定停損、停利、動態停利。
    buy_signal: DataFrame, 1=持有, 0=空手，index=日期, columns=股票
    close_pivot: DataFrame, index=日期, columns=股票
    stop_loss: 跌幅停損百分比（如0.1=10%），None表示不啟用
    take_profit: 漲幅停利百分比（如0.2=20%），None表示不啟用
    trailing_stop: 動態停利百分比（如0.15=15%），None表示不啟用
    debug: 是否印出每次買賣資訊
    回傳：績效 DataFrame
    """
    df = close_pivot.copy()
    position = buy_signal.fillna(0).astype(int)
    returns = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
    holding_price = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
    exit_flag = pd.DataFrame(False, index=df.index, columns=df.columns)

    for stock in df.columns:
        pos = 0
        entry_price = 0
        max_price = 0
        for i, date in enumerate(df.index):
            price = df.loc[date, stock]
            sig = position.loc[date, stock]
            if sig == 1 and pos == 0 and pd.notna(price):
                # 開始持有
                pos = 1
                entry_price = price
                max_price = price
                holding_price.loc[date, stock] = entry_price
                if debug:
                    print(f"[{date}] {stock} 買進於 {entry_price}")
            elif sig == 1 and pos == 1:
                # 持有中
                max_price = max(max_price, price) if pd.notna(price) else max_price
                holding_price.loc[date, stock] = entry_price
                # 停損
                if stop_loss is not None and pd.notna(price) and price <= entry_price * (1 - stop_loss):
                    pos = 0
                    exit_flag.loc[date, stock] = True
                    if debug:
                        print(f"[{date}] {stock} 停損賣出 {price}，損益={(price-entry_price)/entry_price:.2%}")
                # 停利
                elif take_profit is not None and pd.notna(price) and price >= entry_price * (1 + take_profit):
                    pos = 0
                    exit_flag.loc[date, stock] = True
                    if debug:
                        print(f"[{date}] {stock} 停利賣出 {price}，損益={(price-entry_price)/entry_price:.2%}")
                # 動態停利
                elif trailing_stop is not None and pd.notna(price) and price <= max_price * (1 - trailing_stop):
                    pos = 0
                    exit_flag.loc[date, stock] = True
                    if debug:
                        print(f"[{date}] {stock} 動態停利賣出 {price}，損益={(price-entry_price)/entry_price:.2%}")
            elif sig == 0 and pos == 1:
                # 換股賣出
                pos = 0
                exit_flag.loc[date, stock] = True
                if debug:
                    print(f"[{date}] {stock} 換股賣出 {price}，損益={(price-entry_price)/entry_price if pd.notna(price) else float('nan'):.2%}")
            else:
                holding_price.loc[date, stock] = np.nan
        # 若最後一天還持有，視為平倉
        if pos == 1:
            exit_flag.iloc[-1][stock] = True
            if debug:
                last_date = df.index[-1]
                last_price = df.loc[last_date, stock]
                print(f"[{last_date}] {stock} 期末平倉 {last_price}，損益={(last_price-entry_price)/entry_price if pd.notna(last_price) else float('nan'):.2%}")

    # 計算報酬率
    returns = (df - holding_price) / holding_price
    returns[~exit_flag] = np.nan

    # 統計績效
    perf = returns.max(skipna=True)
    return perf, returns, exit_flag

# 範例用法：
if __name__ == '__main__':
    # buy_signal, close_pivot 需自行提供
    pass
