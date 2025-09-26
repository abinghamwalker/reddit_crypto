# src/analysis/correlation_analysis.py

import os
import pandas as pd
from scipy.stats import pearsonr, spearmanr

# --- Configuration ---
# We will get paths from the central config file
try:
    from src import config
except ImportError:
    config = None

# --- Parameter Grids for the Sweep ---
# Define the time windows for future price changes (in hours)
PRICE_HORIZONS = [1, 4, 6, 12, 24, 72, 168] # 1h, 4h, 6h, 12h, 1d, 3d, 7d

# Define the rolling windows for sentiment aggregation (in hours)
SENTIMENT_WINDOWS = [1, 4, 6, 12, 24, 72, 168] # 1h, 4h, 6h, 12h, 1d, 3d, 7d

# Define the time lag between sentiment and price move (in hours)
LAGS = [0, 1, 2, 4, 6, 12] # 0 = sentiment at t vs price from t to t+H

# --- Main Function ---
def run_correlation_sweep(data_path, output_dir):
    """
    Performs a parameter sweep to find correlations between sentiment and price.

    This function systematically tests combinations of price horizons, sentiment
    aggregation windows, and time lags to identify the strongest correlations.

    Args:
        data_path (str): Path to the master data Parquet file.
        output_dir (str): Directory to save the correlation results CSV.

    Returns:
        None: Saves a file named `correlation_results.csv` to the output directory.
    """
    print("--- Starting Correlation Analysis Sweep ---")
    df = pd.read_parquet(data_path)
    all_results = []

    for crypto in ['btc', 'eth']:
        print(f"\n--- Analyzing {crypto.upper()} ---")
        price_col = f'{crypto}_close'
        sentiment_col = f'{crypto}_sentiment_mean'

        for horizon in PRICE_HORIZONS:
            df[f'future_return_{horizon}h'] = df[price_col].pct_change(periods=horizon).shift(-horizon)

            for window in SENTIMENT_WINDOWS:
                df[f'sentiment_{window}h_rolling'] = df[sentiment_col].rolling(window=window, min_periods=1).mean()

                for lag in LAGS:
                    sentiment_series = df[f'sentiment_{window}h_rolling'].shift(lag)
                    price_series = df[f'future_return_{horizon}h']
                    temp_df = pd.concat([sentiment_series, price_series], axis=1).dropna()

                    if len(temp_df) < 50: # Use a slightly higher threshold for robustness
                        continue

                    pearson_corr, pearson_p = pearsonr(temp_df[f'sentiment_{window}h_rolling'], temp_df[f'future_return_{horizon}h'])
                    spearman_corr, spearman_p = spearmanr(temp_df[f'sentiment_{window}h_rolling'], temp_df[f'future_return_{horizon}h'])

                    all_results.append({
                        'crypto': crypto,
                        'price_horizon_h': horizon,
                        'sentiment_window_h': window,
                        'lag_h': lag,
                        'pearson_corr': pearson_corr,
                        'pearson_p_value': pearson_p,
                        'spearman_corr': spearman_corr,
                        'spearman_p_value': spearman_p,
                        'n_observations': len(temp_df)
                    })

    print("\n--- Correlation Sweep Complete ---")
    results_df = pd.DataFrame(all_results)
    
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "correlation_results.csv")
    results_df.to_csv(results_path, index=False)
    print(f"Full results saved to '{results_path}'")

    significant_results = results_df[results_df['pearson_p_value'] < 0.05].copy()
    
    if not significant_results.empty:
        significant_results['abs_corr'] = significant_results['pearson_corr'].abs()
        print("\n--- Top 5 Most Significant Absolute Correlations ---")
        print(significant_results.sort_values(by='abs_corr', ascending=False).head())
    else:
        print("\n--- No statistically significant correlations found (p < 0.05) ---")

