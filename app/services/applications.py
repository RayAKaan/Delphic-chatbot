"""Application lookup business logic (mock, deterministic)."""

from app.data.stores import ApplicationStore
from app.domain.models import Application


def lookup_application(store: ApplicationStore, candidate_id: str) -> Application | None:
    return store.find_by_candidate(candidate_id)
