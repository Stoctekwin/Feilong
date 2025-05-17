"""
filter.py - 條件式資料篩選工具

核心理念：
- 將常見的技術分析條件（如均線多頭排列、均線糾纏等）封裝成可重用的 DataFrame 濾網。
- 支援價格、成交量等各類型資料的多重條件篩選。
- 每個濾網 function 都回傳滿足條件的 DataFrame，便於串接與組合。
- 可用於自動選股、量化回測、策略研究等場景。
"""
import pandas as pd
from typing import List


def golden_alignment_pivot(ma_pivots: dict, ma_list: list) -> pd.DataFrame:
    """
    pivot_df 版本多頭排列篩選。
    ma_pivots: dict, e.g. {'MA5': df, 'MA10': df, ...}，每個 df 為 pivot 結構
    ma_list: e.g. [5, 10, 20, 60, 120]
    回傳：同樣是 pivot 結構，True 表示該日該股多頭排列
    """
    cond = ma_pivots[f'MA{ma_list[0]}'] >= ma_pivots[f'MA{ma_list[1]}']
    for i in range(1, len(ma_list)-1):
        cond = cond & (ma_pivots[f'MA{ma_list[i]}'] >= ma_pivots[f'MA{ma_list[i+1]}'])
    return cond


def ma_entangled_pivot(ma_pivots: dict, ma_list: list, tol: float = 0.01) -> pd.DataFrame:
    """
    pivot_df 版本均線糾纏篩選。
    ma_pivots: dict, e.g. {'MA5': df, 'MA10': df, ...}，每個 df 為 pivot 結構
    ma_list: e.g. [5, 10, 20]
    tol: 百分比容忍度，預設 1%
    回傳：同樣是 pivot 結構，True 表示該日該股均線糾纏
    """
    base = ma_pivots[f'MA{ma_list[0]}']
    cond = True
    for i in range(1, len(ma_list)):
        cond = cond & ((ma_pivots[f'MA{ma_list[i]}'] - base).abs() / base <= tol)
    return cond

