"""Candidate business operations (mock, deterministic)."""

from app.data.stores import CandidateStore
from app.domain.models import Candidate


def find_or_create(store: CandidateStore, whatsapp_number: str) -> tuple[Candidate, bool]:
    """Return (candidate, is_new). Creates a minimal local record when the
    WhatsApp number is unknown. No profile data is collected here yet."""
    existing = store.find_by_whatsapp(whatsapp_number)
    if existing is not None:
        return existing, False
    candidate = Candidate(
        candidate_id=store.next_id(),
        whatsapp_number=whatsapp_number,
        status="ACTIVE",
    )
    store.create(candidate)
    return candidate, True


def update_from_entities(store: CandidateStore, candidate: Candidate, updates: dict) -> Candidate:
    """Apply provided fields to a candidate and persist the result."""
    changed = {
        key: value
        for key, value in updates.items()
        if value is not None and getattr(candidate, key, None) != value
    }
    if not changed:
        return candidate
    updated = candidate.model_copy(update=changed)
    store.update(updated)
    return updated
