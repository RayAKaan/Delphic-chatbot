"""Mock datasets for local development and testing.

All data is clearly fake and must never be treated as real Delphic business
data. These will be replaced by Google Sheets integration in a later phase.
"""

from app.domain.models import FAQ, Application, Candidate, Job

MOCK_CANDIDATES: list[Candidate] = [
    Candidate(
        candidate_id="C001",
        whatsapp_number="+919000000001",
        name="Aisha Khan",
        location="Bangalore",
        experience="FRESHER",
        qualification="B.Com",
        skills=["customer service", "english", "ms office"],
        preferred_role="customer support",
        preferred_location="Bangalore",
        cv=None,
        status="ACTIVE",
    ),
    Candidate(
        candidate_id="C002",
        whatsapp_number="+919000000002",
        name="Rahul Sharma",
        location="Mumbai",
        experience="2 years",
        qualification="BCA",
        skills=["data entry", "tally", "ms excel"],
        preferred_role="data entry operator",
        preferred_location="Mumbai",
        cv=None,
        status="ACTIVE",
    ),
    Candidate(
        candidate_id="C003",
        whatsapp_number="+919000000003",
        name="Priya Nair",
        location="Delhi",
        experience="5 years",
        qualification="Graduate",
        skills=["sales", "leadership", "negotiation"],
        preferred_role="sales executive",
        preferred_location="Delhi",
        cv=None,
        status="ACTIVE",
    ),
]

MOCK_JOBS: list[Job] = [
    Job(
        job_id="J001",
        title="Customer Support Executive",
        company="Delta Services",
        location="Bangalore",
        salary="₹18,000 - ₹22,000 per month",
        experience_required="FRESHER",
        qualification="Any Graduate",
        description="Handle customer queries over phone and chat.",
        status="OPEN",
    ),
    Job(
        job_id="J002",
        title="Data Entry Operator",
        company="Prime Solutions",
        location="Mumbai",
        salary="₹15,000 - ₹18,000 per month",
        experience_required="0-1 years",
        qualification="12th Pass",
        description="Enter and verify data in company systems.",
        status="OPEN",
    ),
    Job(
        job_id="J003",
        title="Sales Executive",
        company="TradeLink",
        location="Delhi",
        salary="₹20,000 - ₹30,000 per month",
        experience_required="1-3 years",
        qualification="Graduate",
        description="Sell products to new and existing customers.",
        status="OPEN",
    ),
    Job(
        job_id="J004",
        title="Back Office Associate",
        company="Metro Business",
        location="Bangalore",
        salary="₹16,000 - ₹20,000 per month",
        experience_required="FRESHER",
        qualification="Any Graduate",
        description="Support back office operations and documentation.",
        status="OPEN",
    ),
    Job(
        job_id="J005",
        title="Customer Support Executive",
        company="Delta Services",
        location="Mumbai",
        salary="₹18,000 - ₹22,000 per month",
        experience_required="FRESHER",
        qualification="Any Graduate",
        description="Handle customer queries over phone and chat.",
        status="OPEN",
    ),
    Job(
        job_id="J006",
        title="Technical Support Associate",
        company="NetWorks",
        location="Pune",
        salary="₹25,000 - ₹35,000 per month",
        experience_required="1-2 years",
        qualification="Diploma/BCA",
        description="Resolve basic technical issues for customers.",
        status="OPEN",
    ),
    Job(
        job_id="J007",
        title="Accounts Executive",
        company="LedgerCorp",
        location="Chennai",
        salary="₹22,000 - ₹28,000 per month",
        experience_required="2-4 years",
        qualification="B.Com",
        description="Manage accounts payable and receivable.",
        status="CLOSED",
    ),
    Job(
        job_id="J008",
        title="Receptionist",
        company="Grand Hotels",
        location="Goa",
        salary="₹17,000 - ₹20,000 per month",
        experience_required="0-1 years",
        qualification="Any Graduate",
        description="Welcome guests and manage front desk.",
        status="OPEN",
    ),
]

MOCK_APPLICATIONS: list[Application] = [
    Application(
        application_id="A001",
        candidate_id="C001",
        job_id="J004",
        status="INTERVIEW",
        application_date="2026-08-20",
        interview_date="2026-09-10",
    ),
    Application(
        application_id="A002",
        candidate_id="C002",
        job_id="J002",
        status="APPLIED",
        application_date="2026-08-25",
        interview_date=None,
    ),
]

MOCK_FAQS: list[FAQ] = [
    FAQ(
        faq_id="F001",
        category="FEES",
        answer=(
            "Delphic Jobs does not charge any registration or placement fees "
            "from jobseekers. Please beware of anyone asking for money."
        ),
        active=True,
    ),
    FAQ(
        faq_id="F002",
        category="HOW_TO_APPLY",
        answer=(
            "To apply for a job, tell us which role or location you are "
            "interested in and we can find matching openings for you."
        ),
        active=True,
    ),
    FAQ(
        faq_id="F003",
        category="DOCUMENTS",
        answer=(
            "You will need a valid ID, your educational certificates and your "
            "resume/CV when you come for an interview."
        ),
        active=True,
    ),
    FAQ(
        faq_id="F004",
        category="TIMING",
        answer=(
            "Our recruiters are available Monday to Saturday, 9 AM to 6 PM. "
            "You can message us anytime and we will reply once available."
        ),
        active=True,
    ),
    FAQ(
        faq_id="F005",
        category="TRANSPORT",
        answer=(
            "Most of our openings are within the city. We will share the exact "
            "work location with you before you attend the interview."
        ),
        active=True,
    ),
    FAQ(
        faq_id="F006",
        category="CLOSED",
        answer="This FAQ category is no longer provided.",
        active=False,
    ),
]
