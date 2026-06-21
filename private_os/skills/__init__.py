from private_os.skills.appointment_booking import AppointmentBookingSkill
from private_os.skills.complaint_management import ComplaintManagementSkill
from private_os.skills.dashboard_digest import DashboardDigestSkill
from private_os.skills.decision_matrix import DecisionMatrixSkill
from private_os.skills.document_request import DocumentRequestSkill
from private_os.skills.email_followup import EmailFollowupSkill
from private_os.skills.housing_search import HousingSearchSkill
from private_os.skills.purchase_research import PurchaseResearchSkill
from private_os.skills.quote_request import QuoteRequestSkill
from private_os.skills.travel_planning import TravelPlanningSkill

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
