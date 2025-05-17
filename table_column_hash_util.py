

import os
from api import db_lib
from typing import Dict, List
import pandas as pd



if __name__ == '__main__':
    print('--- Step 1: 產生/更新 table column hash ---')
    db_lib.save_column_hash()

    print('--- Step 2: 反向查詢範例 ---')
    # 範例：將熟悉名稱 'stock_id' 查回原始 table 欄位名稱
    table = 'dealer'  # 請替換為實際 table 名稱
    familiar_col = 'stock_id'  # 請替換為實際熟悉名稱
    origin_col = db_lib.reverse_column_mapping(table, familiar_col)
    print(f"熟悉名稱 '{familiar_col}' 對應的原始欄位名稱: {origin_col}")

    print('--- Step 3: 產生人工可讀的 table 對應表 ---')
    df = db_lib.get_table_column_mapping_df()
    # print(df)