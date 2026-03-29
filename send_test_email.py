#!/usr/bin/env python3
"""Send a one-off assessment summary email for delivery verification."""

import os
import sys
from types import SimpleNamespace

import django


def main() -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitnessPlatform.settings")
    django.setup()

    from apps.assessments.email_service import send_assessment_summary_email

    recipient = "ms01.saad@gmail.com"
    if len(sys.argv) > 1 and sys.argv[1].strip():
        recipient = sys.argv[1].strip()

    fake_user = SimpleNamespace(
        email=recipient,
        first_name="Saad",
        username="saad-test",
    )

    sample_results = {
        "assessment_score": 16,
        "assessment_percent": 76.2,
        "questionnaire_score": 30,
        "questionnaire_percent": 75.0,
        "recovery_score": 9,
        "recovery_percent": 75.0,
        "composite_score": 78.4,
        "competency_level": 3,
        "competency_label": "build",
        "injury_flags": {},
        "flag_count": 0,
        "safety_mode_count": 0,
        "recommendations": [
            "Maintain progressive overload on key lifts.",
            "Keep sleep quality high for recovery.",
            "Train 3-4 sessions weekly with consistency.",
        ],
    }

    try:
        send_assessment_summary_email(fake_user, sample_results)
        print(f"EMAIL_SEND_SUCCESS to {recipient}")
        return 0
    except Exception as exc:
        print(f"EMAIL_SEND_ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
