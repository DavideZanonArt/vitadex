from vitadex.skills.appointment_booking import AppointmentBookingSkill
from vitadex.skills.complaint_management import ComplaintManagementSkill
from vitadex.skills.dashboard_digest import DashboardDigestSkill
from vitadex.skills.decision_matrix import DecisionMatrixSkill
from vitadex.skills.document_request import DocumentRequestSkill
from vitadex.skills.email_followup import EmailFollowupSkill
from vitadex.skills.housing_search import HousingSearchSkill
from vitadex.skills.purchase_research import PurchaseResearchSkill
from vitadex.skills.quote_request import QuoteRequestSkill
from vitadex.skills.travel_planning import TravelPlanningSkill

ALL_SKILLS = [
    HousingSearchSkill(),
    QuoteRequestSkill(),
    TravelPlanningSkill(),
    AppointmentBookingSkill(),
    DocumentRequestSkill(),
    ComplaintManagementSkill(),
    PurchaseResearchSkill(),
    EmailFollowupSkill(),
    DecisionMatrixSkill(),
    DashboardDigestSkill(),
]
