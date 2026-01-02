# 📊 FX Data Collection Pipeline

**FX取引システム向け包括的データ収集パイプライン**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![データソース](https://img.shields.io/badge/Data%20Sources-3+-orange)](https://github.com/Akier-X/fx-data-pipeline)

---

## 📋 目次

- [概要](#-概要)
- [データソース](#-データソース)
- [機能](#-機能)
- [クイックスタート](#-クイックスタート)
- [使用方法](#-使用方法)
- [ディレクトリ構造](#-ディレクトリ構造)
- [API設定](#-api設定)
- [データフォーマット](#-データフォーマット)

---

## 🎯 概要

本パイプラインは、**FX取引システムの機械学習モデル**に必要な全データを自動収集・加工するシステムです。

複数のデータソースから価格データ、経済指標、ニュースセンチメントを取得し、ML-Readyな形式で出力します。

### 主な特徴

- ✅ **複数データソース統合** - Yahoo Finance, OANDA, FRED
- ✅ **10年分の長期データ** - 2,500日以上のヒストリカルデータ
- ✅ **時間単位から日次まで** - M1, M5, M15, H1, H4, D対応
- ✅ **経済指標自動取得** - 金利、CPI、失業率等
- ✅ **特徴量エンジニアリング** - 313+の特徴量を自動生成
- ✅ **ML-Ready形式** - pandas DataFrame, CSV出力

---

## 🌐 データソース

### 1. Yahoo Finance（メインソース）

**特徴**:
- ✅ **無料・APIキー不要**
- ✅ **3年以上の履歴データ**
- ✅ **日次粒度**
- ✅ **信頼性が高い**

**対応通貨ペア**:
- USD/JPY
- EUR/USD
- GBP/USD
- AUD/USD
- EUR/JPY
- その他主要通貨ペア

**ファイル**: `src/data_sources/yahoo_finance.py`

### 2. OANDA API（リアルタイム・高頻度）

**特徴**:
- ✅ **時間単位データ**（M1, M5, M15, H1, H4）
- ✅ **10年分のヒストリカルデータ**
- ✅ **リアルタイム価格取得**
- ⚠️ **APIキー必要**（無料デモアカウント利用可）

**対応時間足**:
- M1: 1分足
- M5: 5分足
- M15: 15分足
- H1: 1時間足
- H4: 4時間足
- D: 日足

**ファイル**: `src/data_sources/oanda_hourly.py`

### 3. FRED API（経済指標）

**特徴**:
- ✅ **米国・日本の経済指標**
- ✅ **金利、CPI、失業率、GDP等**
- ✅ **長期ヒストリカルデータ**
- ⚠️ **APIキー必要**（無料）

**取得指標**:
- 米国政策金利（FEDFUNDS）
- 日本政策金利（JPNIR）
- 米国失業率（UNRATE）
- 米国CPI（CPIAUCSL）
- 米国10年債利回り（DGS10）
- 日経平均（NIKKEI225）

**ファイル**: `src/data_sources/economic_indicators.py`

### 4. その他（拡張可能）

- **News API**: ニュース取得
- **Alpha Vantage**: センチメント分析
- **FinBERT**: テキスト分析

**ファイル**:
- `src/data_sources/news_collector.py`
- `src/data_sources/sentiment_analyzer.py`

---

## ⚙️ 機能

### データ収集スクリプト

```bash
# 日次データ収集（Yahoo Finance）
python src/data_sources/yahoo_finance.py

# 4時間足データ収集（OANDA）
python collect_4h_data.py

# 時間単位データ収集（OANDA）
python collect_hourly_data.py
```

### 包括的データ収集（Ultimate System）

```bash
# 10年分の包括的データ収集
python scripts/collect_ultimate_data.py

# Phase 2用データ収集
python scripts/collect_phase2_data.py

# 包括的データ収集（全ソース）
python scripts/collect_comprehensive_data.py
```

### 特徴量エンジニアリング

```bash
# 313+特徴量を生成
python scripts/generate_ultimate_ml.py
```

**生成される特徴量**:
- テクニカル指標（60種類）
  - 移動平均（SMA, EMA）
  - RSI, MACD, ボリンジャーバンド
  - ATR, ADX, ストキャスティクス
  - 一目均衡表（転換線、基準線、先行スパン）
- 価格変動指標
  - リターン、ボラティリティ
  - 高値・安値レンジ
- 経済指標
  - 金利差
  - CPI変化率
  - 失業率トレンド
- 時系列特徴
  - ラグ特徴量（1日前〜30日前）
  - 移動統計量（平均、標準偏差）

---

## 🚀 クイックスタート

### 1. インストール

```bash
git clone https://github.com/Akier-X/fx-data-pipeline.git
cd fx-data-pipeline
pip install -r requirements.txt
```

### 2. API設定

```bash
# .env.exampleをコピー
cp .env.example .env

# .envを編集してAPIキーを設定
nano .env
```

`.env`ファイル:

```bash
# OANDA API（時間単位データ用）
OANDA_ACCOUNT_ID=your_account_id
OANDA_ACCESS_TOKEN=your_access_token
OANDA_ENVIRONMENT=practice  # または 'live'

# FRED API（経済指標用）
FRED_API_KEY=your_fred_api_key

# オプション（拡張機能用）
NEWSAPI_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
```

### 3. データ収集実行

```bash
# Yahoo Financeから日次データ取得（APIキー不要）
python src/data_sources/yahoo_finance.py

# 経済指標取得（FREDキー必要）
python src/data_sources/economic_indicators.py

# OANDA 時間単位データ取得（OANDAキー必要）
python src/data_sources/oanda_hourly.py
```

### 4. 包括的データ収集（推奨）

```bash
# 10年分の全データを一括収集
python scripts/collect_ultimate_data.py
```

**出力**: `data/comprehensive/`ディレクトリに全データ保存

---

## 📖 使用方法

### 基本的なデータ収集

```python
from src.data_sources.yahoo_finance import collect_yahoo_finance_data

# USD/JPYの3年分データ取得
df = collect_yahoo_finance_data(
    symbol='USDJPY=X',
    period='3y',
    interval='1d'
)

print(df.head())
# Columns: Open, High, Low, Close, Volume
```

### 経済指標取得

```python
from src.data_sources.economic_indicators import collect_economic_indicators

# 米国政策金利取得
indicators = collect_economic_indicators(
    indicators=['FEDFUNDS', 'UNRATE', 'CPIAUCSL']
)

print(indicators)
```

### OANDA 時間単位データ

```python
from src.data_sources.oanda_hourly import collect_oanda_hourly

# USD/JPY 1時間足を1000本取得
df = collect_oanda_hourly(
    instrument='USD_JPY',
    granularity='H1',
    count=1000
)

print(df.columns)
# Columns: time, open, high, low, close, volume
```

### 特徴量エンジニアリング

```bash
# 価格データから313+特徴量を生成
python scripts/generate_ultimate_ml.py
```

**出力**: `data/comprehensive/ml_ready/USD_JPY_ml_features.csv`

---

## 📁 ディレクトリ構造

```
fx-data-pipeline/
├── README.md                              # このファイル
├── requirements.txt                       # Python依存関係
├── .env.example                           # 環境変数テンプレート
├── .gitignore                             # Git除外設定
│
├── collect_4h_data.py                     # 4時間足データ収集
├── collect_hourly_data.py                 # 時間単位データ収集
│
├── src/                                   # ソースコード
│   └── data_sources/                     # データソースモジュール
│       ├── __init__.py
│       ├── yahoo_finance.py              # Yahoo Finance（メイン）
│       ├── yahoo_finance_hourly.py       # Yahoo Finance時間足
│       ├── oanda_hourly.py               # OANDA時間単位
│       ├── economic_indicators.py        # FRED経済指標
│       ├── news_collector.py             # ニュース収集
│       └── sentiment_analyzer.py         # センチメント分析
│
├── scripts/                               # データ収集スクリプト
│   ├── collect_ultimate_data.py          # 包括的データ収集
│   ├── collect_phase2_data.py            # Phase 2データ収集
│   ├── collect_comprehensive_data.py     # 総合データ収集
│   └── generate_ultimate_ml.py           # 特徴量生成
│
├── docs/                                  # ドキュメント
│   ├── API_SETUP_GUIDE.md                # API設定ガイド
│   ├── OANDA_API_DATA_SOURCES.md         # OANDAデータソース
│   ├── PHASE2_DATA_COLLECTION.md         # Phase 2データ収集
│   └── SETUP_GUIDE.md                    # セットアップガイド
│
└── data/                                  # データ保存先（.gitignore）
    ├── comprehensive/                    # 包括的データ
    │   ├── price_data/                   # 価格データ
    │   ├── economic_indicators/          # 経済指標
    │   └── ml_ready/                     # ML-Ready特徴量
    └── phase2/                           # Phase 2データ
```

---

## 🔑 API設定

### OANDA API（無料デモアカウント）

1. [OANDA](https://www.oanda.com/)でデモアカウント作成
2. APIアクセストークン取得
3. `.env`に設定:
   ```
   OANDA_ACCOUNT_ID=101-xxx-xxxxxxx-xxx
   OANDA_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   OANDA_ENVIRONMENT=practice
   ```

**詳細**: [docs/API_SETUP_GUIDE.md](docs/API_SETUP_GUIDE.md)

### FRED API（無料）

1. [FRED](https://fred.stlouisfed.org/)でアカウント作成
2. APIキー取得
3. `.env`に設定:
   ```
   FRED_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Yahoo Finance

APIキー不要！すぐに使えます。

---

## 📊 データフォーマット

### 価格データ（CSV）

```csv
Date,Open,High,Low,Close,Volume
2024-01-01,145.23,145.67,145.01,145.45,125000
2024-01-02,145.45,146.12,145.30,146.00,130000
```

### 経済指標データ

```csv
Date,FEDFUNDS,UNRATE,CPIAUCSL
2024-01-01,5.33,3.7,307.051
2024-02-01,5.33,3.9,307.863
```

### ML-Ready特徴量

```csv
Date,Close,SMA_7,SMA_25,RSI,MACD,BB_upper,BB_lower,...
2024-01-01,145.45,145.2,144.8,55.3,0.12,146.5,144.1,...
```

**313+カラム**（価格、テクニカル指標、経済指標、ラグ特徴量）

---

## 🛠️ 技術スタック

- **pandas** - データ処理
- **yfinance** - Yahoo Financeクライアント
- **oandapyV20** - OANDA APIクライアント
- **fredapi** - FRED APIクライアント
- **numpy** - 数値計算
- **python-dotenv** - 環境変数管理

---

## 📚 ドキュメント

- [docs/API_SETUP_GUIDE.md](docs/API_SETUP_GUIDE.md) - API設定詳細
- [docs/OANDA_API_DATA_SOURCES.md](docs/OANDA_API_DATA_SOURCES.md) - OANDAデータ詳細
- [docs/PHASE2_DATA_COLLECTION.md](docs/PHASE2_DATA_COLLECTION.md) - Phase 2収集ガイド
- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - セットアップ詳細

---

## 🔗 関連リポジトリ

- [fx-adaptive-trading-system](https://github.com/Akier-X/fx-adaptive-trading-system) - 本番取引システム
- [fx-model-research](https://github.com/Akier-X/fx-model-research) - モデル研究
- [fx-web-dashboard](https://github.com/Akier-X/fx-web-dashboard) - リアルタイム監視

---

## 📝 ライセンス

MIT License

---

## 👤 作成者

**Akier-X**

- GitHub: [@Akier-X](https://github.com/Akier-X)
- Email: info.akierx@gmail.com

---

**💡 ヒント**: Yahoo Financeは無料で3年分のデータを取得できるため、研究・学習には最適です。OANDA APIは本番運用時のリアルタイムデータ取得に使用します。
