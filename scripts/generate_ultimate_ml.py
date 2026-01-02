"""
Ultimate ML Dataset Generator
最強のML学習用データセット生成
"""
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
import time
import json
from datetime import datetime
import os

def main():
    output_dir = Path("data/comprehensive")
    ultimate_dir = output_dir / "ultimate"
    ultimate_ml_dir = ultimate_dir / "ml_ultimate"
    ultimate_ml_dir.mkdir(parents=True, exist_ok=True)

    logger.info("="*70)
    logger.info("Ultimate ML Dataset 生成開始")
    logger.info("="*70)

    # 収集済みデータ読み込み
    cot_file = ultimate_dir / "cot_data/cot_positions.csv"
    cot_data = pd.read_csv(cot_file, index_col=0, parse_dates=True) if cot_file.exists() else pd.DataFrame()

    crypto_file = ultimate_dir / "crypto/crypto_data.csv"
    crypto_data = pd.read_csv(crypto_file, index_col=0, parse_dates=True) if crypto_file.exists() else pd.DataFrame()

    markets_file = ultimate_dir / "markets/global_markets.csv"
    market_data = pd.read_csv(markets_file, index_col=0, parse_dates=True) if markets_file.exists() else pd.DataFrame()

    trends_file = ultimate_dir / "google_trends/google_trends.csv"
    trends_data = pd.read_csv(trends_file, index_col=0, parse_dates=True) if trends_file.exists() else pd.DataFrame()

    logger.info(f"COT: {cot_data.shape}")
    logger.info(f"Crypto: {crypto_data.shape}")
    logger.info(f"Markets: {market_data.shape}")
    logger.info(f"Trends: {trends_data.shape}")

    # 時間足に拡張
    cot_hourly = cot_data.resample('h').ffill() if not cot_data.empty else pd.DataFrame()
    crypto_hourly = crypto_data.resample('h').ffill() if not crypto_data.empty else pd.DataFrame()
    market_hourly = market_data.resample('h').ffill() if not market_data.empty else pd.DataFrame()
    trends_hourly = trends_data.resample('h').ffill() if not trends_data.empty else pd.DataFrame()

    # クロス通貨特徴量生成
    logger.info("\nクロス通貨特徴量生成...")
    price_dir = output_dir / "price_data"
    all_prices = {}
    for pf in price_dir.glob("*_full_history.csv"):
        inst = pf.stem.replace("_full_history", "")
        df = pd.read_csv(pf, index_col="time", parse_dates=True)
        df.index = df.index.tz_localize(None)
        all_prices[inst] = df["close"]

    prices_df = pd.DataFrame(all_prices)
    returns = prices_df.pct_change()

    cross_features = pd.DataFrame(index=prices_df.index)
    for window in [24, 72, 168]:
        pairs = [("USD_JPY", "EUR_USD"), ("USD_JPY", "GBP_USD"), ("EUR_USD", "GBP_USD")]
        for p1, p2 in pairs:
            if p1 in returns.columns and p2 in returns.columns:
                cross_features[f"corr_{p1}_{p2}_{window}h"] = returns[p1].rolling(window).corr(returns[p2])

    # USD/JPY 強度
    usd_rets = [returns[p] for p in ["USD_JPY", "USD_CHF", "USD_CAD"] if p in returns.columns]
    if usd_rets:
        cross_features["usd_strength"] = pd.concat(usd_rets, axis=1).mean(axis=1).rolling(24).mean()

    jpy_rets = [-returns[p] for p in ["USD_JPY", "EUR_JPY", "GBP_JPY"] if p in returns.columns]
    if jpy_rets:
        cross_features["jpy_strength"] = pd.concat(jpy_rets, axis=1).mean(axis=1).rolling(24).mean()

    logger.info(f"クロス通貨特徴量: {len(cross_features.columns)}")

    # 各通貨ペアのML Dataset生成
    ml_dir = output_dir / "ml_ready"

    for ml_file in sorted(ml_dir.glob("*_ml_dataset.csv")):
        instrument = ml_file.stem.replace("_ml_dataset", "")
        logger.info(f"\n{instrument} の Ultimate Dataset 生成中...")

        df = pd.read_csv(ml_file, index_col="time", parse_dates=True)
        df.index = df.index.tz_localize(None)

        # 時間特徴量
        df["hour"] = df.index.hour
        df["day_of_week"] = df.index.dayofweek
        df["month"] = df.index.month
        df["quarter"] = df.index.quarter
        df["hour_sin"] = np.sin(2 * np.pi * df.index.hour / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df.index.hour / 24)
        df["day_sin"] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        df["day_cos"] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        df["month_sin"] = np.sin(2 * np.pi * df.index.month / 12)
        df["month_cos"] = np.cos(2 * np.pi * df.index.month / 12)
        df["is_tokyo_session"] = ((df.index.hour >= 0) & (df.index.hour < 9)).astype(int)
        df["is_london_session"] = ((df.index.hour >= 8) & (df.index.hour < 17)).astype(int)
        df["is_ny_session"] = ((df.index.hour >= 13) & (df.index.hour < 22)).astype(int)
        df["is_month_end"] = (df.index.day >= 28).astype(int)
        df["is_friday"] = (df.index.dayofweek == 4).astype(int)
        df["is_monday"] = (df.index.dayofweek == 0).astype(int)

        # ラグ特徴量
        for lag in [1, 2, 3, 4, 6, 8, 12, 24, 48, 72, 96, 120, 168]:
            df[f"lag_close_{lag}h"] = df["close"].shift(lag)
            df[f"lag_return_{lag}h"] = df["close"].pct_change(lag)

        # 追加ローリング統計量
        for w in [10, 30, 50, 100, 200]:
            df[f"sma_{w}_ext"] = df["close"].rolling(w).mean()
            df[f"ema_{w}_ext"] = df["close"].ewm(span=w).mean()
            df[f"std_{w}_ext"] = df["close"].rolling(w).std()
            df[f"range_{w}_ext"] = df["high"].rolling(w).max() - df["low"].rolling(w).min()
            df[f"skew_{w}"] = df["close"].pct_change().rolling(w).skew()
            df[f"kurtosis_{w}"] = df["close"].pct_change().rolling(w).kurt()
            df[f"zscore_{w}"] = (df["close"] - df[f"sma_{w}_ext"]) / (df[f"std_{w}_ext"] + 1e-10)

        # MACD拡張
        for fast, slow in [(5, 10), (12, 26), (19, 39)]:
            ema_fast = df["close"].ewm(span=fast).mean()
            ema_slow = df["close"].ewm(span=slow).mean()
            df[f"macd_{fast}_{slow}"] = ema_fast - ema_slow
            df[f"macd_signal_{fast}_{slow}"] = df[f"macd_{fast}_{slow}"].ewm(span=9).mean()

        # ボリンジャーバンド
        for w in [10, 20, 50]:
            sma = df["close"].rolling(w).mean()
            std = df["close"].rolling(w).std()
            df[f"bb_upper_{w}"] = sma + 2 * std
            df[f"bb_lower_{w}"] = sma - 2 * std
            df[f"bb_width_{w}"] = (df[f"bb_upper_{w}"] - df[f"bb_lower_{w}"]) / (sma + 1e-10)
            df[f"bb_pos_{w}"] = (df["close"] - df[f"bb_lower_{w}"]) / (df[f"bb_upper_{w}"] - df[f"bb_lower_{w}"] + 1e-10)

        # 追加RSI
        for period in [5, 7, 9, 21, 28]:
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            df[f"rsi_{period}_ext"] = 100 - (100 / (1 + gain / (loss + 1e-10)))

        # ストキャスティクス
        for period in [5, 9, 14, 21]:
            low_min = df["low"].rolling(period).min()
            high_max = df["high"].rolling(period).max()
            df[f"stoch_k_{period}"] = 100 * (df["close"] - low_min) / (high_max - low_min + 1e-10)
            df[f"stoch_d_{period}"] = df[f"stoch_k_{period}"].rolling(3).mean()

        # Williams %R
        for period in [7, 14, 21]:
            high_max = df["high"].rolling(period).max()
            low_min = df["low"].rolling(period).min()
            df[f"williams_r_{period}"] = -100 * (high_max - df["close"]) / (high_max - low_min + 1e-10)

        # CCI
        for period in [10, 14, 20]:
            tp = (df["high"] + df["low"] + df["close"]) / 3
            sma_tp = tp.rolling(period).mean()
            mad = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
            df[f"cci_{period}"] = (tp - sma_tp) / (0.015 * mad + 1e-10)

        # ATR拡張
        for period in [7, 14, 21]:
            high_low = df["high"] - df["low"]
            high_close = abs(df["high"] - df["close"].shift(1))
            low_close = abs(df["low"] - df["close"].shift(1))
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df[f"atr_{period}_ext"] = tr.rolling(period).mean()
            df[f"atr_pct_{period}"] = df[f"atr_{period}_ext"] / df["close"]

        # ADX
        plus_dm = df["high"].diff()
        minus_dm = df["low"].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr = pd.concat([
            df["high"] - df["low"],
            abs(df["high"] - df["close"].shift(1)),
            abs(df["low"] - df["close"].shift(1))
        ], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        plus_di = 100 * (plus_dm.rolling(14).mean() / (atr + 1e-10))
        minus_di = 100 * (abs(minus_dm).rolling(14).mean() / (atr + 1e-10))
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        df["adx"] = dx.rolling(14).mean()
        df["plus_di"] = plus_di
        df["minus_di"] = minus_di
        df["di_diff"] = plus_di - minus_di

        # OBV
        obv = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
        df["obv"] = obv
        df["obv_sma_20"] = obv.rolling(20).mean()
        df["obv_momentum"] = obv - obv.shift(20)

        # MFI (Money Flow Index)
        tp = (df["high"] + df["low"] + df["close"]) / 3
        mf = tp * df["volume"]
        pos_mf = mf.where(tp > tp.shift(1), 0).rolling(14).sum()
        neg_mf = mf.where(tp < tp.shift(1), 0).rolling(14).sum()
        df["mfi"] = 100 - (100 / (1 + pos_mf / (neg_mf + 1e-10)))

        # クロス通貨特徴量
        df = df.join(cross_features, how="left", rsuffix="_cross")

        # 追加市場データ
        if not market_hourly.empty:
            df = df.join(market_hourly, how="left", rsuffix="_mkt")

        # 暗号通貨データ
        if not crypto_hourly.empty:
            df = df.join(crypto_hourly, how="left", rsuffix="_crypto")

        # COTデータ
        if not cot_hourly.empty:
            df = df.join(cot_hourly, how="left", rsuffix="_cot")

        # Google Trends
        if not trends_hourly.empty:
            df = df.join(trends_hourly, how="left", rsuffix="_trends")

        # 欠損値・無限値処理
        df = df.replace([np.inf, -np.inf], np.nan).ffill().bfill()

        # 保存
        output_file = ultimate_ml_dir / f"{instrument}_ultimate.csv"
        df.to_csv(output_file)
        logger.info(f"  保存: {df.shape}")

    # 統計表示
    sample = pd.read_csv(ultimate_ml_dir / "USD_JPY_ultimate.csv", index_col=0, nrows=10)
    total_size = sum(os.path.getsize(f) for f in ultimate_ml_dir.glob("*.csv"))

    logger.info("\n" + "="*70)
    logger.info("Ultimate ML Dataset 完成!")
    logger.info("="*70)
    logger.info(f"特徴量数: {len(sample.columns)}")
    logger.info(f"合計サイズ: {total_size / 1024 / 1024:.1f} MB")

    # 特徴量一覧保存
    with open(ultimate_ml_dir / "feature_list.txt", "w") as f:
        for i, col in enumerate(sample.columns, 1):
            f.write(f"{i}. {col}\n")

    logger.info(f"特徴量一覧: {ultimate_ml_dir / 'feature_list.txt'}")


if __name__ == "__main__":
    main()
