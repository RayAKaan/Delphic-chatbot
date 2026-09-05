"""FAQ lookup business logic (mock, deterministic).

The FAQ store is given an already-determined category. No semantic search,
embeddings or vector store are used.
"""

from app.data.stores import FAQStore


def lookup_faq(store: FAQStore, category: str) -> str | None:
    faq = store.find_active(category)
    return faq.answer if faq is not None else None
