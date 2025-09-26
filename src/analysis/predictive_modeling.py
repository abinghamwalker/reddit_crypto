# src/analysis/predictive_modeling.py

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

# --- Configuration ---
try:
    from src import config
except ImportError:
    config = None

# --- Main Modeling Function ---
def run_predictive_model(data_path, crypto, price_horizon_h, sentiment_window_h, lag_h, output_dir):
    """
    Engineers features, trains a predictive model, and evaluates its performance.

    This function builds a logistic regression model to predict whether the price
    of a crypto will go up or down over a future horizon, based on sentiment and
    technical indicators. It uses TimeSeriesSplit for robust cross-validation.

    Args:
        data_path (str): Path to the master data Parquet file.
        crypto (str): The crypto to model ('btc' or 'eth').
        price_horizon_h (int): The future window for the price prediction (target).
        sentiment_window_h (int): The rolling window for the sentiment feature.
        lag_h (int): The lag for the sentiment feature.
        output_dir (str): Directory to save evaluation results.
    """
    print(f"\n=======================================================================")
    print(f"      RUNNING PREDICTIVE MODEL FOR {crypto.upper()}")
    print(f"      Target: Price direction in {price_horizon_h} hours")
    print(f"      Sentiment Feature: {sentiment_window_h}h rolling average, lagged by {lag_h}h")
    print(f"=======================================================================\n")

    df = pd.read_parquet(data_path)

    # --- 1. Feature Engineering ---
    print("Step 1: Engineering Features...")
    price_col = f'{crypto}_close'
    sentiment_col = f'{crypto}_sentiment_mean'

    # a. Sentiment Feature (based on our correlation analysis)
    df['sentiment_feature'] = df[sentiment_col].rolling(window=sentiment_window_h, min_periods=1).mean().shift(lag_h)

    # b. Technical Features (past returns and volatility)
    # Using a window that matches the sentiment window is a good heuristic
    df['past_return'] = df[price_col].pct_change(periods=sentiment_window_h)
    df['volatility'] = df[price_col].pct_change().rolling(window=sentiment_window_h).std()

    # c. Target Variable (will the price be up or down?)
    # 1 if price goes up, 0 if it goes down or stays the same
    df['target'] = (df[price_col].shift(-price_horizon_h) > df[price_col]).astype(int)
    
    # Prepare final DataFrame for modeling
    model_df = df[['sentiment_feature', 'past_return', 'volatility', 'target']].dropna()
    X = model_df[['sentiment_feature', 'past_return', 'volatility']]
    y = model_df['target']
    
    if len(model_df) < 200:
        print("Not enough data to build a model after feature engineering. Exiting.")
        return

    print(f"Model will be trained on {len(model_df)} data points.")

    # --- 2. Train and Evaluate with TimeSeriesSplit ---
    print("\nStep 2: Training and Evaluating with Forward-Chaining Cross-Validation...")
    tscv = TimeSeriesSplit(n_splits=5)
    
    accuracies, precisions, recalls, f1_scores = [], [], [], []
    
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        
        # --- THIS IS THE FIX ---
        # Use the correct train_index for y_train
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        # ------------------------

        # Scale features based ONLY on the training data
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = LogisticRegression(random_state=42, class_weight='balanced')
        model.fit(X_train_scaled, y_train) # This will now work
        y_pred = model.predict(X_test_scaled)

        accuracies.append(accuracy_score(y_test, y_pred))
        precisions.append(precision_score(y_test, y_pred, zero_division=0))
        recalls.append(recall_score(y_test, y_pred, zero_division=0))
        f1_scores.append(f1_score(y_test, y_pred, zero_division=0))
        
    # --- 3. Report Results ---
    print("\nStep 3: Aggregating and Reporting Results...")
    
    results = {
        "Crypto": crypto.upper(),
        "Avg Accuracy": f"{np.mean(accuracies):.3f}",
        "Avg Precision": f"{np.mean(precisions):.3f}",
        "Avg Recall": f"{np.mean(recalls):.3f}",
        "Avg F1-Score": f"{np.mean(f1_scores):.3f}",
        "Baseline (Guessing 'Up')": f"{y.mean():.3f}"
    }
    
    # --- 4. Interpret Model Coefficients ---
    # To get a stable interpretation, we train one final model on the whole dataset
    final_scaler = StandardScaler()
    X_scaled = final_scaler.fit_transform(X)
    final_model = LogisticRegression(random_state=42, class_weight='balanced').fit(X_scaled, y)
    
    coefficients = pd.DataFrame(
        final_model.coef_[0],
        index=X.columns,
        columns=['Coefficient']
    ).sort_values(by='Coefficient', ascending=False)
    
    # Save and print results
    os.makedirs(output_dir, exist_ok=True)
    results_df = pd.DataFrame([results])
    results_path = os.path.join(output_dir, f"prediction_results_{crypto}.csv")
    results_df.to_csv(results_path, index=False)
    
    coeffs_path = os.path.join(output_dir, f"coefficients_{crypto}.csv")
    coefficients.to_csv(coeffs_path)

    print("\n--- Cross-Validation Performance Metrics ---")
    print(results_df.to_string(index=False))

    print("\n--- Feature Importance (Model Coefficients) ---")
    print("A positive coefficient means the feature pushes the prediction towards 'Up'.")
    print("A negative coefficient means the feature pushes the prediction towards 'Down'.")
    print(coefficients)

    # --- 5. Save the Final Model and Scaler ---

    print("Saving final model artifact...")
    model_artifact = {'model': final_model, 'scaler': final_scaler}
    artifact_path = os.path.join(output_dir, f"model_artifact_{crypto}.joblib")
    joblib.dump(model_artifact, artifact_path)
    print(f"Model artifact saved to '{artifact_path}'")

# --- Script Execution ---
if __name__ == "__main__":
    if config:
        # --- Run the model for BTC using its best (contrarian) parameters ---
        run_predictive_model(
            data_path=config.MASTER_DATA_PATH,
            crypto='btc',
            price_horizon_h=168,
            sentiment_window_h=168,
            lag_h=12,
            output_dir=config.RESULTS_DIR
        )

        # --- Run the model for ETH using its best positive correlation parameters ---
        run_predictive_model(
            data_path=config.MASTER_DATA_PATH,
            crypto='eth',
            price_horizon_h=168,
            sentiment_window_h=168,
            lag_h=12,
            output_dir=config.RESULTS_DIR
        )
        
        # --- Run the model for ETH using its best negative correlation parameters ---
        run_predictive_model(
            data_path=config.MASTER_DATA_PATH,
            crypto='eth',
            price_horizon_h=24,
            sentiment_window_h=24,
            lag_h=12,
            output_dir=config.RESULTS_DIR
        )