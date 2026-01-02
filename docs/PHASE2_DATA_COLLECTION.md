# Phase 2: 大規模データ収集タスク

## 目的

Phase 2で使用する大量のデータを事前に収集し、準備する。
このタスクは別のClaudeCodeインスタンスで並行実行することで、Phase 1のモデル強化と同時進行できる。

## 収集するデータ

### 1. 価格データ（複数年・複数通貨ペア）
- **期間**: 2015年～2024年（約10年分）
- **通貨ペア**:
  - USD_JPY（米ドル/円）
  - EUR_USD（ユーロ/米ドル）
  - GBP_USD（英ポンド/米ドル）
  - EUR_JPY（ユーロ/円）
  - GBP_JPY（英ポンド/円）
  - AUD_USD（豪ドル/米ドル）
  - USD_CHF（米ドル/スイスフラン）
- **時間足**: H1（1時間足）→ 日次に集約
- **取得方法**: Oanda API

### 2. 経済指標データ
- GDP成長率
- 失業率
- インフレ率（CPI）
- 政策金利
- 製造業PMI
- 消費者信頼感指数

### 3. ニュースデータ（オプション）
- 主要経済ニュース
- 中央銀行の発表
- 地政学リスク

### 4. 市場センチメントデータ
- VIX指数（恐怖指数）
- リスクオン/リスクオフ指標
- 通貨強弱インデックス

## 実装手順

### ステップ1: データ収集スクリプトの作成

以下のコマンドを実行してください：

```bash
# Phase 2データ収集システムを作成
python -c "
import sys
from pathlib import Path

# src/data_collection/ ディレクトリ作成
data_dir = Path('src/data_collection')
data_dir.mkdir(parents=True, exist_ok=True)

# __init__.py作成
(data_dir / '__init__.py').write_text('')

print('データ収集ディレクトリ作成完了')
"
```

### ステップ2: 価格データ収集の実行

```bash
python scripts/collect_phase2_data.py
```

## 期待される出力

```
data/
  phase2/
    price_data/
      USD_JPY_2015_2024_H1.csv
      EUR_USD_2015_2024_H1.csv
      GBP_USD_2015_2024_H1.csv
      ... (他の通貨ペア)
    economic_indicators/
      gdp_data.csv
      interest_rates.csv
      inflation_data.csv
      pmi_data.csv
    market_sentiment/
      vix_data.csv
      currency_strength.csv
    metadata.json
```

## データ収集スクリプト（scripts/collect_phase2_data.py）

このファイルを作成してください：

```python
"""
Phase 2: 大規模データ収集スクリプト

複数年・複数通貨ペアのデータを収集
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import time
import json

from src.api.oanda_client import OandaClient

class Phase2DataCollector:
    """Phase 2用の大規模データ収集"""

    def __init__(self):
        self.client = OandaClient()
        self.output_dir = Path("data/phase2")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 収集する通貨ペア
        self.instruments = [
            "USD_JPY",
            "EUR_USD",
            "GBP_USD",
            "EUR_JPY",
            "GBP_JPY",
            "AUD_USD",
            "USD_CHF"
        ]

        # 収集期間
        self.start_year = 2015
        self.end_year = 2024

    def collect_price_data(self):
        """価格データを収集"""
        logger.info("価格データ収集開始...")

        price_dir = self.output_dir / "price_data"
        price_dir.mkdir(exist_ok=True)

        for instrument in self.instruments:
            logger.info(f"\n{instrument} のデータ収集中...")

            try:
                # 年ごとに分けて取得（API制限対策）
                all_data = []

                for year in range(self.start_year, self.end_year + 1):
                    logger.info(f"  {year}年のデータ取得中...")

                    # 1年 = 365日 * 24時間
                    candles_per_year = 365 * 24

                    # 複数回に分けて取得
                    chunks = (candles_per_year // 5000) + 1

                    for chunk in range(chunks):
                        count = min(5000, candles_per_year - chunk * 5000)

                        if count <= 0:
                            break

                        data = self.client.get_historical_data(
                            instrument=instrument,
                            granularity="H1",
                            count=count
                        )

                        if not data.empty:
                            all_data.append(data)
                            logger.info(f"    チャンク {chunk+1}/{chunks}: {len(data)}件")

                        time.sleep(0.5)  # API制限

                # 結合
                if all_data:
                    combined = pd.concat(all_data).drop_duplicates().sort_index()

                    # 保存
                    output_file = price_dir / f"{instrument}_{self.start_year}_{self.end_year}_H1.csv"
                    combined.to_csv(output_file)

                    logger.info(f"{instrument} 完了: {len(combined)}件 -> {output_file}")
                else:
                    logger.warning(f"{instrument} データ取得失敗")

            except Exception as e:
                logger.error(f"{instrument} エラー: {e}")
                continue

        logger.info("\n価格データ収集完了!")

    def collect_economic_indicators(self):
        """経済指標データ収集（将来の拡張用）"""
        logger.info("\n経済指標データ収集...")

        econ_dir = self.output_dir / "economic_indicators"
        econ_dir.mkdir(exist_ok=True)

        # TODO: 経済指標APIとの連携
        # 現時点ではプレースホルダー

        logger.info("経済指標データ収集は将来実装予定")

    def create_metadata(self):
        """メタデータ作成"""
        metadata = {
            "collection_date": datetime.now().isoformat(),
            "instruments": self.instruments,
            "period": {
                "start_year": self.start_year,
                "end_year": self.end_year
            },
            "granularity": "H1",
            "status": "completed"
        }

        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"\nメタデータ保存: {metadata_file}")

    def run(self):
        """全データ収集を実行"""
        logger.info("="*70)
        logger.info("Phase 2: 大規模データ収集開始")
        logger.info("="*70 + "\n")

        # 1. 価格データ収集
        self.collect_price_data()

        # 2. 経済指標データ収集
        self.collect_economic_indicators()

        # 3. メタデータ作成
        self.create_metadata()

        logger.info("\n" + "="*70)
        logger.info("Phase 2 データ収集完了!")
        logger.info(f"保存先: {self.output_dir}")
        logger.info("="*70 + "\n")

def main():
    collector = Phase2DataCollector()
    collector.run()

if __name__ == "__main__":
    main()
```

## 使用方法

### 新しいClaudeCodeで実行する場合:

1. 新しいターミナルでClaudeCodeを開く
2. このファイルを指定して実行:

```
@PHASE2_DATA_COLLECTION.md 実行して
```

3. または直接コマンド実行:

```bash
# スクリプトファイルを作成してから
python scripts/collect_phase2_data.py
```

## 推定実行時間

- 価格データ収集: 30分～1時間
  - 7通貨ペア × 10年分 × API待機時間
- 経済指標データ: 将来実装
- 合計: 約1時間

## 注意事項

1. **API制限**: Oanda APIには取得制限があるため、適切な待機時間を設定
2. **エラーハンドリング**: ネットワークエラーやAPI認証エラーに対応
3. **データ検証**: 収集後、欠損値やデータの整合性をチェック
4. **並行実行**: Phase 1のモデル強化と同時に実行可能

## 次のステップ

データ収集完了後:
1. データの品質チェック
2. 欠損値の補完
3. 特徴量エンジニアリング
4. Phase 2本体（大規模学習）への投入
