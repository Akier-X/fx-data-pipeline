# OANDA APIと外部APIのデータソース一覧

## 1. OANDA APIで取得できるデータ

### 現在実装済み：
- ✓ OHLCV（価格データ）- open, high, low, close, volume
- ✓ 複数時間足（M1, M5, M15, H1, H4, D1, W1, M1）
- ✓ アカウント情報
- ✓ ポジション情報

### 追加で取得可能（未実装）：

#### 1.1 価格の詳細情報
```python
# bid/ask スプレッド
- bid（売値）
- ask（買値）
- spread（スプレッド幅）
- liquidity（流動性）
```

**重要度**: ★★★★☆
スプレッドは市場のボラティリティと流動性を示す重要な指標

#### 1.2 ポジショニングデータ（オーダーブック）
```python
# OANDA独自のポジショニングデータ
endpoint: instruments.InstrumentsOrderBook
endpoint: instruments.InstrumentsPositionBook

- price_points（価格レベル）
- long_count_percent（ロングポジション比率）
- short_count_percent（ショートポジション比率）
```

**重要度**: ★★★★★
市場参加者のポジション傾向がわかる（逆張り指標として有効）

#### 1.3 複数通貨ペアの相関
```python
# 同時に複数通貨ペアを取得して相関分析
instruments = ["USD_JPY", "EUR_USD", "GBP_USD", "EUR_JPY", "AUD_USD"]

- 通貨強弱インデックス
- クロスペア相関
```

**重要度**: ★★★★☆
USD_JPYの予測にEUR_USDなどの動きを反映

#### 1.4 複数時間足の統合
```python
# マルチタイムフレーム分析
timeframes = ["M5", "M15", "H1", "H4", "D1"]

- M5: 短期トレンド
- H1: 中期トレンド
- D1: 長期トレンド
```

**重要度**: ★★★★★
異なる時間軸のトレンドを統合することで精度向上

---

## 2. 外部APIで取得できるデータ

### 2.1 経済指標（FRED API - Federal Reserve Economic Data）

**無料、登録必要**

```python
from fredapi import Fred

重要な経済指標:
- FEDFUNDS: 米国政策金利
- UNRATE: 米国失業率
- CPIAUCSL: 米国CPI（インフレ率）
- GDP: GDP成長率
- DGS10: 10年国債利回り
- DEXJPUS: USD/JPY為替レート（検証用）

日本の経済指標:
- JPNRATE: 日本政策金利
- JPNPROINDMISMEI: 日本製造業PMI
```

**重要度**: ★★★★★
為替レートは金利差で大きく動くため必須

### 2.2 VIX指数（恐怖指数）

**Alpha Vantage API - 無料枠あり**

```python
- VIX: S&P500ボラティリティ指数
- リスクオン/オフの判定
```

**重要度**: ★★★★☆
リスク回避局面でUSD_JPYは円高になる傾向

### 2.3 商品価格

**Alpha Vantage / Yahoo Finance**

```python
- 金（GOLD）: リスク回避資産
- 原油（WTI）: インフレ指標
- 米国債10年（TNX）: 金利動向
```

**重要度**: ★★★☆☆
補助的な指標として有効

### 2.4 ニュースセンチメント

**NewsAPI - 無料枠あり**

```python
- 経済ニュースのキーワード抽出
- センチメント分析（ポジティブ/ネガティブ）
- FRB・日銀の発表
```

**重要度**: ★★★☆☆
重要イベント前後の予測精度向上

### 2.5 株式市場指標

**Yahoo Finance - 無料**

```python
- ^DJI: ダウ平均
- ^GSPC: S&P 500
- ^N225: 日経平均
- ^VIX: VIX指数
```

**重要度**: ★★★★☆
株価とUSD_JPYは相関あり（リスクオン時は円安）

---

## 3. 推奨される実装優先順位

### 最優先（Phase 1 超強化版に実装）：

1. **複数時間足データ統合** ★★★★★
   - M5, H1, H4, D1 を同時に使用
   - 各時間足でテクニカル指標を計算

2. **OANDA ポジショニングデータ** ★★★★★
   - オーダーブック、ポジションブック
   - 市場参加者の偏りを利用

3. **bid/ask スプレッド情報** ★★★★☆
   - スプレッド幅の変化
   - 流動性の変化

4. **複数通貨ペア相関** ★★★★☆
   - EUR_USD, GBP_USD など主要ペア
   - 通貨強弱インデックス

5. **経済指標（FRED API）** ★★★★★
   - 米国・日本の政策金利
   - 失業率、CPI

### 次の優先順位（Phase 2で実装）：

6. **VIX指数** ★★★★☆
7. **株式市場指標** ★★★☆☆
8. **商品価格** ★★★☆☆
9. **ニュースセンチメント** ★★☆☆☆

---

## 4. 外部APIで取得できないが、OANDA APIで取得できる独自データ

### OANDA限定データ：

1. **ポジショニングデータ（Order Book / Position Book）**
   - OANDA顧客のポジション分布
   - 他のブローカーでは取得不可
   - 逆張り指標として非常に有効

2. **OANDA独自のヒストリカルスプレッド**
   - 過去のbid/askスプレッド履歴
   - 流動性の変化を分析可能

3. **OANDA顧客のオープンオーダー分布**
   - 指値注文が集中している価格帯
   - サポート/レジスタンスの判定に有効

---

## 5. 実装計画

### Phase 1 超強化版で追加：
```
✓ 複数時間足（M5, H1, H4, D1）
✓ bid/ask スプレッド
✓ ポジショニングデータ
✓ 複数通貨ペア（USD_JPY, EUR_USD, GBP_USD, EUR_JPY）
✓ FRED API経済指標（金利、失業率、CPI）
✓ より高度なモデル（XGBoost + LSTM）
```

### 推定特徴量数：
- 現在: 87個
- 超強化版: **200～300個**

---

## 6. API登録・設定が必要なもの

### FRED API（経済指標）
```bash
# 登録: https://fred.stlouisfed.org/docs/api/api_key.html
# 無料、即時発行

pip install fredapi

# .envに追加
FRED_API_KEY=your_api_key_here
```

### Alpha Vantage（株価・VIX）
```bash
# 登録: https://www.alphavantage.co/support/#api-key
# 無料枠: 500リクエスト/日

pip install alpha-vantage

# .envに追加
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### NewsAPI（ニュースセンチメント）- オプション
```bash
# 登録: https://newsapi.org/register
# 無料枠: 100リクエスト/日

pip install newsapi-python

# .envに追加
NEWS_API_KEY=your_api_key_here
```
