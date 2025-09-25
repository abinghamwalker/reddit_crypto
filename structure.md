## 📁 Project Structure

## Phase 0: Foundation & Data Acquisition

### 1. Define Project Scope

- Finalize list of cryptocurrencies to analyze (e.g., BTC, ETH).
  - BTC and ETH are chosen for initial tests for speed and efficiency of code
- Finalize list of subreddits to scrape (e.g., r/CryptoCurrency, r/Bitcoin).
  - Final list of subreddits to be used r/CryptoCurrency, r/Bitcoin, and r/ethereum.
- Define the historical date range (e.g., Jan 1, 2020 – Present).
  - I am going to focus on 1 years worth of data because the cryto market \
    evolves very quickly and patterns that have emerged a long time ago will not necessarily stand up now.

### 2. Acquire Market Data

- Download historical price data (Open, High, Low, Close, Volume) for the chosen cryptocurrencies and time frame.
- Clean and store it in a time-series format (e.g., CSV or database).

### 3. Scrape Reddit Data

- Use the Reddit API (via **PRAW** library in Python) to collect all posts and comments from the target subreddits within the defined date range.
- Store the raw data, making sure to include timestamp, id, subreddit, title, and body/comment_text.

---

## Phase 1: Sentiment Generation & Data Unification

### 4. Preprocess Raw Text

- Develop a Python script to clean the collected text: remove URLs, special characters, convert to lowercase, etc.

### 5. Generate Sentiment Scores

- Implement a baseline sentiment analysis model. Start with **VADER** for its speed and suitability for social media.
- Run every preprocessed post/comment through the model to generate a sentiment score (e.g., compound score from -1 to +1).
- Store these scores alongside the original text data.

### 6. Create a Unified Time-Series DataFrame

- Aggregate the individual sentiment scores into regular time intervals (e.g., hourly averages).
- Merge this aggregated sentiment data with the market price data based on the timestamp.
- This creates the **master DataFrame** for your experiments.

---

## Phase 2: Exploratory Correlation Analysis

### 7. Implement the Parameter Sweep (Grid Search)

As detailed in our previous conversation, write a script to systematically test combinations of:

- Price movement time frames (1h, 4h, 24h...).
- Sentiment aggregation windows (1h, 4h, 24h...).
- Time lags (sentiment at _t_ vs. price at _t+1, t+2..._).

For each combination:

- Calculate **Pearson** and **Spearman** correlation coefficients.
- Record their **p-values**.

### 8. Analyze Correlation Results

- Store the results of the sweep in a DataFrame.
- Identify the parameter sets with the highest statistically significant correlations.
- Use **heatmaps** and **tables** to visualize and report these findings.

---

## Phase 3: Predictive Modeling & Validation

### 9. Engineer Features for Modeling

- Based on the best parameters from Phase 2, create features for a predictive model.
  - Example: "12-hour rolling average sentiment, lagged by 4 hours."
- Add other technical features like past returns, volatility, etc.
- Define the target variable (e.g., binary classification: will the price be up or down in 24 hours?).

### 10. Train and Evaluate Predictive Model

- Choose a simple, interpretable model to start (e.g., Logistic Regression).
- Use **Forward-Chaining Cross-Validation (TimeSeriesSplit)** to train and test the model, respecting chronological order.
- Evaluate with appropriate metrics: Accuracy, F1-Score, Precision, Recall.

### 11. Interpret Model and Validate Findings

- Analyze the model’s coefficients to confirm whether sentiment is a significant predictor.
- Perform robustness checks on an **out-of-sample** test set.

---

## Phase 4: Iteration and Refinement

### 12. (If Necessary) Improve Sentiment Model

- If performance is poor and sentiment seems weak, try a more advanced model (e.g., Hugging Face pipeline).
- If still unsatisfactory, consider labeling data and fine-tuning your own transformer model.

### 13. Finalize and Report

- Summarize methodology, optimal parameters, predictive model performance, and final conclusions.
- Deliver insights on the **relationship between Reddit sentiment and crypto price movements**.

crypto-sentiment-correlation/

- .venv/ # virtual environment created by uv
- data/
  - raw/
  - processed/
  - master/
- src/
  - acquisition/
    - fetch_reddit.py
    - fetch_market.py
    - store_data.py
  - preprocessing/
    - clean_text.py
    - process_sentiment.py
  - sentiment/
    - vader_baseline.py
    - transformer_model.py
    - inference.py
- analysis/
  - correlation.py
  - visualization.py
- modeling/
  - feature_engineering.py
  - train_model.py
  - evaluate_model.py
- notebooks/
  - 00_data_acquisition.ipynb
  - 01_sentiment_generation.ipynb
  - 02_correlation_analysis.ipynb
  - 03_predictive_modeling.ipynb
- scripts/
  - run_ingest.sh
  - run_train.sh
- pyproject.toml # project metadata + dependencies (preferred with uv)
- uv.lock # lockfile managed by uv (auto-created after sync)
- README.md
