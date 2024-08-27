import numpy as np
import pandas as pd
import streamlit as st
import math
from pathlib import Path
from model import random_forest ,linear_regression

# Use current path
current_path = Path(__file__).resolve().parent

# Read a preset sample Excel file and return data sets
def load_sample_data():
    history = pd.read_excel(
            f"{current_path}//sample//history.xlsx",
            engine="openpyxl")
    order_data = pd.read_excel(
            f"{current_path}//sample//order_data.xlsx",
            engine="openpyxl")
    machine_data = pd.read_excel(
            f"{current_path}//sample//machine_state.xlsx",
            engine="openpyxl")
    return history, order_data, machine_data

# Provide a file upload interface and return the uploaded file object
def load_data():
    with st.expander("#### 點我上傳資料集"):
        st.markdown("#### 請上傳織造紀錄資料集:")
        uploaded_history = st.file_uploader("", key="history")
        st.write("-----------------")
        st.markdown("#### 請上傳訂單資料:")
        uploaded_order = st.file_uploader("", key="order")
        st.write("-----------------")
        st.markdown("#### 請上傳機台資料:")
        uploaded_machine = st.file_uploader("", key="machine")
    return uploaded_history, uploaded_order, uploaded_machine
    
# Process uploaded files and read data based on file type 
def upload_data(uploaded, fk):
    if uploaded is not None:
        file_extension = Path(f"{uploaded.name}").suffix
        if file_extension == ".csv":
            sel_cols = st.columns(4)
            with sel_cols[0]:
                sp_mark = st.selectbox(
                    "分隔符號", [",", "空格", "/", ";", ":"], key=f"mark_{fk}")
            with sel_cols[1]:
                f_encode = st.selectbox(
                    "資料集編碼", ["utf-8", "Big5", "cp950"],
                    key=f"encode_{fk}")
            if sp_mark == "空格":
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=" ")
            else:
                df_data = pd.read_csv(
                    uploaded, encoding=f_encode,
                    sep=sp_mark)
        elif file_extension in [".xlsx", ".xls"]:
            if file_extension == ".xlsx":
                def_engine = "openpyxl"
            else:
                def_engine = "xlrd"
            df_data = pd.read_excel(
                uploaded, engine=def_engine)
        else:
            st.error(f"請輸入正確的檔案格式: csv, xlsx, xls 格式")
            df_data = None
    return df_data

# Predict rotation speed
def predict_rotation(history, order_data):
    predict_df = random_forest(history,order_data, ["織造數量(米)","布重(克/平方米)","丹尼數(D)","針數(針/吋)","棉%"], "針筒轉數(圈)")
    predict_df = predict_df.round(0)
    order_data = pd.concat([order_data,predict_df],axis=1)
    return  order_data

# Predict yarn tension
def predict_tension(history, order_data):
    predict_df = random_forest(history,order_data, ["織造數量(米)","布重(克/平方米)","丹尼數(D)","針數(針/吋)","棉%"], "紗線張力(cN)")
    predict_df = predict_df.round(1)
    order_data = pd.concat([order_data,predict_df],axis=1)
    return  order_data

# Predict yarn feed rate
def predict_feedyarn(history, order_data):
    predict_df = random_forest(history,order_data, ["布重(克/平方米)","丹尼數(D)","針數(針/吋)","聚酯纖維%","棉%"], "喂紗率(米/每分鐘​)")
    predict_df = predict_df.round(0)
    order_data = pd.concat([order_data,predict_df],axis=1)
    return  order_data

# Predict oil feeding amount
def predict_feedoil(history, order_data):
    predict_df = random_forest(history,order_data, ["織造數量(米)","布重(克/平方米)","丹尼數(D)","聚酯纖維%","棉%"], "喂油量(毫升/小時)")
    predict_df = predict_df.round(1)
    order_data = pd.concat([order_data,predict_df],axis=1)
    return  order_data
    
