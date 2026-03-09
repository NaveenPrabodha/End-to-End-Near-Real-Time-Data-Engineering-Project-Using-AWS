# End-to-End-Near-Real-Time-Data-Engineering-Project-Using-AWS
In this project, set up an end-to-end real-time data pipeline using AWS Kinesis Data Firehose. The goal is to ingest data from an API, process it in real-time, store it in Amazon S3, and query it using Amazon Athena for analytics.




# 🚀 End-to-End Near Real-Time Data Engineering Pipeline on AWS

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

A fully automated, near real-time data pipeline that ingests stock market data from the **Alpha Vantage API**, streams it through **AWS Kinesis Firehose**, stores it in **Amazon S3**, and makes it queryable via **Amazon Athena** — all with CI/CD deployment via GitHub Actions.

> 📖 Based on the Medium series: [Part 1](https://medium.com/data-epic/end-to-end-near-real-time-data-engineering-project-using-aws-services-part-1-47bf44a5d84b) | [Part 2](https://medium.com/data-epic/end-to-end-near-real-time-data-engineering-project-using-aws-services-part-2-09be1533952a)

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Alpha Vantage  │────▶│  AWS Lambda      │────▶│  Kinesis Firehose   │
│  Stock API      │     │  (Producer)      │     │  (Delivery Stream)  │
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                 ▲                           │
                        ┌────────┴────────┐                  ▼
                        │  EventBridge    │         ┌────────────────┐
                        │  (Scheduler)   │         │   Amazon S3    │
                        └─────────────────┘         │  (Data Lake)   │
                                                    └───────┬────────┘
                                                            │
                                              ┌─────────────▼──────────┐
                                              │   AWS Glue Crawler     │
                                              │   (Schema Discovery)   │
                                              └─────────────┬──────────┘
                                                            │
                                              ┌─────────────▼──────────┐
                                              │    Amazon Athena       │
                                              │   (SQL Analytics)      │
                                              └────────────────────────┘
```

![Architecture Diagram](architecture/architecture_diagram.png)

---

## 🛠️ Tech Stack

| Service | Purpose |
|---|---|
| **AWS Lambda** | Fetch stock data & push to Firehose |
| **Amazon Kinesis Firehose** | Buffer & deliver streaming data to S3 |
| **Amazon S3** | Raw data storage / data lake |
| **AWS Glue Crawler** | Auto-discover schema from S3 data |
| **Amazon Athena** | SQL queries on S3 data |
| **Amazon EventBridge** | Schedule Lambda every N minutes |
| **GitHub Actions** | CI/CD — auto-deploy Lambda on push |
| **Alpha Vantage API** | Real-time stock market data |

---

## 📁 Project Structure

```
aws-realtime-data-pipeline/
├── README.md
├── architecture/
│   ├── architecture_diagram.png
│   └── data_flow_diagram.png
├── lambda/
│   └── data_producer/
│       ├── lambda_function.py       # Core Lambda handler
│       └── requirements.txt
├── scripts/
│   ├── setup_firehose.py            # Create Kinesis Firehose stream
│   ├── setup_s3_bucket.py           # Create & configure S3 bucket
│   ├── setup_eventbridge.py         # Create EventBridge rule
│   ├── setup_athena.py              # Create Athena DB + table
│   └── test_pipeline.py             # End-to-end smoke test
├── sql/
│   ├── create_table.sql             # Athena DDL
│   └── sample_queries.sql           # Analytics queries
├── ci-cd/
│   └── .github/
│       └── workflows/
│           └── deploy_lambda.yml    # GitHub Actions CI/CD
├── configs/
│   ├── firehose_config.json
│   ├── eventbridge_rule.json
│   └── iam_policies/
│       ├── lambda_policy.json
│       └── firehose_policy.json
└── docs/
    ├── setup_guide.md
    └── troubleshooting.md
```

---

## ⚡ Prerequisites

- AWS Account with appropriate IAM permissions
- [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) (free)
- Python 3.11+
- AWS CLI configured (`aws configure`)
- GitHub repository with Actions enabled

---

## 🚀 Quick Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/aws-realtime-data-pipeline.git
cd aws-realtime-data-pipeline
```

### 2. Set environment variables
```bash
export AWS_REGION=us-east-1
export ALPHA_VANTAGE_API_KEY=your_api_key_here
export S3_BUCKET_NAME=your-stock-data-bucket
export FIREHOSE_STREAM_NAME=stock-data-stream
```

### 3. Run infrastructure setup scripts
```bash
pip install boto3
python scripts/setup_s3_bucket.py
python scripts/setup_firehose.py
python scripts/setup_eventbridge.py
python scripts/setup_athena.py
```

### 4. Deploy Lambda (manual)
```bash
cd lambda/data_producer
pip install -r requirements.txt -t .
zip -r ../../lambda_package.zip .
aws lambda create-function \
  --function-name stock-data-producer \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://../../lambda_package.zip
```

### 5. Set GitHub Secrets for CI/CD
Go to **Settings → Secrets → Actions** and add:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ALPHA_VANTAGE_API_KEY`
- `S3_BUCKET_NAME`
- `FIREHOSE_STREAM_NAME`

Push to `main` branch — GitHub Actions will auto-deploy Lambda! ✅

---

## 💰 Cost Estimate

Running this pipeline is **nearly free-tier eligible**:

| Service | Free Tier | Estimated Cost |
|---|---|---|
| Lambda | 1M requests/month | ~$0 |
| Kinesis Firehose | First 500 GB/month | ~$0–$1 |
| S3 | 5 GB storage | ~$0 |
| Athena | First 1 TB queries | ~$0 |
| Glue Crawler | First 1M DPU-seconds | ~$0 |

> ⚠️ Always set AWS billing alerts!

---

## 📊 Sample Athena Query Results

After the pipeline runs, you can query like:
```sql
SELECT symbol, timestamp, open, high, low, close, volume
FROM stock_data
WHERE symbol = 'AAPL'
ORDER BY timestamp DESC
LIMIT 10;
```

---

## 📚 Resources

- [Medium Article Part 1](https://medium.com/data-epic/end-to-end-near-real-time-data-engineering-project-using-aws-services-part-1-47bf44a5d84b)
- [Medium Article Part 2](https://medium.com/data-epic/end-to-end-near-real-time-data-engineering-project-using-aws-services-part-2-09be1533952a)
- [Alpha Vantage API Docs](https://www.alphavantage.co/documentation/)
- [AWS Kinesis Firehose Docs](https://docs.aws.amazon.com/firehose/)
- [Amazon Athena Docs](https://docs.aws.amazon.com/athena/)

---

## 📄 License

This project is licensed under the MIT License.
