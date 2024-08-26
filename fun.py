import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import math


from pathlib import Path
from model import random_forest #,linear_regression
from schedule import schedule,plot_gantt_chart

current_path = Path(__file__).resolve().parent



# ---- 資料匯入 ----
def load_sample_data():
    history = pd.read_excel(
            f'{current_path}//sample//history.xlsx',
            engine='openpyxl')
    order_data = pd.read_excel(
            f'{current_path}//sample//order_data.xlsx',
            engine='openpyxl')
    machine_data = pd.read_excel(
            f'{current_path}//sample//machine_state.xlsx',
            engine='openpyxl')
    return history, order_data, machine_data


# --streamlit 資料匯入功能介面--
def load_data():
    with st.expander('#### 點我上傳資料集'):
        st.markdown('#### 請上傳織造紀錄資料集:')
        uploaded_history = st.file_uploader("", key='history')
        st.write('-----------------')
        st.markdown('#### 請上傳訂單資料:')
        uploaded_order = st.file_uploader("", key='order')
        st.write('-----------------')
        st.markdown('#### 請上傳機台資料:')
        uploaded_machine = st.file_uploader("", key='machine')
    return uploaded_history, uploaded_order, uploaded_machine
    


# --- 載入資料 ---
def upload_data(uploaded, fk):
    """_summary_

    Args:
        uploaded : streamlit.file_uploader
        fk (str): key word

    Returns:
        df_data: dataframe or None
    """
    if uploaded is not None:
        file_extension = Path(f'{uploaded.name}').suffix
        if file_extension == '.csv':
            sel_cols = st.columns(4)
            with sel_cols[0]:
                sp_mark = st.selectbox(
                    '分隔符號', [',', '空格', '/', ';', ':'], key=f'mark_{fk}')
            with sel_cols[1]:
                f_encode = st.selectbox(
                    "資料集編碼", ['utf-8', 'Big5', 'cp950'],
                    key=f'encode_{fk}')
            if sp_mark == '空格':
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=' ')
            else:
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=sp_mark)
        elif file_extension in ['.xlsx', '.xls']:
            if file_extension == '.xlsx':
                def_engine = 'openpyxl'
            else:
                def_engine = 'xlrd'
            df_data = pd.read_excel(
                uploaded, engine=def_engine)
        else:
            st.error(f'請輸入正確的檔案格式: csv, xlsx, xls 格式')
            df_data = None
    return df_data


   
        
        
   



 