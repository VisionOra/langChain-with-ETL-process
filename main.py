from concurrent.futures import ThreadPoolExecutor
import math
from sqlalchemy.orm import Session
from database import create_tables, get_db
from crud import (
    create_advisor_batch,
    create_broker,
    get_advisor_by_crd,
    get_advisors_with_linkedin_data,
    create_linkedin_profile,
)
from models import Advisor
import pandas as pd
from rapid_api_client import RapidApiLIProfileClient
from scraper import BrokerInfoScraper
import json


def is_db_populated(db: Session) -> bool:
    """Check if the database has been populated."""
    advisor_count = db.query(Advisor).count()
    print("count: ", advisor_count)
    return advisor_count > 0


def process_batches(df: pd.DataFrame, batch_size: int):
    print("Inside Process Batches")
    num_batches = math.ceil(len(df) / batch_size)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(num_batches):
            start_index = i * batch_size
            end_index = start_index + batch_size
            batch_df = df.iloc[start_index:end_index]
            advisor_data_batch = batch_df.to_dict(orient="records")
            executor.submit(create_advisor_batch, advisor_data_batch)


def fetch_and_store_linkedin_data(
    db: Session, advisor: Advisor, rapid_api_client: RapidApiLIProfileClient
):
    try:
        username = advisor.linkedin.split("/")[-1]
        linkedin_data = rapid_api_client.get_user_data(username)
        profile = create_linkedin_profile(db, advisor.id, linkedin_data)
        print(profile)
    except Exception as e:
        print(f"Error processing advisor {advisor.id}: {e}")


def fetch_and_store_broker_check_data(db: Session, advisor: Advisor):
    try:
        crd = advisor.crd
        scraper = BrokerInfoScraper(crd)
        scraper.scrape_info()
        broker_info = scraper.get_broker_info()
        db_broker = create_broker(db, advisor.id, broker_info)
        print(db_broker)
    except Exception as e:
        print(f"Error processing advisor {advisor.id}: {e}")


def main():
    # Create the tables only if they do not exist
    db = get_db()

    print("Database is empty. Creating tables and loading data.")
    create_tables()

    # Load CSV data
    file_path = "AdvizorPro_Person_04.24.2024-1.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")

    # Process data in batches
    batch_size = 100
    process_batches(df, batch_size)

    advisor = get_advisor_by_crd(db, 1000034)
    if advisor:
        print(advisor)
    else:
        print("Advisor with CRD 1000034 not found.")

    limit = 15
    rapid_api_client = RapidApiLIProfileClient()
    advisors = get_advisors_with_linkedin_data(db, limit)

    for advisor in advisors:
        fetch_and_store_linkedin_data(db, advisor, rapid_api_client)
        fetch_and_store_broker_check_data(db, advisor)


if __name__ == "__main__":
    main()
