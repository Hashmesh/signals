from prefect import flow, task
from datetime import datetime, timezone
import httpx
import json
import os
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
import psycopg2
import hashlib

NEWS_API_URL = os.getenv("NEWS_API_URL")
R2_BUCKET_NAME = os.getenv("TREE_OF_ALPHA_NEWS_BUCKET")
R2_PREFIX = os.getenv("TREE_OF_ALPHA_NEWS_PREFIX")
NEON_CONN = os.getenv("NEON_CONN")

def get_deterministic_id(record):
    base = f"{record.get('title', '')}-{record.get('url', '')}"
    return hashlib.sha256(base.encode()).hexdigest()

@task
def fetch_news():
    response = httpx.get(NEWS_API_URL)
    response.raise_for_status()
    return response.json()

@task
def normalize_news(records):
    rows = []
    for r in records:
        row = {
            "id": r.get("_id") or get_deterministic_id(r),
            "source": r.get("source"),
            "title": r.get("title"),
            "url": r.get("url"),
            "icon": r.get("icon"),
            "image": r.get("image"),
            "time": datetime.fromtimestamp(r["time"] / 1000, tz=timezone.utc),
            "symbols": r.get("symbols"),
            "first_price": r.get("firstPrice"),
            "info": r.get("info"),
            "suggestions": r.get("suggestions"),
        }
        rows.append(row)
    return rows

@task
def store_to_r2_parquet(records):
    ts = datetime.utcnow()
    year, month, day, hour = ts.year, ts.month, ts.day, ts.hour
    df = pd.DataFrame(records)
    table = pa.Table.from_pandas(df)

    out_buffer = BytesIO()
    pq.write_table(table, out_buffer, compression='gzip')
    out_buffer.seek(0)

    key = f"{R2_PREFIX}/year={year}/month={month:02d}/day={day:02d}/hour={hour:02d}/batch_{ts.strftime('%Y%m%dT%H%M%S')}.parquet"
    s3 = boto3.client("s3", endpoint_url=os.getenv("R2_ENDPOINT"), 
                      aws_access_key_id=os.getenv("R2_ACCESS_KEY"), 
                      aws_secret_access_key=os.getenv("R2_SECRET_KEY"))
    s3.upload_fileobj(out_buffer, R2_BUCKET_NAME, key)

@task
def upsert_to_neon(records):
    conn = psycopg2.connect(NEON_CONN)
    cur = conn.cursor()
    for r in records:
        cur.execute("""
            INSERT INTO news_items (id, source, title, url, icon, image, time, symbols, first_price, info, suggestions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            r["id"], r["source"], r["title"], r["url"], r["icon"], r["image"], r["time"],
            r.get("symbols"), json.dumps(r.get("first_price")), json.dumps(r.get("info")),
            json.dumps(r.get("suggestions"))
        ))
    conn.commit()
    cur.close()
    conn.close()

@flow
def tree_of_alpha_news_ingest():
    raw_data = fetch_news()
    normalized = normalize_news(raw_data)
    store_to_r2_parquet(normalized)
    upsert_to_neon(normalized)

if __name__ == "__main__":
    tree_of_alpha_news_ingest()
