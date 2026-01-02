"""
時間足データ収集 - 実行スクリプト
Yahoo Financeから無料・無制限でデータ取得
"""
from src.data_sources.yahoo_finance_hourly import collect_all_hourly_data

if __name__ == '__main__':
    # すべての通貨ペアの2年分1時間足データを収集
    results = collect_all_hourly_data()
    print(f"\n✅ {len(results)}通貨ペアのデータ収集完了")
