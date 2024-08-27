import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


'''
Random Forest: Predicts variable machine parameters (rotation, tension, yarn feed, oil feed)
Linear Regression: Estimates consistent outcomes (weaving time, defect count)
'''


# Define the model
def random_forest(history,order_data,features, target):
    # Split the data into training and testing sets
    X = history[features]
    y = history[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    best_r2 = -float('inf')
    best_model = None
    
    for i in range(1, 200,50):
        # Use the pipeline to scale the data and fit the model
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=i, random_state=42))
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        
        # Find the best model
        if r2 > best_r2:
            best_r2 = r2
            best_model = pipeline
    print(f"target:{target} best r2_score : {best_r2}")
    
    # Predict the target value
    predict_data = best_model.predict(order_data[features])
    predict_df = pd.DataFrame(predict_data, columns=[target])

    return predict_df

# Define the model
def linear_regression(history,order_data,features,target):
    # Split the data into training and testing sets
    X = history[features]
    y = history[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    
    # Use the pipeline to scale the data and fit the model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', LinearRegression())
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"target:{target} r2_score : {r2}")
    
    # Predict the target value
    predict_data = pipeline.predict(order_data[features])
    predict_df = pd.DataFrame(predict_data, columns=[target])
    return predict_df



   
    