# Predict weaving time
def predict_time(history,order_data):
    predict_df = linear_regression(history,order_data,["織造數量(米)","布重(克/平方米)","丹尼數(D)","針數(針/吋)"],"織造時間(小時)")
    predict_df["織造時間(天)"] = predict_df["織造時間(小時)"]/24
    predict_df["織造時間(天)"] = predict_df["織造時間(天)"].apply(math.ceil)
    order_data = pd.concat([order_data,predict_df],axis=1)
    return order_data

# Predict number of flaws
def predict_flaw(history,order_data):
    predict_df = linear_regression(history,order_data,["織造數量(米)","布重(克/平方米)", "丹尼數(D)", "針數(針/吋)","織造時間(小時)"],"瑕疵數")
    predict_df = np.ceil(predict_df)
    order_data = pd.concat([order_data, predict_df], axis=1)
    return order_data
    
# Show the schedule information  
def show_schedule(machine_assignments,predict_df):
    # Create a schedule information dataframe
    schedule_info = []
    for index, orders in enumerate(machine_assignments):
        for order in orders:
            schedule_info.append({
                "訂單編號": order["order_number"],
                "機台編號": index + 1,
                "幾日後開始生產": order["start_time"],
                "預計織造數量(米)": round(float(order["length"]), 0),
                "預估織造時間(小時)": round(float(order["duration_hour"]), 0),
                "預計瑕疵數": round(float(order["flaw"]), 0),
            })            
    schedule_info_df = pd.DataFrame(schedule_info)
    
    # Combine parameters and schedule results
    for schedule_index, schedule_data in schedule_info_df.iterrows():
        for predict_index, predict_data in predict_df.iterrows(): 
            if schedule_data["訂單編號"] == predict_data["訂單編號"]:
                schedule_info_df.loc[schedule_index, "針筒轉數(圈)"] = predict_data["針筒轉數(圈)"]
                schedule_info_df.loc[schedule_index, "紗線張力(cN)"] = predict_data["紗線張力(cN)"]
                schedule_info_df.loc[schedule_index, "喂紗率(米/每分鐘)"] = predict_data["喂紗率(米/每分鐘​)"]
                schedule_info_df.loc[schedule_index, "喂油量(毫升/小時)"] = predict_data["喂油量(毫升/小時)"]
                
    # Rearrange the columns       
    columns = ["訂單編號","機台編號","幾日後開始生產","預計織造數量(米)","針筒轉數(圈)","紗線張力(cN)","喂紗率(米/每分鐘)","喂油量(毫升/小時)","預估織造時間(小時)","預計瑕疵數"] 
    schedule_info_df = schedule_info_df.reindex(columns=columns)
    
    # Sort the schedule information by the start time
    schedule_info_df = schedule_info_df.sort_values(by=["幾日後開始生產"])
    
    Evaluate_efficiency(schedule_info_df)
    return schedule_info_df 

 # Compute the efficiency and flaw rate
def Evaluate_efficiency(schedule_info_df):
    # Calculate the total length, time, and flaw
    total_length = schedule_info_df["預計織造數量(米)"].sum()
    total_time = schedule_info_df["預估織造時間(小時)"].sum()
    total_flaw = schedule_info_df["預計瑕疵數"].sum()
    efficiency = float(total_length / total_time)
    flaw_rate = float(total_flaw / (total_length/1000))
    
    # Display the efficiency and flaw rate
    efficiency_text = f"<span style='color: green; font-size:24px'>優化後效率: {format(efficiency, '.2f')} 米/小時</span>"
    flaw_rate_text = f"<span style='color: green ; font-size:24px'>優化後瑕疵率 : {format(flaw_rate, '.2f')} 瑕疵數/千米</span>"
    st.markdown(efficiency_text, unsafe_allow_html=True)
    st.markdown(flaw_rate_text, unsafe_allow_html=True)
    return efficiency,flaw_rate
