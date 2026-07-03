import pandas as pd
import numpy as np
import argparse
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import os

def process_data(data, lookback, horizon, num_companies, jump=1):
    X, Y = [], []
    for i in range(0, len(data) - lookback - horizon + 1, jump):
        X.append(data[i : (i + lookback)])
        Y.append(data[(i + lookback) : (i + lookback + horizon)])
    return np.array(X), np.array(Y)

def do_inverse_transform(output_result, num_companies, scl):
    original_matrix_format = []
    for result in output_result:
        # Reshape to (horizon, num_companies), inverse scale, and flatten
        reshaped = [result[x : x + num_companies] for x in range(0, len(result), num_companies)]
        original_matrix_format.append(scl.inverse_transform(reshaped))
    
    original_matrix_format = np.array(original_matrix_format)
    
    # Restore to flat representation
    for i in range(len(original_matrix_format)):
        output_result[i] = original_matrix_format[i].ravel()
        
    return output_result

def prediction_by_step_by_company(raw_model_output, num_companies):
    matrix_prediction = []
    for i in range(num_companies):
        matrix_prediction.append([
            [lista[j] for j in range(i, len(lista), num_companies)] 
            for lista in raw_model_output
        ])
    return np.array(matrix_prediction)

def target_by_company(raw_model_output, num_companies):
    matrix_target = [[] for _ in range(num_companies)]
    for output in raw_model_output:
        for i in range(num_companies):
            for j in range(0, len(output), num_companies):
                matrix_target[i].append(output[i + j])
    return np.array(matrix_target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--quick", action="store_true", help="Run a quick 3-epoch train for verification")
    args = parser.parse_args()
    
    epochs = 3 if args.quick else args.epochs
    
    feature_file = "full_feature_dataset.csv"
    pivot_file = "final_closing_prices_pivot.csv"
    
    if not os.path.exists(feature_file) or not os.path.exists(pivot_file):
        raise FileNotFoundError("Make sure to run download_data.py, pivot_data.py, and feature_engineering.py first.")
        
    print("Loading datasets...")
    full_features_df = pd.read_csv(feature_file, header=[0, 1], index_col=0, parse_dates=True)
    df_close = pd.read_csv(pivot_file, index_col=0, parse_dates=True)
    
    # Keep Closing prices only for the dates in full_features_df
    df_close_aligned = df_close.loc[full_features_df.index]
    
    # Split train and test (80% train, 20% test)
    # We do a sequential chronological split
    train_size = int(len(full_features_df) * 0.8)
    
    array_train = df_close_aligned.iloc[:train_size].to_numpy()
    array_test = df_close_aligned.iloc[train_size:].to_numpy()
    
    PCA_train = full_features_df.iloc[:train_size].to_numpy()
    PCA_test = full_features_df.iloc[train_size:].to_numpy()
    
    # Scale targets [0, 1]
    scl = MinMaxScaler()
    scale = MinMaxScaler()
    array_train_scaled = scl.fit_transform(array_train)
    array_test_scaled = scale.fit_transform(array_test)
    
    # Lookback and horizon configuration
    num_companies = df_close.shape[1]
    lookback = 252
    horizon = 22
    
    # Scale and apply PCA to feature inputs to reduce to num_companies components
    pcTrain_scl = MinMaxScaler()
    pcTest_scl = MinMaxScaler()
    pcaTrain = PCA(n_components=num_companies)
    pcaTest = PCA(n_components=num_companies)
    
    PCA_train_scaled = pcTrain_scl.fit_transform(PCA_train)
    PCA_train_pca = pcaTrain.fit_transform(PCA_train_scaled)
    
    PCA_test_scaled = pcTest_scl.fit_transform(PCA_test)
    PCA_test_pca = pcaTest.fit_transform(PCA_test_scaled)
    
    # Prepare sequence data
    print("Preparing sequence data for LSTM model...")
    # Chronological training setup
    X_PCA_train, _ = process_data(PCA_train_pca, lookback, horizon, num_companies)
    _, y_train_full = process_data(array_train_scaled, lookback, horizon, num_companies)
    y_train_full = np.array([list(x.ravel()) for x in y_train_full])
    
    # Testing setup (using jump=horizon to avoid overlap)
    X_test, _ = process_data(PCA_test_pca, lookback, horizon, num_companies, horizon)
    _, y_test_full = process_data(array_test_scaled, lookback, horizon, num_companies, horizon)
    y_test_full = np.array([list(a.ravel()) for a in y_test_full])
    
    # Split train into training and validation sets (80/20)
    X_train, X_validate, y_train, y_validate = train_test_split(
        X_PCA_train, y_train_full, test_size=0.2, random_state=1
    )
    
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_test shape: {y_test_full.shape}")
    
    # Build LSTM Network
    print("Building LSTM model...")
    model = Sequential()
    model.add(LSTM(800, input_shape=(lookback, num_companies), return_sequences=True))
    model.add(LSTM(600))
    model.add(Dense(horizon * num_companies, activation='relu'))
    model.add(Dense(horizon * num_companies, activation='sigmoid'))
    
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
    
    # Train model
    print(f"Training LSTM model for {epochs} epochs...")
    callbacks = [EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)]
    model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=256,
        validation_data=(X_validate, y_validate),
        callbacks=callbacks,
        verbose=1
    )
    
    # Predict on the entire dataset (train + test) to allow full-length backtesting
    print("Generating predictions for the entire dataset...")
    PCA_full_scaled = pcTrain_scl.transform(full_features_df.to_numpy())
    PCA_full_pca = pcaTrain.transform(PCA_full_scaled)
    
    array_full_scaled = scl.transform(df_close_aligned.to_numpy())
    
    # Process with jump=horizon to avoid overlap
    X_full, _ = process_data(PCA_full_pca, lookback, horizon, num_companies, horizon)
    _, y_full_scaled = process_data(array_full_scaled, lookback, horizon, num_companies, horizon)
    y_full_scaled = np.array([list(a.ravel()) for a in y_full_scaled])
    
    Xt_full = model.predict(X_full)
    
    # Reconstruct original Close prices
    Xt_unscaled = do_inverse_transform(Xt_full, num_companies, scl)
    y_unscaled = do_inverse_transform(y_full_scaled, num_companies, scl)
    
    predictions = prediction_by_step_by_company(Xt_unscaled, num_companies)
    actuals = target_by_company(y_unscaled, num_companies)
    
    # Reshape predictions and actuals to (days, 59)
    predictions_2d = predictions.reshape(num_companies, -1).T
    actuals_2d = actuals.T
    
    # Get the matching Dates index for the predictions
    # First sequence starts at 0, prediction starts at lookback (252)
    test_dates = df_close_aligned.index[lookback : lookback + len(predictions_2d)]
    
    pred_df = pd.DataFrame(data=predictions_2d, index=test_dates, columns=df_close.columns)
    actual_df = pd.DataFrame(data=actuals_2d, index=test_dates, columns=df_close.columns)
    
    pred_df.index.name = "Date"
    actual_df.index.name = "Date"
    
    pred_df.to_csv("PCA_Predicted_Prices1.csv")
    actual_df.to_csv("PCA_Actual_Prices1.csv")
    
    print(f"Saved LSTM predictions to 'PCA_Predicted_Prices1.csv' and actuals to 'PCA_Actual_Prices1.csv' with shape {pred_df.shape}")

if __name__ == "__main__":
    main()
