# 📊 Log Analyzer  

This project processes gzipped **transaction logs from CALO** and extracts structured insights for further investigation.  
It focuses on detecting **balance synchronization issues**, **overdrafting**, and **losses**, while generating **Excel-based analytical reports** with both tabular and graphical views.  

*implemetaion details can be found in **overview.md***

---

## ⚙️ Project Structure  


```bash
.
├── main.py                # Entry point: parses logs, runs analysis, generates reports
├── utility.py             # Handles log reading and extraction
├── analysis.py            # Provides anomaly detection & error analysis
├── exporter.py            # Exports results into Excel with charts
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build instructions
└── README.md              # Documentation
```

## 🚀 Setup & Usage

### 1. Direct Run (Local Environment)
Install dependencies:
```BASh
pip install -r requirements.txt
```

Run the analyzer:
```bash
python main.py --logs-dir ./input --output-dir ./output
```
Example with your own paths:
```bash
python main.py \
  --logs-dir /Users/macbook/Documents/data-eng/balance-recon/a3fb6cdb-607b-469f-8f8a-ec4792e827cb \
  --output-dir /Users/macbook/Documents/data-eng/output
```

### 2. Run with Docker

Build the image:

```bash
docker build -t log-analyzer .
```

Run the container (mount input and output directories):
```bash
docker run --rm \
  -v /path/to/logs:/app/input \
  -v /path/to/output:/app/output \
  log-analyzer \
  --logs-dir /app/input \
  --output-dir /app/output
```

Replace /path/to/logs with the directory containing gzipped logs and /path/to/output with where you want reports saved.


📑 Generated Reports

After running, the following Excel reports will be available inside your chosen --output-dir:
| Report File                             | Description                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **balance\_sync\_report.xlsx**          | Detailed breakdown of balance synchronization issues (e.g., overdrafts, debit/credit mismatches per user/currency). |
| **get\_errors\_over\_time.xlsx**        | Timeline of errors aggregated monthly, with **charts** showing error trends.                                        |
| **get\_top\_error\_reasons.xlsx**       | Most frequent error reasons, useful for **root-cause analysis**.                                                    |
| **get\_total\_loss\_by\_currency.xlsx** | Summary of debit/credit losses per currency, with **graphical visualization of financial impact**.                  |

## 📁 Overview.md

  For implementaion details please refer to overview.md file. 