from celery import shared_task
from .models import Complaint
from .ai.gemini import send_to_gemini
from .services import apply_ai_result
import traceback


def analyze_complaint(complaint_id):
    complaint = Complaint.objects.get(pk=complaint_id)

    try:
        result = send_to_gemini(complaint)
        apply_ai_result(complaint, result)

    except Exception as e:
        print("ERROR IN COMPLAINT:", e)
        traceback.print_exc()

        complaint.analysis_status = "Failed"
        complaint.save()


@shared_task
def analyze_complaint_task(complaint_id):
    analyze_complaint(complaint_id)