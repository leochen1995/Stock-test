import os
import json
import logging
import requests
import subprocess
import pandas as pd
# import azure.functions as func
from datetime import datetime, timedelta, timezone


# logging.info('Python timer trigger function ran at %s', datetime.datetime.utcnow().isoformat())

# 設定網址
url = "https://www.tpex.org.tw/www/zh-tw/mostActive/brokerVol?id=&response=json"

# 發送 GET 請求
response = requests.get(url)

# 檢查請求是否成功
if response.status_code == 200:
    # 解析 JSON 數據
    data = response.json()
    # 打印數據
    logging.info(json.dumps(data, indent=4, ensure_ascii=False))
    json_data = data

    # 加入新的值到 fields
    json_data["tables"][0]["fields"].append("剩餘量(張)")

    # 儲存到檔案
    with open('modified_data.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    logging.info("已儲存修改後的 JSON 檔案到 'modified_data.json'")

    # 讀取 JSON 檔案
    with open('modified_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 處理每個 data 項目
    for table in data['tables']:
        for item in table['data']:
            # 提取總買量和總賣量
            total_buy = int(item[3])  # 總買量
            total_sell = int(item[4])  # 總賣量
            # 計算差異
            difference = total_buy - total_sell
            # 將結果儲存到最後一個位置，轉換為字串
            item.append(str(difference))  # 轉換為字串以加上引號

    # 將修改後的資料寫入新的 JSON 檔案
    with open('modified_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    logging.info("已成功更新 modified_data.json 檔案。")

    # 將 data 寫入 CSV 檔案
    csv_data = []

    # 收集表頭
    headers = data['tables'][0]['fields']

    # 收集每一行的數據
    for table in data['tables']:
        for item in table['data']:
            csv_data.append(item)


    # 設定 UTC+8 的時區
    utc_8 = timezone(timedelta(hours=8))

    # 獲取當前 UTC+8 的時間
    current_time_utc_8 = datetime.now(utc_8)

    today = current_time_utc_8.strftime('%Y-%m-%d %H-%M-%S')

    # 使用 pandas 將資料寫入 CSV
    df = pd.DataFrame(csv_data, columns=headers)
    df.to_csv(f'output_{today}_data.csv', index=False, encoding='utf-8')

    logging.info(f"已成功將數據寫入 'output_{today}_data.csv' 檔案。")

    # 將資料寫入 XLSX 檔案
    df.to_excel(f'output_{today}_data.xlsx', index=False)

    print(f"已成功將數據寫入 'output_{today}_data.xlsx' 檔案。")

    # Git 操作
    repo_dir = 'D:\Codeing\dev'  # 本地 Git 倉庫路徑
    os.chdir(repo_dir)

    # 添加更改
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Automated commit message'])
    subprocess.run(['git', 'push', 'origin', 'master'])  # 替換 'main' 為您的分支名稱

else:
    logging.error(f"請求失敗，狀態碼：{response.status_code}")
