import pandas as pd
import glob


# Load the CSV file
Data= pd.read_csv('pair_data.csv')

print(Data.head())

print(Data.columns)

Data['arr_at'] = pd.to_datetime(Data['arr_at'])
Data['arr_at'] = Data['arr_at'].dt.strftime('%H:%M')
print(Data['arr_at'].head())

Data['Route'] = Data['Station_A'] + '-' + Data['Station_B']

print(Data['Route'].head())
from sklearn.preprocessing import LabelEncoder
# Initialize LabelEncoder
label_encoder = LabelEncoder()

# Fit and transform the 'Route' column to encode it numerically
Data['Route_encoded'] = label_encoder.fit_transform(Data['Route'])

# View the updated DataFrame
print(Data['Route_encoded'].head())



import numpy as np



Data['cos_hour'] = np.cos(2 * np.pi * Data['departure_time_of_day'] / 24)
Data['sin_hour'] = np.sin(2 * np.pi * Data['departure_time_of_day'] / 24)


Data = Data.drop(['Station_A', 'Station_B', 'Route','departure_time_of_day'], axis=1)



Data.dropna(inplace=True)
Data.reset_index(drop=True, inplace=True)  # Reset the DataFrame index
print(Data.shape)

Data['arr_at'] = pd.to_datetime(Data['arr_at'])

# Calculate minutes past midnight
Data['arr_at'] = Data['arr_at'].dt.hour * 60 + Data['arr_at'].dt.minute

# Treat 'arrival_minutes' as your target variable (y)



X = Data[['Route_encoded', 'cos_hour','sin_hour', 'day_of_week', 'month', 'departure_delay', 'arrival_delay']]

# Label (y)
y = Data['arr_at']



from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score


from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

knn_model = KNeighborsRegressor()
xgb_model = XGBRegressor()
rf_model = RandomForestRegressor()

# Train models
knn_model.fit(X_train, y_train)
xgb_model.fit(X_train, y_train)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred_knn = knn_model.predict(X_test)
y_pred_xgb = xgb_model.predict(X_test)
y_pred_rf = rf_model.predict(X_test)

# Calculate MSE and R-squared
mse_knn = mean_squared_error(y_test, y_pred_knn)
mse_xgb = mean_squared_error(y_test, y_pred_xgb)
mse_rf = mean_squared_error(y_test, y_pred_rf)

r2_knn = r2_score(y_test, y_pred_knn)
r2_xgb = r2_score(y_test, y_pred_xgb)
r2_rf = r2_score(y_test, y_pred_rf)

# Plot results
models = ['KNN', 'XGBoost', 'Random Forest']
mse_scores = [mse_knn, mse_xgb, mse_rf]
r2_scores = [r2_knn, r2_xgb, r2_rf]

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.bar(models, mse_scores, color=['blue', 'orange', 'green'])
plt.xlabel('Model')
plt.ylabel('Mean Squared Error (MSE)')
plt.title('MSE Comparison')

plt.subplot(1, 2, 2)
plt.bar(models, r2_scores, color=['blue', 'orange', 'green'])
plt.xlabel('Model')
plt.ylabel('R-squared (R²) Score')
plt.title('R² Score Comparison')

plt.tight_layout()
plt.show()
from sklearn.preprocessing import StandardScaler

Data['predicted_arrival_time'] = pd.NA
Data.loc[X_test.index, 'predicted_arrival_time'] = y_pred_rf

print(Data.head())

# Optionally, verify the length and alignment again if needed
print("Length of DataFrame:", len(Data))
print("Length of Test Set Predictions:", len(y_pred_rf))

X = Data[['Route_encoded', 'cos_hour', 'sin_hour', 'day_of_week', 'month', 'departure_delay', 'arrival_delay', 'predicted_arrival_time']]
y = Data['arr_at']  # Target variable: actual arrival time

# Handling missing values in 'predicted_arrival_time'
X['predicted_arrival_time'].fillna(X['predicted_arrival_time'].mean(), inplace=True)  # Replace NA with mean or median

# Normalize/Standardize your features if necessary
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.20, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)  # Training the model

"""
Data['total_predicted_time'] = Data.groupby('rid')['predicted_travel_time'].transform('sum')

# Train a new model
X_new = Data[['total_predicted_time', 'additional_features']]
y_new = Data['total_journey_time']  # Assuming you have this data

rf_model_total = RandomForestRegressor()

rf_model_total.fit(X_new, y_new)
"""