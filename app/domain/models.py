"""Domain models for the Delphic chatbot.

PROVISIONAL: These models are initial working definitions. They MUST be
reconciled with Delphic's actual Google Sheet structure when the client
provides it. Field names and allowed values are NOT confirmed requirements.
"""

from typing import Literal

from pydantic import BaseModel

CandidateStatus = Literal["ACTIVE", "ARCHIVED"]
JobStatus = Literal["OPEN", "CLOSED"]
ApplicationStatus = Literal["APPLIED", "INTERVIEW", "OFFERED", "REJECTED"]


class Candidate(BaseModel):
    candidate_id: str
    whatsapp_number: str
    name: str | None = None
    location: str | None = None
    experience: str | None = None
    qualification: str | None = None
    skills: list[str] = []
    preferred_role: str | None = None
    preferred_location: str | None = None
    cv: str | None = None
    status: CandidateStatus = "ACTIVE"


class Job(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    salary: str | None = None
    experience_required: str | None = None
    qualification: str | None = None
    description: str | None = None
    status: JobStatus = "OPEN"


class Application(BaseModel):
    application_id: str
    candidate_id: str
    job_id: str
    status: ApplicationStatus
    application_date: str
    interview_date: str | None = None


class FAQ(BaseModel):
    faq_id: str
    category: str
    answer: str
    active: bool = True
