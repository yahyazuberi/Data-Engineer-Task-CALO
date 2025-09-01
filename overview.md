# 🛠️ Implementation Details – Log Analyzer

This document provides a deeper look into the **design, implementation choices, and future improvements** for the Log Analyzer project.  
It complements the [README.md](./README.md) by focusing on the **why** and **how** behind the code.

---

## 📌 Overview

The Log Analyzer processes **gzipped transaction logs from CALO** and generates structured **Reports**.  
The pipeline is designed to detect and analyze:

- **Overdrafting**  
- **Balance synchronization issues**  
- **Error patterns leading to transaction failures**  
- **Loss incurred per currency due to failed syncs**  

The overall goal is to **trace overdraft events at a user level** and produce reports that highlight both **who was impacted** and **what the financial cost was**.

---

## 🔍 Main Task: Transaction Log Analysis

The **core objective** of this project was to make sense of the logs for the accounting team to understand the different trends a subscriber goes through from their payment history. **overdrafting** caused by failed balance synchronization.  

Steps implemented:  
1. **Parsing**  
    The logs were in compressed gzip file. The log files were read unzipped and parsed in standard dataframe extracting main information like time, request_id, log level and message body etc.
     
   - Each log line was scanned for transactions and errors with failure reasons in subsequest dataframes leading to 2 output df 1 with all transactions and other with errors.  
   - Using regex-based parsing, we extracted critical fields such as:
        - userId
        - requestId
        - timestamp
        - error type and reason
        
    - This step established the foundation for further anomaly detection, ensuring structured data could be derived from raw, unstructured logs. 

2. **Failure Mapping**  
   - After extracting error events, the next step was to map them to user transactions.  
   - We identified which user transactions failed and why.
   - Sync failures were carefully traced since they often caused cascading issues:
        - A failed sync meant the user’s balance wasn’t updated properly.
        - This led to downstream overdrafting (attempting transactions without sufficient balance due to stale state).  

3. **Overdraft Detection**  
   - By analyzing patterns of repeated sync failures, we determined when overdrafting began for each affected user. 
   - A timeline of overdraft events was constructed, pinpointing the first occurrence and subsequent failures.
   - The analysis produced a per-user overdraft history, making it easier to trace systemic vs. user-specific issues. 

4. **Final Reports**  
For each affected user, a detailed Excel report is generated in the output/ directory. These reports contain:
    - An excel report that displays a hollictic view by userId identifying the potential credit and debit loss CALO incurred due to sync failures.
    - Currency-wise losses in terms of credit and debit transactions that occured due to balance sync failures.
   - Errors grouped by type and reason. 
   - Overdraft events with exact timestamps.

5. **Loss Analysis (Charts)**  
   - Beyond individual reports, we also calculated total financial losses per currency resulting from overdraft-related failures. 
   - These losses were visualized using charts (matplotlib) and exported to Excel for better readability.
   - To make review faster, snapshots of these charts are also stored in the snapshots/ directory.

---


## 🚀 Anomoly Detection:
Once all sync errors were extracted, we performed a time-based analysis to identify the periods with the highest error occurrences. These were visualized in a month-to-month error trend chart, highlighting anomalies and unusual spikes.

From the analysis, it was observed that December 2023 (2023-12) recorded the highest number of errors, pointing to a potential system anomaly/bug that was later resolved.

When you run this project, the chart will be automatically generated as get_errors_over_time in the output directory, allowing you to easily spot similar anomalies in future runs.


## 📊 Current Outputs

1. **Overdraft Reports (Per User)**  
   - Generated in `output/`.  
   - Contains details of failed transactions, overdraft timestamps, and sync mismatches. 
        -  **balance_sync_report** A final structured report is generated listing each userId with sync failures, including total and failed transactions, transaction currency, first error occurrence, and estimated credit/debit loss.
        -  **get_total_loss_by_currency** A hollistic view by currency of CALO potential loss due to transaction sync failures
        -  **get_top_error_reasons** A visilization of top reason captured for trasaction failures
        -  **get_errors_over_time** A timescale graph is generated showing error counts on a month-to-month basis, helping highlight anomalies and potential system bugs.

2. **Error & Loss Charts**  
   - Aggregated **loss per currency** visualized in charts.  
   - Timeline identifying the timeframe where mostly balance sync failed pointing anomloy and putting attention towards that fram to look for potential cause
   - Top failure reasons incuured to analyse the root cause.
   - Stored in Excel and **snapshots/** folder for quick reference.  

---


## 🔧 Key Implementation Decisions

### Language: **Python**
- Chosen for strong **ecosystem in data analysis** (pandas, matplotlib, openpyxl).  
- Flexible for log parsing and scalable for processing large gzipped files.

### Log Parsing
- **gzip + regex parsing** for handling compressed input files directly.  
- Keeps memory usage efficient while still extracting structured fields.

### Data Analysis
- **pandas DataFrames** for transformations, joins, and anomaly checks.  
- Core analysis logic (`analysis.py`) detects overdraft events and error trends.

### Reporting
- **Excel (`.xlsx`) reports** with:
  - Balance sync/overdraft tables.  
  - Error breakdowns.  
  - Embedded charts for loss analysis.  
- Preferred format for business teams (easy to share and filter).

### Containerization
- **Dockerfile** for consistent execution across machines.  
- Encapsulates dependencies (Python, pandas, openpyxl, matplotlib).  

---


## 🚀 Future Improvements

### Technical
- Parallelize parsing with **dask or pyspark** for very large log sets.  
- Store parsed logs in a **SQL database** for faster repeated queries.  
- Add **configurable overdraft detection rules** via JSON/YAML.

### Reporting
- Enhance Excel reports with **pivot tables and slicers**.  
- Create **interactive dashboards** (Streamlit/Plotly) for real-time exploration.  
- Add **PDF executive summaries** for quick stakeholder updates.



---

## ✅ Conclusion

The Log Analyzer was primarily designed to **detect overdrafting issues** caused by balance sync failures.  
By analyzing **errors → failed transactions → overdraft impact**, the system produces **per-user reports** and **currency-wise loss charts**.  

This ensures both **technical teams (debugging root causes)** and **business teams (estimating financial loss)** have actionable insights.
