"""Small in-memory data access layer.

PROVISIONAL: these stores operate on mock in-memory data. Later they will be
replaced or adapted to read from Google Sheets. Keeping business logic behind
these stores is the only reason they exist.
"""

from app.data.mock_data import MOCK_APPLICATIONS, MOCK_CANDIDATES, MOCK_FAQS, MOCK_JOBS
from app.domain.models import FAQ, Application, Candidate, Job


class CandidateStore:
    def __init__(self, candidates: list[Candidate] | None = None) -> None:
        self._candidates: list[Candidate] = (
            list(candidates) if candidates is not None else list(MOCK_CANDIDATES)
        )

    def find_by_whatsapp(self, whatsapp_number: str) -> Candidate | None:
        return next(
            (c for c in self._candidates if c.whatsapp_number == whatsapp_number),
            None,
        )

    def find_by_id(self, candidate_id: str) -> Candidate | None:
        return next((c for c in self._candidates if c.candidate_id == candidate_id), None)

    def create(self, candidate: Candidate) -> Candidate:
        self._candidates.append(candidate)
        return candidate

    def next_id(self) -> str:
        numbers = [
            int(c.candidate_id[1:]) for c in self._candidates if c.candidate_id.startswith("C")
        ]
        return f"C{max(numbers, default=0) + 1:03d}"

    def update(self, candidate: Candidate) -> Candidate:
        for i, existing in enumerate(self._candidates):
            if existing.candidate_id == candidate.candidate_id:
                self._candidates[i] = candidate
                return candidate
        raise KeyError(f"Candidate {candidate.candidate_id} not found")


class JobStore:
    def __init__(self, jobs: list[Job] | None = None) -> None:
        self._jobs: list[Job] = list(jobs) if jobs is not None else list(MOCK_JOBS)

    def find_open(self, job_id: str) -> Job | None:
        return next(
            (j for j in self._jobs if j.job_id == job_id and j.status == "OPEN"),
            None,
        )

    def search(
        self,
        role: str | None = None,
        location: str | None = None,
        experience: str | None = None,
        qualification: str | None = None,
    ) -> list[Job]:
        """Return matching jobs whose status is OPEN.

        Matching is deliberately simple and case-insensitive: a term matches
        when the job field contains it. No fuzzy/semantic matching.
        """

        def _contains(field: str | None, term: str | None) -> bool:
            if not term:
                return True
            if not field:
                return False
            return term.strip().lower() in field.strip().lower()

        return [
            job
            for job in self._jobs
            if job.status == "OPEN"
            and _contains(job.title, role)
            and _contains(job.location, location)
            and _contains(job.experience_required, experience)
            and _contains(job.qualification, qualification)
        ]


class ApplicationStore:
    def __init__(self, applications: list[Application] | None = None) -> None:
        self._applications: list[Application] = (
            list(applications) if applications is not None else list(MOCK_APPLICATIONS)
        )

    def find_by_candidate(self, candidate_id: str) -> Application | None:
        return next(
            (a for a in self._applications if a.candidate_id == candidate_id),
            None,
        )

    def find_by_id(self, application_id: str) -> Application | None:
        return next(
            (a for a in self._applications if a.application_id == application_id),
            None,
        )


class FAQStore:
    def __init__(self, faqs: list[FAQ] | None = None) -> None:
        self._faqs: list[FAQ] = list(faqs) if faqs is not None else list(MOCK_FAQS)

    def find_active(self, category: str) -> FAQ | None:
        return next(
            (f for f in self._faqs if f.category == category.upper() and f.active),
            None,
        )
