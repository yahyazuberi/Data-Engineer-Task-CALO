import os
import pandas as pd
import openpyxl

class Exporter:
    def __init__(self, output_dir: str = '/output'):
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def to_excel(self, df: pd.DataFrame, filename: str, index: bool = False):
        
        for col in df.select_dtypes(include=["datetimetz"]).columns:
            df[col] = df[col].dt.tz_convert(None)

        
        file_path = os.path.join(self.output_dir, filename)
        df.to_excel(file_path, index=index, engine="openpyxl")
        print(f"✅ DataFrame written to: {file_path}")

    