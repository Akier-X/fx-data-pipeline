# FX自動トレードシステム セットアップガイド

## 🚀 クイックスタート

### 1. 環境構築

```bash
# Python 3.11以上が必要です
python --version

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数ファイルの作成
cp .env.example .env
```

### 2. Oanda APIキーの取得

1. [Oanda](https://www.oanda.jp/)にログイン
2. アカウント設定 → API Access
3. Personal Access Token を生成
4. Account ID をメモ

### 3. 環境変数の設定

`.env` ファイルを編集:

```bash
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_ACCESS_TOKEN=your_token_here
OANDA_ENVIRONMENT=practice  # 最初はpracticeで！
```

### 4. 接続テスト

```bash
python examples/test_connection.py
```

成功すれば、アカウント情報と現在価格が表示されます。

## 📊 バックテストの実行

戦略の有効性を確認:

```bash
python examples/backtest_example.py
```

結果例:
```
バックテスト結果: MovingAverageCross
テスト期間: 83日 (2.8ヶ月)
初期資金: ¥10,000
最終資金: ¥10,450
総利益率: 4.50%
月次平均利益率: 1.61%
```

## 🤖 機械学習モデルの訓練

より高度な戦略:

```bash
python examples/train_ml_model.py
```

このスクリプトは:
- 過去5000本のローソク足データを取得
- Random Forestモデルを訓練
- テストデータでバックテスト実行
- モデルを `models/` に保存

## 🎯 実運用の開始

### ステップ1: ペーパートレード

実際のお金を使う前に、プラクティスアカウントでテスト:

```bash
# .envで OANDA_ENVIRONMENT=practice を確認
python src/main.py
```

ボットは1時間ごとに:
1. 市場データを取得
2. シグナルを判定
3. トレードを実行（またはログのみ）

### ステップ2: 本番環境

十分にテストした後:

1. `.env` を編集:
   ```bash
   OANDA_ENVIRONMENT=live
   ```

2. `src/main.py` の注文実行部分のコメントを外す:
   ```python
   # 実際に注文する場合は以下のコメントを外す
   response = self.client.place_market_order(...)
   ```

3. 慎重に実行:
   ```bash
   python src/main.py
   ```

## ☁️ クラウドへのデプロイ

### Render.com（推奨）

1. [Render.com](https://render.com/)にサインアップ
2. GitHubリポジトリを接続
3. New → Blueprint を選択
4. `render.yaml` を検出させる
5. 環境変数を設定
6. Deploy!

無料プランで24時間稼働可能です。

### Railway.app

1. [Railway.app](https://railway.app/)にサインアップ
2. New Project → Deploy from GitHub repo
3. 環境変数を追加
4. `python -m src.main` を実行コマンドに設定

月500時間の無料枠があります。

## 📈 戦略のカスタマイズ

### 移動平均線戦略のパラメータ調整

`src/strategies/moving_average_strategy.py`:

```python
strategy = MovingAverageCrossStrategy(
    fast_period=10,  # 短期移動平均
    slow_period=30,  # 長期移動平均
    use_rsi_filter=True,  # RSIフィルター
    use_macd_filter=True  # MACDフィルター
)
```

### 新しい戦略の追加

1. `src/strategies/` に新しいファイルを作成
2. `BaseStrategy` を継承
3. `generate_signals()` メソッドを実装

例:
```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # あなたの戦略ロジック
        pass
```

## 🎓 Claude Code & MCP の活用

### MCP (Model Context Protocol) サーバーの追加

MCPを使用してデータベースやAPIと統合:

```json
// .claude/mcp.json に追加
{
  "mcpServers": {
    "sqlite": {
      "command": "mcp-server-sqlite",
      "args": ["data/trades.db"]
    }
  }
}
```

### カスタムSkillsの作成

繰り返し実行するタスクをSkillsに:

```markdown
// .claude/skills/backtest.md
# Backtest Skill
Run backtests for all strategies and compare results
```

### Slash Commandsの追加

```markdown
// .claude/commands/optimize.md
Optimize strategy parameters using grid search
```

## ⚠️ リスク管理の重要性

### 必ず守るべきルール:

1. **少額からスタート**: 初期は1万円程度
2. **損切りは必須**: ストップロスを必ず設定
3. **リスクは2%以下**: 1トレードで資金の2%以上リスクを取らない
4. **レバレッジは控えめに**: 初期は5-10倍程度
5. **定期的な監視**: 完全放置はNG
6. **バックテスト必須**: 実運用前に必ず検証

### 推奨される目標利回り:

- **保守的**: 月利 2-5%
- **中程度**: 月利 5-10%
- **積極的**: 月利 10%以上

⚠️ **注意**: 月利10%以上は非常に高リスクです！

## 🔧 トラブルシューティング

### API接続エラー

```
Error: Unauthorized
```

→ `.env` のAPIキーを確認

### データ取得エラー

```
Error: Invalid instrument
```

→ 通貨ペアの形式を確認 (例: `USD_JPY`, `EUR_USD`)

### モデル訓練エラー

```
Error: Not enough data
```

→ より多くの履歴データを取得 (`count` を増やす)

## 📚 参考資料

- [Oanda API ドキュメント](https://developer.oanda.com/rest-live-v20/introduction/)
- [TA-Lib ドキュメント](https://technical-analysis-library-in-python.readthedocs.io/)
- [Claude Code ガイド](https://docs.anthropic.com/claude/docs)

## 🤝 サポート

質問やバグ報告は:
- GitHub Issues
- Claude Code コミュニティ

Happy Trading! 📈💰
