# 📈 End-to-End Near Real-Time Stock Data Pipeline on AWS

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![Apache Parquet](https://img.shields.io/badge/Apache%20Parquet-50ABF1?style=for-the-badge&logo=apache&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A fully serverless, near real-time data pipeline that ingests live stock market data for **TSLA** and **NVDA** from the Alpha Vantage API, streams it through **AWS Kinesis Firehose**, transforms and stores it as partitioned **Parquet files** in Amazon S3, queries it with **Amazon Athena**, and visualizes it via a **Streamlit dashboard**.

Dashboard Link: http://51.21.209.34:8501 
---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Alpha Vantage     │
│   Stock Market API  │
└────────┬────────────┘
         │ HTTP Request (every 5 min)
         ▼
┌─────────────────────┐
│   Amazon            │
│   EventBridge       │──────── Triggers every 5 minutes
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   AWS Lambda        │
│   (Producer)        │──── Fetches TSLA + NVDA data
└────────┬────────────┘
         │ put_record_batch()
         ▼
┌─────────────────────┐         ┌──────────────────────┐
│   Kinesis           │────────▶│  S3 Raw Backup        │
│   Data Firehose     │         │  (dp-raw-stock-data)  │
└────────┬────────────┘         └──────────────────────┘
         │ Invokes transformer
         ▼
┌─────────────────────┐
│   AWS Lambda        │
│   (Transformer)     │──── Cleans data + adds partition keys
└────────┬────────────┘
         │ Parquet conversion via Glue schema
         ▼
┌──────────────────────────────────────────────────┐
│   Amazon S3 (dp-transformed-stock-data)          │
│                                                  │
│   data/                                          │
│   └── symbol=TSLA/                               │
│       └── date=2026-03-10/                       │
│           └── hour=14/                           │
│               └── file.parquet                   │
└────────┬─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│   AWS Glue          │──── Holds schema (stock_db / stock_prices)
│   Data Catalog      │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Amazon Athena     │──── SQL queries directly on S3
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Streamlit         │──── Live dashboard on EC2
│   Dashboard         │
└─────────────────────┘
```

---

## ⚙️ AWS Services Used

| Service | Role |
|---|---|
| 🕐 **Amazon EventBridge** | Triggers producer Lambda every 5 minutes |
| ⚡ **AWS Lambda (Producer)** | Fetches stock data from API, sends to Firehose |
| 🚀 **Amazon Kinesis Firehose** | Buffers and streams data to S3 with transformation |
| ⚡ **AWS Lambda (Transformer)** | Cleans records, renames fields, adds partition keys |
| 🪣 **Amazon S3 (Raw)** | Backup of all original unmodified records |
| 🪣 **Amazon S3 (Transformed)** | Final partitioned Parquet files for analytics |
| 🗂️ **AWS Glue Data Catalog** | Schema registry used by Athena to read Parquet |
| 🔍 **Amazon Athena** | Serverless SQL engine querying data directly from S3 |
| 📊 **Amazon CloudWatch** | Logs and error monitoring for Lambda + Firehose |

---

## 📁 Project Structure

```
aws-stock-pipeline/
│
├── lambda/
│   ├── producer.py              # Fetches API data, sends to Firehose
│   └── transformer.py           # Transforms records, adds partition keys
│
├── dashboard/
│   └── stock_dashboard.py       # Streamlit visualization dashboard
│
├── sql/
│   └── sample_queries.sql       # Useful Athena queries
│
└── README.md
```

---

## 🗄️ Glue Table Schema

**Database:** `stock_db` | **Table:** `stock_prices`

| Column | Type | Description |
|---|---|---|
| `symbol` | string | Stock ticker (TSLA / NVDA) |
| `event_time` | string | Full datetime of the record |
| `open` | double | Opening price |
| `high` | double | Highest price in interval |
| `low` | double | Lowest price in interval |
| `close` | double | Closing price |
| `volume` | bigint | Number of shares traded |
| `date` | string | ⭐ Partition key |
| `hour` | int | ⭐ Partition key |

**Partition Keys:** `symbol` → `date` → `hour`

---

## 🔍 S3 Folder Structure

Data is stored in Hive-style partitioning for efficient querying:

```
dp-transformed-stock-data/
└── data/
    ├── symbol=TSLA/
    │   └── date=2026-03-10/
    │       ├── hour=13/
    │       │   └── file.parquet
    │       └── hour=14/
    │           └── file.parquet
    └── symbol=NVDA/
        └── date=2026-03-10/
            └── hour=14/
                └── file.parquet
```

---

## 🔍 Sample Athena Queries

```sql
-- Register all partitions first (run once)
MSCK REPAIR TABLE stock_prices;

-- Query using partition keys (fastest + cheapest)
SELECT * FROM stock_prices
WHERE symbol = 'TSLA'
AND date = '2026-03-10'
AND hour = 14;

-- Average closing price per day per stock
SELECT symbol, date, ROUND(AVG(close), 2) AS avg_close
FROM stock_prices
GROUP BY symbol, date
ORDER BY date DESC;

-- Highest price NVDA ever hit
SELECT symbol, event_time, high
FROM stock_prices
WHERE symbol = 'NVDA'
ORDER BY high DESC
LIMIT 5;

-- Trading volume by hour
SELECT hour, SUM(volume) AS total_volume
FROM stock_prices
GROUP BY hour
ORDER BY total_volume DESC;
```

> 💡 **Tip:** Always filter on partition keys (`symbol`, `date`, `hour`) first — Athena will skip irrelevant folders and scan far less data, saving both time and cost.

---

## 📊 Streamlit Dashboard

A local dashboard built with Streamlit connects directly to Athena and visualizes the pipeline data in real time.

**Features:**
- 📌 Stock selector — TSLA, NVDA, or Both
- 📅 Date filter — picks from all available dates in the pipeline
- 📈 Close price line chart over time
- 🕯️ Candlestick chart (OHLC)
- 📊 Volume bar chart by hour
- 🔢 Key metrics — High, Low, Avg Close, Total Volume
- 🗃️ Raw data table
  
<img width="2924" height="1508" alt="image" src="https://github.com/user-attachments/assets/ba3357cc-984f-4246-b7e7-063ee2f937e0" />

**Setup:**
```bash
pip install streamlit boto3 pyathena pandas plotly
streamlit run dashboard/stock_dashboard.py
```

Opens at → `http://localhost:8501`

---

## 💰 Cost Breakdown

| Service | Free Tier | Estimated Monthly Cost |
|---|---|---|
| AWS Lambda | 1M requests/month | ✅ Free |
| Amazon S3 | 5 GB storage | ✅ Free |
| Amazon EventBridge | 14M events/month | ✅ Free |
| AWS Glue Catalog | First 1M objects | ✅ Free |
| Amazon CloudWatch | Basic monitoring | ✅ Free |
| Amazon Athena | ~$0.005 per query | ✅ ~$0.01 |
| **Kinesis Firehose** | Not in free tier | 💲 ~$0.63 |
| **Total** | | **~$0.64/month** |

> ⚠️ Set up an AWS billing alert to avoid surprises!

---

## 🔐 IAM Permissions

| Resource | Permission Required |
|---|---|
| Producer Lambda role | `AmazonKinesisFirehoseFullAccess` |
| Kinesis Firehose | Auto-created service role |
| Streamlit (local) | `AmazonAthenaFullAccess` + `AmazonS3FullAccess` |

---

## 🌍 AWS Region

All resources deployed in **`eu-north-1`** (Europe — Stockholm)

---

## 📡 Data Source

Stock data provided by [Alpha Vantage API](https://rapidapi.com/alphavantage/api/alpha-vantage) via RapidAPI.
- Stocks tracked: **TSLA**, **NVDA**
- Interval: **1 minute**
- Trigger frequency: **every 5 minutes**

---

## 📚 Resources

- [Amazon Kinesis Firehose Docs](https://docs.aws.amazon.com/firehose/)
- [Amazon Athena Docs](https://docs.aws.amazon.com/athena/)
- [AWS Glue Data Catalog](https://docs.aws.amazon.com/glue/)
- [Alpha Vantage API Docs](https://www.alphavantage.co/documentation/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [PyAthena — Python Athena Client](https://github.com/laughingman7743/PyAthena)

---

## 📄 License

This project is licensed under the MIT License.
