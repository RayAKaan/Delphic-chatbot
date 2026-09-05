from app.data.stores import ApplicationStore, FAQStore
from app.services import applications, faqs


def test_faq_existing_category_returns_answer() -> None:
    store = FAQStore()
    answer = faqs.lookup_faq(store, "FEES")
    assert answer is not None
    assert "does not charge" in answer


def test_faq_category_is_case_insensitive() -> None:
    store = FAQStore()
    assert faqs.lookup_faq(store, "fees") == faqs.lookup_faq(store, "FEES")


def test_faq_inactive_category_returns_none() -> None:
    store = FAQStore()
    assert faqs.lookup_faq(store, "CLOSED") is None


def test_faq_missing_category_returns_none() -> None:
    store = FAQStore()
    assert faqs.lookup_faq(store, "NONEXISTENT") is None


def test_application_existing() -> None:
    store = ApplicationStore()
    application = applications.lookup_application(store, "C001")
    assert application is not None
    assert application.status == "INTERVIEW"
    assert application.interview_date == "2026-09-10"


def test_application_missing() -> None:
    store = ApplicationStore()
    assert applications.lookup_application(store, "C999") is None
