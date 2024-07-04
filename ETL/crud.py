from sqlalchemy.orm import Session
from sqlalchemy import and_

from sqllite_database.database import get_db
from sqllite_database.models import Advisor, BrokerCheckData, LinkedInProfile
import pandas as pd

from ETL.scrapper.rapid_api_client import RapidApiLIProfileClient


def create_advisor(db: Session, advisor_data: dict):
    advisor = Advisor(**advisor_data)
    db.add(advisor)
    db.commit()
    db.refresh(advisor)
    return advisor


def create_advisor_batch(advisor_data_batch: list):
    print("Inside Create Advisor Batch")
    db = get_db()
    print(db)
    try:
        advisors = [Advisor(**advisor_data) for advisor_data in advisor_data_batch]
        db.bulk_save_objects(advisors)
        db.commit()
        print(f"Processed a batch of {len(advisors)} advisors")
    except Exception as e:
        db.rollback()
        print(f"Skipping batch due to error: {e}")
    finally:
        db.close()


def get_advisors_with_linkedin_data(db: Session, limit: int):
    return (
        db.query(Advisor)
        .filter(and_(Advisor.crd.isnot(None), Advisor.linkedin.isnot(None)))
        .limit(limit)
        .all()
    )


def store_linkedin_data(db: Session, advisor_id: int, linkedin_data: dict):
    linkedin_entry = LinkedInProfile(advisor_id=advisor_id, data=linkedin_data)
    db.add(linkedin_entry)
    db.commit()
    db.refresh(linkedin_entry)
    return linkedin_entry


def get_advisor_by_crd(db: Session, crd: int):
    return db.query(Advisor).filter(Advisor.crd == crd).first()


def update_advisor(db: Session, advisor_id: int, update_data: dict):
    db.query(Advisor).filter(Advisor.id == advisor_id).update(update_data)
    db.commit()


def delete_advisor(db: Session, advisor_id: int):
    db.query(Advisor).filter(Advisor.id == advisor_id).delete()
    db.commit()


def create_broker(
    session: Session, advisor_id: int, broker_data: dict
) -> BrokerCheckData:
    broker = BrokerCheckData(
        advisor_id=advisor_id,
        disclosures=broker_data.get("disclosures"),
        timeline=broker_data.get("timeline"),
        exams=broker_data.get("exams"),
        state_registrations=broker_data.get("state_registrations"),
        sro_registrations=broker_data.get("sro_registrations"),
        current_registrations=broker_data.get("current_registrations"),
        previous_registrations=broker_data.get("previous_registrations"),
    )
    session.add(broker)
    session.commit()
    session.refresh(broker)
    return broker


def get_broker_check_data_by_advisor_id(
    db: Session, advisor_id: int
) -> BrokerCheckData:
    return (
        db.query(BrokerCheckData)
        .filter(BrokerCheckData.advisor_id == advisor_id)
        .first()
    )


def update_broker_check_data(
    db: Session, broker_data: BrokerCheckData, update_data: dict
) -> BrokerCheckData:
    for key, value in update_data.items():
        setattr(broker_data, key, value)
    db.commit()
    db.refresh(broker_data)
    return broker_data


def delete_broker_check_data(db: Session, broker_data: BrokerCheckData):
    db.delete(broker_data)
    db.commit()


def create_linkedin_profile(
    db: Session, advisor_id: int, linkedin_data: dict
) -> LinkedInProfile:
    # import pdb; pdb.set_trace()
    linkedin_profile = LinkedInProfile(
        advisor_id=advisor_id,
        urn=linkedin_data.get("urn"),
        username=linkedin_data.get("username"),
        firstName=linkedin_data.get("firstName"),
        lastName=linkedin_data.get("lastName"),
        isCreator=linkedin_data.get("isCreator") == "Yes",
        isOpenToWork=linkedin_data.get("isOpenToWork") == "Yes",
        isHiring=linkedin_data.get("isHiring") == "Yes",
        profilePicture=linkedin_data.get("profilePicture"),
        backgroundImage=linkedin_data.get("backgroundImage"),
        summary=linkedin_data.get("summary"),
        headline=linkedin_data.get("headline"),
        geo=linkedin_data.get("geo"),
        languages=linkedin_data.get("languages"),
        educations=linkedin_data.get("educations"),
        position=linkedin_data.get("position"),
        fullPositions=linkedin_data.get("fullPositions"),
        skills=linkedin_data.get("skills"),
        courses=linkedin_data.get("courses"),
        certifications=linkedin_data.get("certifications"),
        honors=linkedin_data.get("honors"),
        projects=linkedin_data.get("projects"),
        volunteering=linkedin_data.get("volunteering"),
    )
    db.add(linkedin_profile)
    db.commit()
    db.refresh(linkedin_profile)
    return linkedin_profile


def get_linkedin_profile_by_advisor_id(db: Session, advisor_id: int) -> LinkedInProfile:
    return (
        db.query(LinkedInProfile)
        .filter(LinkedInProfile.advisor_id == advisor_id)
        .first()
    )


def update_linkedin_profile(
    db: Session, linkedin_profile: LinkedInProfile, update_data: dict
) -> LinkedInProfile:
    for key, value in update_data.items():
        setattr(linkedin_profile, key, value)
    db.commit()
    db.refresh(linkedin_profile)
    return linkedin_profile


def delete_linkedin_profile(db: Session, linkedin_profile: LinkedInProfile):
    db.delete(linkedin_profile)
    db.commit()
