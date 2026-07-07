from .models import Complaint

def apply_ai_result(complaint: Complaint, result: dict):

    if not result["is_valid"]:
        complaint.is_valid = False
        complaint.invalid_reason = result.get(
            "invalid_reason",
            "Unknown reason"
        )

    else:
        complaint.is_valid = True

        complaint.voice_transcript = result.get("voice_transcript", "")

        complaint.original_language = result.get("original_language", "")

        complaint.english_translation = result.get("english_translation", "")

        complaint.category = result.get("category", "")

        complaint.severity = result.get("severity", "")

        complaint.severity_reason = result.get("severity_reason", "")

        complaint.department = result.get("department", "")

        complaint.ai_summary = result.get("summary", "")

        complaint.suggested_actions = result.get("suggested_action", "")

        complaint.ai_confidence = result.get("confidence", 0.0)

        complaint.keywords = result.get("keywords", [])

        complaint.priority_score = result.get("priority_score", None)


    complaint.analysis_status = "Completed"
    complaint.save()