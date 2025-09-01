import argparse
from utility import Utility
# from analysis import analyze_balance_sync, get_errors_over_time,get_top_error_reasons,get_total_loss_by_currency
from exporter import Exporter
from analysis import Analysis
import os


def main():
    parser = argparse.ArgumentParser(description="Log Parser Utility Runner")
    parser.add_argument(
        "--logs-dir",
        type=str,
        help="Root directory containing gzipped log files",
        required=True
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory where reports will be saved",
        required=True
    )
    args = parser.parse_args()

    utility = Utility()
    exporter = Exporter(args.output_dir)
    analysis = Analysis()

    print(f"Scanning directory: {args.logs_dir}")
    df = utility.process_gzipped_logs(args.logs_dir)

    if not df.empty:
        print(f"Parsed {len(df)} log entries")
        transactions = utility.extract_transactions(df)
        errors = utility.extract_errors(df)

        sync_errors_df = analysis.analyze_balance_sync(transactions, errors)

        output_file = "balance_sync_report.xlsx"
        output_path = os.path.join(args.output_dir, output_file)
        print(f"Saving report to {output_path}")
        exporter.to_excel(sync_errors_df, output_file)
        get_errors_over_time_file= 'get_errors_over_time.xlsx'
        analysis.get_errors_over_time(errors, os.path.join(args.output_dir, get_errors_over_time_file))
        get_top_error_reasons_file = 'get_top_error_reasons.xlsx'
        analysis.get_top_error_reasons(errors,transactions,os.path.join(args.output_dir, get_top_error_reasons_file))
        get_total_loss_by_currency_file = "get_total_loss_by_currency.xlsx"
        analysis.get_total_loss_by_currency(sync_errors_df,os.path.join(args.output_dir, get_total_loss_by_currency_file))
    else:
        print("No logs parsed.")


if __name__ == "__main__":
    main()
