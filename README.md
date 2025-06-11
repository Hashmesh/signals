# Signals Data Pipeline

A data pipeline for collecting and processing token unlocks and social sentiment data using Prefect, Supabase, and S3.

## 🏗️ Architecture

- **Orchestration:** Self-hosted Prefect 2.x
- **Storage:**
  - Large Data: S3 (Parquet format)
  - Metadata: Supabase (PostgreSQL)
- **Deployment:** Docker containers

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- AWS account (for production)
- Supabase account

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd signals
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment template and fill in your credentials:
   ```bash
   cp .env.template .env
   ```

5. For local testing, ensure `storage_mode: local` is set in `storage/s3_config.yaml`

### Running with Docker (Self-hosted Prefect)

1. Build and start the services:
   ```bash
   docker-compose up --build
   ```

2. Access Prefect UI at: http://localhost:4200

3. Create deployments:
   ```bash
   python prefect/deployment.py
   ```

### Production Deployment

1. Set `storage_mode: s3` in `storage/s3_config.yaml`

2. Ensure all environment variables are set in `.env`:
   - AWS credentials
   - Supabase credentials

3. Build and push the worker image:
   ```bash
   docker build -t signals-worker:latest .
   ```

4. Deploy using docker-compose:
   ```bash
   docker-compose up -d
   ```

## 📊 Data Flows

### Token Unlocks Flow
- Runs daily at 1 AM UTC
- Collects token unlock schedules
- Stores raw data in Parquet format
- Updates metadata in Supabase

### Social Sentiment Flow
- Runs hourly
- Collects sentiment data from Twitter and Reddit
- Aggregates and processes sentiment scores
- Stores raw data in Parquet format
- Updates aggregated metrics in Supabase

## 📁 Project Structure

```
signals/
│
├── flows/
│   ├── ingest_token_unlocks.py     # Token unlocks ingestion flow
│   ├── ingest_social_sentiment.py   # Social sentiment ingestion flow
│   └── utils/
│       ├── s3.py                    # S3 utilities
│       ├── storage.py               # Storage management
│       └── supabase.py             # Supabase utilities
│
├── storage/
│   ├── s3_config.yaml              # Storage configuration
│   └── parquet_schema/             # Parquet schema definitions
│
├── prefect/
│   ├── deployment.py               # Prefect deployment configuration
│   └── docker-compose.yml          # Prefect server configuration
│
├── Dockerfile                      # Worker Dockerfile
├── docker-compose.yml             # Application docker-compose
├── requirements.txt               # Python dependencies
└── .env                          # Environment variables
```

## 🔧 Configuration

### Storage Modes

- **Local Mode**: For development and testing
  - Set `storage_mode: local` in `s3_config.yaml`
  - Data stored in `storage/data/`

- **S3 Mode**: For production
  - Set `storage_mode: s3` in `s3_config.yaml`
  - Requires AWS credentials

### Prefect Configuration

- Server runs on port 4200
- PostgreSQL backend for workflow state
- Docker-based worker infrastructure
- Configured work pools and deployments
