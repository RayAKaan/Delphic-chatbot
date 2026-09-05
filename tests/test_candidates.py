from app.data.stores import CandidateStore
from app.services import candidates


def test_find_existing_candidate_by_whatsapp() -> None:
    store = CandidateStore()
    found = store.find_by_whatsapp("+919000000001")
    assert found is not None
    assert found.candidate_id == "C001"
    assert found.name == "Aisha Khan"


def test_find_or_create_returns_existing_candidate_with_flag_false() -> None:
    store = CandidateStore()
    candidate, is_new = candidates.find_or_create(store, "+919000000001")
    assert is_new is False
    assert candidate.whatsapp_number == "+919000000001"


def test_find_or_create_creates_new_candidate() -> None:
    store = CandidateStore()
    candidate, is_new = candidates.find_or_create(store, "+919999999999")
    assert is_new is True
    assert candidate.whatsapp_number == "+919999999999"
    assert candidate.candidate_id == "C004"
    assert store.find_by_whatsapp("+919999999999") is not None


def test_create_assigns_incremental_id() -> None:
    store = CandidateStore([])
    first, _ = candidates.find_or_create(store, "+911111111111")
    second, _ = candidates.find_or_create(store, "+912222222222")
    assert first.candidate_id == "C001"
    assert second.candidate_id == "C002"


def test_update_candidate_fields() -> None:
    store = CandidateStore()
    existing = store.find_by_whatsapp("+919000000001")
    assert existing is not None
    updated = candidates.update_from_entities(
        store, existing, {"preferred_role": "data entry operator"}
    )
    assert updated.preferred_role == "data entry operator"
    assert store.find_by_id("C001").preferred_role == "data entry operator"


def test_update_ignores_unchanged_or_none_fields() -> None:
    store = CandidateStore()
    existing = store.find_by_whatsapp("+919000000001")
    assert existing is not None
    updated = candidates.update_from_entities(store, existing, {"location": None})
    assert updated.preferred_role == "customer support"
    assert store.find_by_id("C001").preferred_role == "customer support"
