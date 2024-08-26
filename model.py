import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from pathlib import Path
from matplotlib import font_manager


def clean_filename(filename):
    # 移除或替換不允許的字符
    cleaned = re.sub(r'[<>:"/\\|?*\u200b]', '_', filename)
    # 移除首尾的空格和下劃線
    return cleaned.strip().strip('_')

# 指定字體路徑（你需要將路徑替換為實際字體檔案的路徑）
font_path = 'C:/Windows/Fonts/simsun.ttc'  

# 設定字體
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

'''
    random_forest: 預測機器的轉數、張力、喂紗量、喂油量(會因為機台不同和布料不同而有所差異  
    linear_regression: 預測機器的織造時間與瑕疵數(機台不同和布料不同大致差不多

'''


# Define the model
def random_forest(history,order_data,features, target):
    X = history[features]
    y = history[target] 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    results = []
    best_r2 = -float('inf')
    best_model = None
    best_n_estimators = None
    for i in range(1, 200, 20):
        
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=i, random_state=42))
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        results.append((i, r2))
        if r2 > best_r2:
            best_r2 = r2
            best_model = pipeline
            best_n_estimators = i
        print(f"n_estimators: {i}, R² Score: {r2:.4f}")
    print(f"\nBest model: n_estimators = {best_n_estimators}, R² Score = {best_r2:.4f}")

    predict_df = pd.DataFrame()
    predict_data = best_model.predict(order_data[features])
    predict_data = pd.DataFrame(predict_data, columns= [target])
    predict_df = pd.concat([predict_df, predict_data],  ignore_index=True)
    return predict_df

# def linear_regression(history,order_data,features,target):
#     predict_df = pd.DataFrame()
#     model = LinearRegression()
#     X = history[features]
#     Y = history[target[0]]
#     model.fit(X,Y)
#     predict_data = model.predict(order_data[features])
#     predict_data = pd.DataFrame(predict_data, columns=target)
#     predict_df = pd.concat([predict_df, predict_data],  ignore_index=True)
#     return predict_df