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
