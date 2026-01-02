# 外部APIセットアップガイド

Phase 1 超強化版で使用する外部APIの登録方法を説明します。

## 必須API

### 1. FRED API（経済指標データ）★必須★

**重要度**: ★★★★★
**コスト**: 無料
**制限**: なし

#### 登録手順:

1. **FREDウェブサイトにアクセス**
   ```
   https://fred.stlouisfed.org/
   ```

2. **アカウント作成**
   - 右上の「My Account」をクリック
   - 「Request API Key」を選択
   - メールアドレスで無料登録

3. **APIキーを取得**
   - 即座に発行されます
   - 例: `abcd1234efgh5678ijkl9012mnop3456`

4. **`.env`ファイルに追加**
   ```env
   FRED_API_KEY=abcd1234efgh5678ijkl9012mnop3456
   ```

#### 取得できるデータ:

```python
# 米国経済指標
- FEDFUNDS: 米国政策金利
- UNRATE: 失業率
- CPIAUCSL: 消費者物価指数（CPI）
- GDP: GDP成長率
- DGS10: 10年国債利回り

# 日本経済指標
- IRLTLT01JPM156N: 日本長期金利
- JPNPROINDMISMEI: 製造業PMI
- LRHUTTTTJPM156S: 失業率
```

---

## オプションAPI（推奨）

### 2. Alpha Vantage API（株価・VIX指数）

**重要度**: ★★★★☆
**コスト**: 無料枠あり
**制限**: 500リクエスト/日（無料）、25リクエスト/日（株価）

#### 登録手順:

1. **Alpha Vantageウェブサイト**
   ```
   https://www.alphavantage.co/support/#api-key
   ```

2. **無料APIキーを取得**
   - メールアドレスを入力
   - 即座に発行

3. **`.env`ファイルに追加**
   ```env
   ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE
   ```

#### 取得できるデータ:

```python
- ^VIX: VIX指数（恐怖指数）
- ^GSPC: S&P 500
- ^DJI: ダウ平均
- 為替レートの検証用データ
```

---

### 3. News API（ニュースセンチメント）

**重要度**: ★★★☆☆（Phase 2以降で使用）
**コスト**: 無料枠あり
**制限**: 100リクエスト/日

#### 登録手順:

1. **News APIウェブサイト**
   ```
   https://newsapi.org/register
   ```

2. **無料アカウント作成**
   - メールアドレスで登録
   - APIキーが発行される

3. **`.env`ファイルに追加**
   ```env
   NEWS_API_KEY=YOUR_NEWS_API_KEY
   ```

#### 取得できるデータ:

```python
- 経済ニュースのヘッドライン
- FRB・日銀の発表
- センチメント分析用テキスト
```

---

## セットアップ確認

### 1. パッケージインストール

```bash
# FRED API用
pip install fredapi

# Alpha Vantage用（オプション）
pip install alpha-vantage

# News API用（オプション）
pip install newsapi-python
```

### 2. 動作確認スクリプト

```python
# test_apis.py
import os
from dotenv import load_dotenv

load_dotenv()

# FRED API確認
fred_key = os.getenv('FRED_API_KEY')
if fred_key and fred_key != 'your_fred_api_key_here':
    try:
        from fredapi import Fred
        fred = Fred(api_key=fred_key)
        data = fred.get_series('FEDFUNDS', limit=10)
        print(f"✓ FRED API: 正常動作 - {len(data)}件取得")
    except Exception as e:
        print(f"✗ FRED API: エラー - {e}")
else:
    print("✗ FRED API: 未設定")

# Alpha Vantage確認（オプション）
alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
if alpha_key and alpha_key != 'your_alpha_vantage_key_here':
    print("✓ Alpha Vantage API: 設定済み")
else:
    print("○ Alpha Vantage API: 未設定（オプション）")

# News API確認（オプション）
news_key = os.getenv('NEWS_API_KEY')
if news_key and news_key != 'your_news_api_key_here':
    print("✓ News API: 設定済み")
else:
    print("○ News API: 未設定（オプション）")
```

実行:
```bash
python test_apis.py
```

---

## Phase 1 超強化版を実データで実行

### 必須設定（FRED APIのみ）

FRED APIキーを設定したら:

```bash
python run_phase1_ultra.py
```

### 期待される改善:

```
デモデータ使用時:
- MAPE: 3.06%
- 方向性的中率: 75.84%

実データ使用時（期待値）:
- MAPE: 1.5% 以下
- 方向性的中率: 85% 以上
```

---

## よくある質問

### Q1: FRED APIキーが動作しない

**A**:
- キーにスペースが入っていないか確認
- `.env`ファイルの文法が正しいか確認
- Pythonを再起動してみる

### Q2: Alpha VantageのAPI制限に引っかかる

**A**:
- 無料版は25リクエスト/日の制限があります
- データをキャッシュして再利用する
- または有料プラン検討

### Q3: すべてのAPIを登録する必要がある？

**A**:
- **必須**: FRED API（経済指標）のみ
- **推奨**: Alpha Vantage（株価・VIX）
- **オプション**: News API（Phase 2以降）

最低限FREDだけでも十分に効果があります。

---

## トラブルシューティング

### エラー: "ModuleNotFoundError: No module named 'fredapi'"

```bash
pip install fredapi
```

### エラー: "Invalid API key"

- APIキーを再確認
- `.env`ファイルの該当行をコピー&ペースト
- ブラウザから直接コピーせずにテキストエディタを経由

### 環境変数が読み込まれない

```python
# Pythonスクリプトの最初で確認
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('FRED_API_KEY'))  # デバッグ出力
```

---

## 次のステップ

1. ✓ FRED APIキーを取得・設定
2. ✓ `pip install fredapi`
3. ✓ `python run_phase1_ultra.py` 実行
4. ✓ 精度向上を確認
5. → Phase 2のデータ収集に進む

設定完了後、モデルの精度が大幅に向上します！
