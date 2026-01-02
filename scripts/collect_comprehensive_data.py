"""
大規模データ収集スクリプト

収集データ:
1. 価格データ（OANDA API - 10年分）
2. 経済指標（FRED API）
3. ニュース/センチメント（数値化）
4. VIX・市場センチメント指標
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
import time
import json
import requests
from typing import Dict, List, Optional
import os

from oandapyV20 import API
from oandapyV20.endpoints import instruments
from oandapyV20.exceptions import V20Error

from src.config import settings


class ComprehensiveDataCollector:
    """包括的データ収集システム"""

    def __init__(self):
        self.output_dir = Path("data/comprehensive")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # OANDA API
        self.oanda = API(
            access_token=settings.oanda_access_token,
            environment=settings.oanda_environment
        )

        # 通貨ペア
        self.instruments = [
            "USD_JPY", "EUR_USD", "GBP_USD", "EUR_JPY",
            "GBP_JPY", "AUD_USD", "USD_CHF", "NZD_USD",
            "USD_CAD", "AUD_JPY", "CHF_JPY", "EUR_GBP"
        ]

        # FRED API
        self.fred_api_key = os.getenv('FRED_API_KEY')

        logger.info("ComprehensiveDataCollector 初期化完了")

    # ===== 1. 価格データ収集（完全履歴） =====

    def collect_full_price_history(self, start_year: int = 2015, end_year: int = 2024):
        """
        完全な履歴価格データを収集
        日付範囲を指定して取得
        """
        logger.info("="*70)
        logger.info("1. 価格データ収集（完全履歴）")
        logger.info("="*70)

        price_dir = self.output_dir / "price_data"
        price_dir.mkdir(exist_ok=True)

        for instrument in self.instruments:
            logger.info(f"\n{instrument} のデータ収集中...")

            try:
                all_data = []

                # 月単位で取得（API制限対策）
                current_date = datetime(start_year, 1, 1)
                end_date = datetime(end_year, 12, 31)

                while current_date < end_date:
                    next_date = current_date + timedelta(days=180)  # 6ヶ月ずつ
                    if next_date > end_date:
                        next_date = end_date

                    logger.info(f"  {current_date.strftime('%Y-%m')} ~ {next_date.strftime('%Y-%m')}...")

                    try:
                        params = {
                            "granularity": "H1",
                            "from": current_date.strftime("%Y-%m-%dT00:00:00Z"),
                            "to": next_date.strftime("%Y-%m-%dT23:59:59Z"),
                            "price": "MBA"
                        }

                        endpoint = instruments.InstrumentsCandles(
                            instrument=instrument,
                            params=params
                        )
                        response = self.oanda.request(endpoint)

                        candles = response.get('candles', [])

                        for candle in candles:
                            if candle.get('complete', False):
                                mid = candle.get('mid', {})
                                bid = candle.get('bid', {})
                                ask = candle.get('ask', {})

                                all_data.append({
                                    'time': candle['time'],
                                    'open': float(mid.get('o', 0)),
                                    'high': float(mid.get('h', 0)),
                                    'low': float(mid.get('l', 0)),
                                    'close': float(mid.get('c', 0)),
                                    'volume': int(candle.get('volume', 0)),
                                    'bid_close': float(bid.get('c', 0)) if bid else 0,
                                    'ask_close': float(ask.get('c', 0)) if ask else 0,
                                })

                        logger.info(f"    取得: {len(candles)}件")

                    except V20Error as e:
                        logger.warning(f"    API エラー: {e}")

                    time.sleep(0.5)  # API制限
                    current_date = next_date

                # データフレーム化・保存
                if all_data:
                    df = pd.DataFrame(all_data)
                    df['time'] = pd.to_datetime(df['time'])
                    df = df.drop_duplicates(subset=['time']).sort_values('time')
                    df.set_index('time', inplace=True)

                    # スプレッド計算
                    df['spread'] = df['ask_close'] - df['bid_close']

                    output_file = price_dir / f"{instrument}_full_history.csv"
                    df.to_csv(output_file)

                    logger.info(f"{instrument} 完了: {len(df)}件 ({df.index.min()} ~ {df.index.max()})")

            except Exception as e:
                logger.error(f"{instrument} エラー: {e}")
                continue

        logger.info("\n価格データ収集完了!")

    # ===== 2. 経済指標データ収集（FRED API） =====

    def collect_economic_indicators(self, start_date: str = "2015-01-01"):
        """
        FRED APIから経済指標を収集
        """
        logger.info("\n" + "="*70)
        logger.info("2. 経済指標データ収集（FRED API）")
        logger.info("="*70)

        if not self.fred_api_key:
            logger.warning("FRED_API_KEY が設定されていません")
            return

        econ_dir = self.output_dir / "economic_indicators"
        econ_dir.mkdir(exist_ok=True)

        # 取得する指標リスト
        indicators = {
            # 米国
            'FEDFUNDS': 'us_fed_funds_rate',
            'UNRATE': 'us_unemployment',
            'CPIAUCSL': 'us_cpi',
            'GDP': 'us_gdp',
            'INDPRO': 'us_industrial_production',
            'UMCSENT': 'us_consumer_sentiment',
            'PAYEMS': 'us_nonfarm_payrolls',
            'DGS10': 'us_10y_treasury',
            'DGS2': 'us_2y_treasury',
            'VIXCLS': 'vix',

            # 日本
            'IRLTLT01JPM156N': 'jp_long_term_rate',
            'LRHUTTTTJPM156S': 'jp_unemployment',
            'JPNCPIALLMINMEI': 'jp_cpi',

            # ユーロ圏
            'ECBDFR': 'ecb_deposit_rate',
            'LRHUTTTTEZM156S': 'ez_unemployment',

            # 英国
            'BOERUKM': 'uk_bank_rate',
            'LRHUTTTTGBM156S': 'uk_unemployment',

            # グローバル
            'DCOILWTICO': 'wti_crude_oil',
            'GOLDAMGBD228NLBM': 'gold_price',
        }

        all_data = {}

        for series_id, name in indicators.items():
            logger.info(f"  {name} ({series_id}) 取得中...")

            try:
                url = f"https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': series_id,
                    'api_key': self.fred_api_key,
                    'file_type': 'json',
                    'observation_start': start_date,
                }

                response = requests.get(url, params=params)
                data = response.json()

                if 'observations' in data:
                    observations = data['observations']
                    series_data = []

                    for obs in observations:
                        try:
                            value = float(obs['value']) if obs['value'] != '.' else np.nan
                            series_data.append({
                                'date': obs['date'],
                                'value': value
                            })
                        except:
                            continue

                    if series_data:
                        df = pd.DataFrame(series_data)
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)
                        all_data[name] = df['value']
                        logger.info(f"    成功: {len(df)}件")

                time.sleep(0.3)  # API制限

            except Exception as e:
                logger.error(f"    エラー: {e}")
                continue

        # 統合データフレーム作成
        if all_data:
            combined = pd.DataFrame(all_data)
            combined = combined.sort_index()

            # 欠損値を前方補完
            combined = combined.ffill()

            # 追加特徴量
            if 'us_10y_treasury' in combined.columns and 'us_2y_treasury' in combined.columns:
                combined['yield_curve'] = combined['us_10y_treasury'] - combined['us_2y_treasury']

            if 'us_fed_funds_rate' in combined.columns and 'jp_long_term_rate' in combined.columns:
                combined['us_jp_rate_diff'] = combined['us_fed_funds_rate'] - combined['jp_long_term_rate']

            output_file = econ_dir / "all_indicators.csv"
            combined.to_csv(output_file)

            logger.info(f"\n経済指標データ保存: {output_file}")
            logger.info(f"  期間: {combined.index.min()} ~ {combined.index.max()}")
            logger.info(f"  指標数: {len(combined.columns)}")

    # ===== 3. ニュース/センチメントデータ =====

    def collect_sentiment_data(self):
        """
        ニュースセンチメントデータを収集・数値化

        Note: 無料APIの制限により、サンプルデータ生成も含む
        """
        logger.info("\n" + "="*70)
        logger.info("3. センチメント/VIXデータ収集")
        logger.info("="*70)

        sentiment_dir = self.output_dir / "sentiment"
        sentiment_dir.mkdir(exist_ok=True)

        # VIXデータはFREDから取得済み
        # 追加のセンチメント指標を生成

        logger.info("センチメント特徴量を価格データから生成...")

        price_dir = self.output_dir / "price_data"

        for csv_file in price_dir.glob("*.csv"):
            instrument = csv_file.stem.replace("_full_history", "")
            logger.info(f"  {instrument} のセンチメント特徴量生成中...")

            try:
                df = pd.read_csv(csv_file, index_col='time', parse_dates=True)

                # テクニカルベースのセンチメント指標
                sentiment_features = pd.DataFrame(index=df.index)

                # 1. ボラティリティ（恐怖指標）
                sentiment_features['volatility_20'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
                sentiment_features['volatility_60'] = df['close'].pct_change().rolling(60).std() * np.sqrt(252)

                # 2. トレンド強度（ADX的な指標）
                high_low = df['high'] - df['low']
                high_close = abs(df['high'] - df['close'].shift(1))
                low_close = abs(df['low'] - df['close'].shift(1))
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                sentiment_features['atr_14'] = true_range.rolling(14).mean()

                # 3. モメンタム
                sentiment_features['momentum_10'] = df['close'].pct_change(10)
                sentiment_features['momentum_20'] = df['close'].pct_change(20)

                # 4. RSI（過買い/過売り）
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                sentiment_features['rsi_14'] = 100 - (100 / (1 + rs))

                # 5. ボリューム変化率
                sentiment_features['volume_change'] = df['volume'].pct_change()
                sentiment_features['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

                # 6. 価格位置（過去N日間の中での位置）
                sentiment_features['price_position_20'] = (
                    (df['close'] - df['low'].rolling(20).min()) /
                    (df['high'].rolling(20).max() - df['low'].rolling(20).min())
                )

                # 7. ギャップ分析
                sentiment_features['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)

                # 8. スプレッド異常（流動性低下の兆候）
                if 'spread' in df.columns:
                    sentiment_features['spread_ma_ratio'] = df['spread'] / df['spread'].rolling(20).mean()

                # 保存
                output_file = sentiment_dir / f"{instrument}_sentiment.csv"
                sentiment_features.to_csv(output_file)

                logger.info(f"    完了: {len(sentiment_features.columns)}指標")

            except Exception as e:
                logger.error(f"    エラー: {e}")
                continue

        logger.info("\nセンチメント特徴量生成完了!")

    # ===== 4. 全データ統合（ML用） =====

    def create_ml_dataset(self):
        """
        全データを統合してML学習用データセットを作成
        """
        logger.info("\n" + "="*70)
        logger.info("4. ML学習用データセット作成")
        logger.info("="*70)

        ml_dir = self.output_dir / "ml_ready"
        ml_dir.mkdir(exist_ok=True)

        # 経済指標データ読み込み
        econ_file = self.output_dir / "economic_indicators" / "all_indicators.csv"
        econ_data = None
        if econ_file.exists():
            econ_data = pd.read_csv(econ_file, index_col='date', parse_dates=True)
            logger.info(f"経済指標データ読み込み: {len(econ_data)}件")

        # 各通貨ペアごとに統合
        price_dir = self.output_dir / "price_data"
        sentiment_dir = self.output_dir / "sentiment"

        for price_file in price_dir.glob("*.csv"):
            instrument = price_file.stem.replace("_full_history", "")
            logger.info(f"\n{instrument} のML用データセット作成中...")

            try:
                # 価格データ
                price_df = pd.read_csv(price_file, index_col='time', parse_dates=True)

                # センチメントデータ
                sentiment_file = sentiment_dir / f"{instrument}_sentiment.csv"
                if sentiment_file.exists():
                    sentiment_df = pd.read_csv(sentiment_file, index_col='time', parse_dates=True)
                    price_df = price_df.join(sentiment_df, how='left')

                # 経済指標データ（日次→時間足に拡張）
                if econ_data is not None:
                    # 日次データを時間足にリサンプル（前方補完）
                    econ_hourly = econ_data.resample('H').ffill()
                    price_df = price_df.join(econ_hourly, how='left')

                # ターゲット変数作成
                price_df['target_1h'] = price_df['close'].shift(-1) > price_df['close']  # 1時間後上昇
                price_df['target_4h'] = price_df['close'].shift(-4) > price_df['close']  # 4時間後上昇
                price_df['target_1d'] = price_df['close'].shift(-24) > price_df['close']  # 1日後上昇

                price_df['return_1h'] = price_df['close'].pct_change(1).shift(-1)  # 1時間リターン
                price_df['return_4h'] = price_df['close'].pct_change(4).shift(-4)  # 4時間リターン
                price_df['return_1d'] = price_df['close'].pct_change(24).shift(-24)  # 1日リターン

                # 欠損値を含む行を削除（または補完）
                price_df = price_df.ffill().bfill()

                # 保存
                output_file = ml_dir / f"{instrument}_ml_dataset.csv"
                price_df.to_csv(output_file)

                logger.info(f"  保存: {output_file}")
                logger.info(f"  サイズ: {price_df.shape}")
                logger.info(f"  期間: {price_df.index.min()} ~ {price_df.index.max()}")

            except Exception as e:
                logger.error(f"  エラー: {e}")
                continue

        logger.info("\n\nML用データセット作成完了!")

    # ===== メイン実行 =====

    def run(self, start_year: int = 2015, end_year: int = 2024):
        """全データ収集を実行"""
        logger.info("="*70)
        logger.info("包括的データ収集システム 開始")
        logger.info(f"期間: {start_year}年 ~ {end_year}年")
        logger.info("="*70 + "\n")

        start_time = time.time()

        # 1. 価格データ収集
        self.collect_full_price_history(start_year, end_year)

        # 2. 経済指標収集
        self.collect_economic_indicators(f"{start_year}-01-01")

        # 3. センチメントデータ生成
        self.collect_sentiment_data()

        # 4. ML用データセット作成
        self.create_ml_dataset()

        # メタデータ保存
        metadata = {
            "collection_date": datetime.now().isoformat(),
            "period": {"start_year": start_year, "end_year": end_year},
            "instruments": self.instruments,
            "execution_time_seconds": time.time() - start_time
        }

        with open(self.output_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info("\n" + "="*70)
        logger.info("全データ収集完了!")
        logger.info(f"保存先: {self.output_dir}")
        logger.info(f"実行時間: {time.time() - start_time:.1f}秒")
        logger.info("="*70)


def main():
    collector = ComprehensiveDataCollector()
    collector.run(start_year=2015, end_year=2024)


if __name__ == "__main__":
    main()
