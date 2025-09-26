# Crypto Price Movement vs. Reddit Sentiment Analysis

This project investigates the relationship between cryptocurrency price movements and the sentiment of discussions on Reddit. Using a custom data pipeline, this analysis scrapes, cleans, and processes Reddit posts to generate sentiment scores, which are then correlated with market data to build and evaluate predictive models. The goal is to determine if social media sentiment can be transformed into actionable insights for the cryptocurrency market.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Key Findings & Conclusion](#key-findings--conclusion)
3.  [Data & Methodology](#data--methodology)
    - [Coins Selected](#coins-selected)
    - [Data Sources](#data-sources)
    - [Pipeline Stages](#pipeline-stages)
4.  [Project Structure](#project-structure)
5.  [Setup and Execution](#setup-and-execution)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Running the Pipeline](#running-the-pipeline)
6.  [Future Work & Limitations](#future-work--limitations)

## Project Overview

The core hypothesis of this project is that the collective sentiment of retail investors, as expressed on public forums like Reddit, contains a predictive signal for future cryptocurrency price movements. The project employs Natural Language Processing (NLP) with the VADER sentiment model to quantify discussion sentiment and uses a systematic, parameter-driven approach to discover and validate correlations.

The experimental framework is designed for flexibility, allowing for easy configuration of:

- **Coins:** The list of cryptocurrencies to analyze can be easily expanded.
- **Time Intervals:** The market data frequency (e.g., hourly, daily) is a configurable parameter.
- **Scraping Parameters:** The subreddits, keywords, and post limits for data collection are centralized for easy modification.

This modular structure allows for rapid iteration and experimentation with different market conditions and assets.

## Key Findings & Conclusion

After executing the full data pipeline—from acquisition and cleaning to sentiment analysis and predictive modeling—the project arrived at a clear and powerful conclusion:

**For the period analyzed, Reddit sentiment acts as a statistically significant _contrarian indicator_ for both Bitcoin (BTC) and Ethereum (ETH), particularly at longer time horizons.**

This suggests that peak positive sentiment on Reddit often coincides with a local market top, preceding a price correction rather than indicating the start of a rally.

### Detailed Findings:

1.  **Bitcoin (BTC): A Strong Long-Term Contrarian Signal**

    - The strongest and most statistically significant relationship found was a **negative correlation (-0.168)** between a week of sustained positive sentiment and the price movement over the following week.
    - A predictive model built on this relationship confirmed that sentiment was by far the most important feature, with a massively negative coefficient **(-3.088)**.
    - **Conclusion:** High, sustained positive chatter about Bitcoin on Reddit is a strong predictor of a **price decrease** over the next week. This aligns with a classic "retail FOMO precedes a sell-off" market dynamic.

2.  **Ethereum (ETH): A More Nuanced Contrarian Signal**
    - Ethereum also exhibits contrarian behavior, but on a much **shorter, 24-hour timescale**. A build-up of positive sentiment over a day was a significant predictor of a price drop over the following day.
    - A predictive model for this short-term effect showed a small but genuine **predictive edge over the baseline**, with an accuracy of 52.2% vs 51.1%.
    - Unlike Bitcoin, ETH also showed a very weak positive correlation at long time horizons, but this signal was not strong enough to build a successful predictive model.

### Limitations and Future Scope

It is crucial to caveat these findings with the fact that they are based on a limited dataset. Due to the restrictions of the free Reddit API, this analysis was performed on **approximately 800 of the most recent relevant posts**, not a deep historical archive covering the full year of market data.

However, the infrastructure built for this project is robust and scalable. With access to a paid, high-volume Reddit API endpoint, this same pipeline could be used with minimal changes to ingest and process a much larger and more comprehensive dataset. Doing so would significantly increase the confidence in these findings and would be a valuable next step for this research.

## Data & Methodology

### Coins Selected

The analysis was initially focused on two key assets:

- **Bitcoin (BTC):** As the largest and most established cryptocurrency, it serves as a baseline for the overall market. Its price movements are influenced by a mix of retail, institutional, and macroeconomic factors.
- **Ethereum (ETH):** As the leading smart contract platform, its sentiment is often tied more to ecosystem developments (DeFi, NFTs, upgrades) and can exhibit different dynamics than Bitcoin.

### Data Sources

- **Market Data:** Hourly OHLCV (Open, High, Low, Close, Volume) data was sourced from the Yahoo Finance API via the `yfinance` library.
- **Sentiment Data:** Posts were scraped from relevant subreddits (r/CryptoCurrency, r/Bitcoin, r/ethereum) using the official Reddit API via the `praw` library.

### Pipeline Stages

The project is orchestrated by `main.py` and is divided into distinct, runnable stages:

1.  **Acquire:** Fetches raw market and Reddit data and saves it to `data/raw/`.
2.  **Clean:** Applies validation rules and filters to the raw data, saving the cleaned versions to `data/processed/`.
3.  **Process:** Calculates sentiment scores and unifies the cleaned datasets into a single `master_data.parquet` file.
4.  **Analyze:** Performs the correlation parameter sweep to identify the strongest signals.
5.  **Predict:** Builds and evaluates predictive models based on the findings from the analysis stage.

## Project Structure

The project follows a standard data science structure to separate logic, data, and results.

```
reddit_crypto/
│
├── data/
│   ├── raw/          # Raw, unprocessed data
│   └── processed/    # Cleaned and unified data
│
├── notebooks/
│   ├── 01_acquisition_clean_investigate.ipynb
│   └── 02_correlation_analysis.ipynb
│
├── results/
│   ├── correlation_results.csv
│   ├── coefficients_btc.csv
│   ├── coefficients_eth.csv
│   ├── prediction_results_eth.csv
│   └── prediction_results_btc.csv
│
├── src/
│   ├── __init__.py
│   ├── config.py     # Central configuration file for all parameters
│   ├── acquisition/  # Scripts for fetching data
│   ├── processing/   # Scripts for cleaning, sentiment, and unifying data
│   └── analysis/     # Scripts for correlation and predictive modeling
│
├── .env              # (Not in Git) Stores secret API credentials
├── .gitignore
├── main.py           # Main runner script to orchestrate the pipeline
├── pyproject.toml    # Project metadata and dependencies
└── README.md         # This file
```

## Setup and Execution

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (a fast Python package installer)
- Homebrew (on macOS) for installing system dependencies like `cmake`.
- Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abinghamwalker/reddit_crypto.git
    cd reddit_crypto
    ```
2.  **Create a virtual environment:**
    ```bash
    uv venv
    ```
3.  **Install all dependencies:**
    ```bash
    uv pip install .
    ```

### Configuration

1.  **Reddit API Credentials:** You must have a Reddit account and create a "script" app [here](https://www.reddit.com/prefs/apps).
2.  **Create `.env` file:** In the project root, create a file named `.env` and add your credentials. Use the `.env.example` file as a template.
    ```text
    REDDIT_CLIENT_ID=your_client_id
    REDDIT_CLIENT_SECRET=your_client_secret
    REDDIT_USER_AGENT=AppName/0.1 by u/YourUsername
    REDDIT_USERNAME=YourUsername
    REDDIT_PASSWORD=YourPasswordOrAppPassword
    ```
3.  **Project Parameters:** All other parameters (tickers, subreddits, date ranges) can be modified in `src/config.py`.

### Running the Pipeline

The pipeline is controlled via `main.py`. You can run specific stages or all of them.

- **Run the entire pipeline from scratch:**
  ```bash
  uv run python main.py
  ```
- **Run only a specific stage (e.g., 'acquire'):**
  ```bash
  uv run python main.py acquire
  ```
- **Run multiple stages in order:**
  ```bash
  uv run python main.py clean process analyze
  ```

## Future Work & Limitations

As noted, the primary limitation is the amount of historical Reddit data available via the free API. Future work could involve:

- Integrating a paid, high-volume data source to perform a more robust historical analysis.
- Expanding the list of assets to include less liquid altcoins, which may be more susceptible to social media sentiment.
- Experimenting with more sophisticated NLP models (e.g., fine-tuning a transformer model like FinBERT) for sentiment analysis.
- Developing a simulated trading strategy based on the signals from the predictive models to backtest their financial viability.
