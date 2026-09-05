"""Job lookup and search business logic (mock, deterministic)."""

from app.data.stores import JobStore
from app.domain.intents import Entities
from app.domain.models import Job


def search_jobs(store: JobStore, entities: Entities) -> list[Job]:
    return store.search(
        role=entities.role,
        location=entities.location,
        experience=entities.experience,
        qualification=entities.qualification,
    )


def get_job_details(store: JobStore, job_id: str) -> Job | None:
    return store.find_open(job_id)
