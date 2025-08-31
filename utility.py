import os
import re
import gzip
import pandas as pd
import ast
import json
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows


LOG_PATTERN = re.compile(
    r'^(?P<time>\d{4}-\d{2}-\d{2}T[0-9:.]+Z)'
    r'(?:\s+(?P<category>\S+))?'
    r'(?:\s+RequestId:\s*(?P<req_id>[\w-]+))?'
    r'(?:\s+Version:\s*(?P<ver>\S+))?'
    r'(?:\t(?P<secondary_time>\d{4}-\d{2}-\d{2}T[0-9:.]+Z))?'
    r'(?:\t(?P<secondary_req_id>[\w-]+))?'
    r'(?:\t(?P<level>\w+))?'
)



class Utility:
    
    TRANSACTION_PATTERN = {
        'id': r"id: '([^']*)'",
        'type': r"type: '([^']*)'",
        'source': r"source: '([^']*)'",
        'action': r"action: '([^']*)'",
        'userId': r"userId: '([^']*)'",
        'paymentBalance': r"paymentBalance: (\d+)",
        'updatePaymentBalance': r"updatePaymentBalance: (true|false)",
        'metadata': r"metadata: '([^']*)'",
        'currency': r"currency: '([^']*)'",
        'amount': r"amount: (\d+\.?\d*)",   # handles int & float
        'vat': r"vat: (\d+\.?\d*)",
        'oldBalance': r"oldBalance: (\d+)",
        'newBalance': r"newBalance: (\d+)",
    }

    def __init__(self, pattern: re.Pattern = LOG_PATTERN):
        self.pattern = pattern

    def extract(self, raw_logs: str) -> pd.DataFrame:
        
        sections = re.split(r'(?=^\d{4}-\d{2}-\d{2}T[0-9:.]+Z)', raw_logs, flags=re.MULTILINE)
        
        records = []
        for chunk in sections:
            if not chunk.strip():
                continue

            rows = chunk.splitlines()
            first_row = rows[0]

            match = self.pattern.match(first_row)

            entry = {
                'time': None, 'category': None, 'req_id': None, 'ver': None,
                'secondary_time': None, 'secondary_req_id': None, 'level': None
            }

            if match:
                entry.update({k: match.group(k) for k in entry.keys() if match.group(k) is not None})
                inline_text = first_row[match.end():].strip()
            else:
                inline_text = first_row

            # Add full log message
            msg = inline_text
            if len(rows) > 1:
                msg += '\n' + '\n'.join(rows[1:])
            entry['message'] = msg

            records.append(entry)

        return pd.DataFrame(records)

    def process_gzipped_logs(self, root_directory: str) -> pd.DataFrame:
        
        all_dfs = []
        
        if not os.path.isdir(root_directory):
            print(f"Error: The directory '{root_directory}' does not exist.")
            return pd.DataFrame()

        for dirpath, _, filenames in os.walk(root_directory):
            for filename in filenames:
                if filename.endswith('.gz'):
                    file_path = os.path.join(dirpath, filename)
                    print(f"Processing file: {file_path}")
                    try:
                        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                            log_content = f.read()
                        
                        df = self.extract(log_content)
                        if not df.empty:
                            df['source_file'] = file_path
                            all_dfs.append(df)
                        
                    except Exception as e:
                        print(f"Could not read or parse file {file_path}. Error: {e}")

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)

            # Convert time fields to datetime
            combined_df['time'] = pd.to_datetime(combined_df['time'], errors='coerce')
            combined_df['secondary_time'] = pd.to_datetime(combined_df['secondary_time'], errors='coerce')
            
            # Sort by the primary time
            combined_df = combined_df.sort_values(by='time').reset_index(drop=True)
            return combined_df
        else:
            print("No gzipped log files found or parsed.")
            return pd.DataFrame()

    def extract_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        
        records = []

        for _, row in df.iterrows():
            record = {}
            message = row.get("message", "")

            # Parse using regex patterns
            for key, pat in self.TRANSACTION_PATTERN.items():
                m = re.search(pat, message)
                if key == "id" and not m:
                    break  # if there's no transaction id, skip this row
                if not m:
                    record[key] = None
                else:
                    val = m.group(1)
                    if key in ["paymentBalance", "oldBalance", "newBalance"]:
                        record[key] = int(val)
                    elif key in ["amount", "vat"]:
                        record[key] = float(val)
                    elif key == "updatePaymentBalance":
                        record[key] = True if val == "true" else False
                    else:
                        record[key] = val

            if record:  # add only if we found a transaction
                record["request_id"] = row.get("secondary_req_id")
                record["timestamp"] = row.get("time")
                records.append(record)

        parsed_df = pd.DataFrame(records)
        if not parsed_df.empty:
            parsed_df["timestamp"] = pd.to_datetime(parsed_df["timestamp"])
        return parsed_df

    def extract_errors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract error logs from the parsed DataFrame.
        Only keeps timestamp, request_id (from secondary), and message.
        """
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "request_id", "message"])

        df['level'] = df['level'].str.upper().fillna("")

        error_df = df[
            (df['level'] == "ERROR") |
            (df['message'].str.contains(r"\berror\b", case=False, na=False))
        ].copy()

        # Use secondary_request_id as the main request_id for errors
        error_df['request_id'] = error_df['secondary_req_id'].fillna(error_df['secondary_req_id'])

        error_df = error_df[['time', 'request_id', 'message']]

        return error_df.reset_index(drop=True)


# create parser instance
parser = Utility()


# parse all gzipped logs in a directory
# df2 = parser.process_gzipped_logs('/Users/macbook/Documents/data-eng/balance-recon/a3fb6cdb-607b-469f-8f8a-ec4792e827cb')
# print(df2.head())
# df2.to_csv("output.csv", index=False) 
