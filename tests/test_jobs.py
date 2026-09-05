from app.data.stores import JobStore
from app.domain.intents import Entities
from app.services import jobs


def test_search_by_role() -> None:
    store = JobStore()
    results = store.search(role="customer support")
    assert {j.job_id for j in results} == {"J001", "J005"}


def test_search_by_location() -> None:
    store = JobStore()
    results = store.search(location="Bangalore")
    assert {j.job_id for j in results} == {"J001", "J004"}


def test_search_by_experience() -> None:
    store = JobStore()
    results = store.search(experience="FRESHER")
    assert {j.job_id for j in results} == {"J001", "J004", "J005"}


def test_search_combined_filters() -> None:
    store = JobStore()
    results = store.search(role="customer support", location="Bangalore", experience="FRESHER")
    assert [j.job_id for j in results] == ["J001"]


def test_search_excludes_closed_jobs() -> None:
    store = JobStore()
    results = store.search(qualification="B.Com")
    assert results == []
    assert jobs.get_job_details(store, "J007") is None


def test_search_no_matching_jobs() -> None:
    store = JobStore()
    results = store.search(role="pilot")
    assert results == []


def test_search_is_case_insensitive() -> None:
    store = JobStore()
    lower = store.search(location="bangalore")
    upper = store.search(location="BANGALORE")
    assert {j.job_id for j in lower} == {j.job_id for j in upper}


def test_search_accepts_service_layer_with_entities() -> None:
    store = JobStore()
    results = jobs.search_jobs(
        store,
        Entities(location="Mumbai", experience="FRESHER"),
    )
    assert [j.job_id for j in results] == ["J005"]


def test_get_job_details_returns_open_job() -> None:
    store = JobStore()
    job = jobs.get_job_details(store, "J001")
    assert job is not None
    assert job.title == "Customer Support Executive"


def test_get_job_details_returns_none_for_missing_job() -> None:
    store = JobStore()
    assert jobs.get_job_details(store, "J999") is None
