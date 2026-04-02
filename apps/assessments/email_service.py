import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import resend
from django.conf import settings


RESEND_API_URL = "https://api.resend.com/emails"
DEFAULT_FROM_EMAIL = "peter@fortifyfitnessonline.com"
DEFAULT_CC_EMAIL = "peter@fortifyfitness.com"

LEVEL_LABELS = {
    1: "Rebuild",
    2: "Foundation",
    3: "Build",
    4: "Perform",
}

BOOK_A_CALL_URL = "https://fortifyfitness.com/glp1bookacall"


def _get_level_from_score(score: float) -> int:
    if score >= 80:
        return 4
    if score >= 60:
        return 3
    if score >= 40:
        return 2
    return 1


def _get_competency_level(results: Dict[str, Any]) -> int:
    """Return a consistent competency level aligned with score and injury caps."""
    try:
        score = float(results.get("composite_score", 0))
    except (TypeError, ValueError):
        score = 0.0

    base_level = _get_level_from_score(score)

    try:
        flag_count = int(results.get("flag_count", 0))
    except (TypeError, ValueError):
        flag_count = 0

    try:
        safety_mode_count = int(results.get("safety_mode_count", 0))
    except (TypeError, ValueError):
        safety_mode_count = 0

    if safety_mode_count > 0:
        return 1
    if flag_count > 0:
        return min(base_level, 2)
    return base_level


def _get_competency_label(results: Dict[str, Any]) -> str:
    """Return a consistent competency label aligned with level if available."""
    level = _get_competency_level(results)
    if level in LEVEL_LABELS:
        return LEVEL_LABELS[level]
    return str(results.get("competency_label", "N/A")).title()


def _read_env_file_value(env_path: Path, key: str) -> Optional[str]:
    if not env_path.exists():
        return None

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        k, v = stripped.split("=", 1)
        if k.strip() != key:
            continue
        value = v.strip().strip("\"").strip("'")
        return value or None

    return None


def _resolve_resend_api_key() -> Optional[str]:
    backend_env = Path(settings.BASE_DIR) / ".env"
    backend_key = (
        _read_env_file_value(backend_env, "RESEND_API_KEY")
        or _read_env_file_value(backend_env, "RESEND_API")
    )
    if backend_key:
        return backend_key

    configured_key = getattr(settings, "RESEND_API_KEY", None)
    if configured_key:
        return configured_key

    key = os.getenv("RESEND_API_KEY") or os.getenv("RESEND_API")
    if key:
        return key

    frontend_env = Path(settings.BASE_DIR).parent / "fitness-platform-frontend" / ".env"
    return (
        _read_env_file_value(frontend_env, "RESEND_API_KEY")
        or _read_env_file_value(frontend_env, "RESEND_API")
        or _read_env_file_value(frontend_env, "VITE_RESEND_API_KEY")
        or _read_env_file_value(frontend_env, "VITE_RESEND_API")
    )


def _build_html_body(user_name: str, results: Dict[str, Any], recommendations: List[str]) -> str:
    competency_level = _get_competency_level(results)
    competency_label = _get_competency_label(results)
    return f"""
    <div style=\"font-family: Arial, Helvetica, sans-serif; background:#f5f7fb; padding:24px;\">
      <div style=\"max-width:720px; margin:0 auto; background:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e6ebf2;\">
        <div style=\"background:linear-gradient(135deg,#0f766e,#0ea5a4); color:#ffffff; padding:24px;\">
          <h1 style=\"margin:0; font-size:26px;\">Your Fortify Assessment Results</h1>
          <p style=\"margin:8px 0 0; opacity:.95;\">Great work, {user_name}. Here is your latest score breakdown.</p>
        </div>

        <div style=\"padding:24px;\">
          <table style=\"width:100%; border-collapse:collapse;\">
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Assessment Score</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">{results.get('assessment_score', 0)} / 21 ({results.get('assessment_percent', 0)}%)</td>
            </tr>
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Questionnaire Score</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">{results.get('questionnaire_score', 0)} / 40 ({results.get('questionnaire_percent', 0)}%)</td>
            </tr>
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Recovery Score</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">{results.get('recovery_score', 0)} / 12 ({results.get('recovery_percent', 0)}%)</td>
            </tr>
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Composite Score (40% Assessment, 30% Questionnaire, 30% Recovery)</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">{results.get('composite_score', 0)} / 100</td>
            </tr>
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Competency Level</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">Level {competency_level} - {competency_label}</td>
            </tr>
            <tr>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\"><strong>Injury Flags</strong></td>
              <td style=\"padding:12px; border:1px solid #e6ebf2;\">{results.get('flag_count', 0)} flag(s), {results.get('safety_mode_count', 0)} safety mode trigger(s)</td>
            </tr>
          </table>

          <h2 style=\"margin:24px 0 10px; font-size:18px; color:#0f172a;\">Recommendations</h2>
          <ul style=\"margin:0; padding-left:20px; color:#334155;\">
            {''.join([f'<li style=\"margin:8px 0;\">{item}</li>' for item in recommendations]) or '<li>No recommendations available.</li>'}
          </ul>

          <!-- Book a Call CTA -->
          <div style=\"margin:32px 0; padding:24px; background:linear-gradient(135deg,#f0fdf4,#dcfce7); border-radius:12px; border:1px solid #bbf7d0; text-align:center;\">
            <p style=\"margin:0 0 6px; font-size:18px; font-weight:700; color:#0f172a;\">Ready to Take the Next Step?</p>
            <p style=\"margin:0 0 18px; font-size:14px; color:#475569;\">Book a free strategy call with a Fortify Fitness coach and get a personalised plan based on your results.</p>
            <a href=\"{BOOK_A_CALL_URL}\" style=\"display:inline-block; background:linear-gradient(135deg,#0f766e,#0ea5a4); color:#ffffff; font-weight:700; font-size:15px; text-decoration:none; padding:14px 32px; border-radius:8px;\">Book Your Free Call &rarr;</a>
          </div>

          <p style=\"margin:24px 0 0; color:#64748b; font-size:13px;\">
            This is an automated summary from Fortify Fitness. Keep this email for your records.
          </p>
        </div>
      </div>
    </div>
    """.strip()


def _build_text_body(user_name: str, results: Dict[str, Any], recommendations: List[str]) -> str:
    competency_level = _get_competency_level(results)
    competency_label = _get_competency_label(results)
    recommendation_lines = "\n".join([f"- {item}" for item in recommendations]) or "- No recommendations available."
    return (
        f"Fortify Assessment Results for {user_name}\n\n"
        f"Assessment Score: {results.get('assessment_score', 0)} / 21 ({results.get('assessment_percent', 0)}%)\n"
        f"Questionnaire Score: {results.get('questionnaire_score', 0)} / 40 ({results.get('questionnaire_percent', 0)}%)\n"
        f"Recovery Score: {results.get('recovery_score', 0)} / 12 ({results.get('recovery_percent', 0)}%)\n"
        f"Composite Score (40% Assessment, 30% Questionnaire, 30% Recovery): {results.get('composite_score', 0)} / 100\n"
        f"Competency: Level {competency_level} - {competency_label}\n"
        f"Injury Flags: {results.get('flag_count', 0)}\n"
        f"Safety Mode Count: {results.get('safety_mode_count', 0)}\n\n"
        f"Recommendations:\n{recommendation_lines}\n\n"
        f"---\n"
        f"Ready to take the next step? Book a free strategy call with a Fortify Fitness coach:\n"
        f"{BOOK_A_CALL_URL}\n"
    )


def send_assessment_summary_email(user, results: Dict[str, Any]) -> None:
    """Send a summary email via Resend to user, with fixed sender and cc."""
    if not user.email:
        raise ValueError("Cannot send assessment email: user has no email.")

    api_key = _resolve_resend_api_key()
    if not api_key:
        raise ValueError("Cannot send assessment email: RESEND API key not configured.")

    recommendations = results.get("recommendations", []) or []
    user_name = user.first_name or user.username or "Athlete"

    payload = {
        "from": DEFAULT_FROM_EMAIL,
        "to": [user.email],
        "cc": [DEFAULT_CC_EMAIL],
        "subject": "Your Fortify Fitness Assessment Results",
        "html": _build_html_body(user_name=user_name, results=results, recommendations=recommendations),
        "text": _build_text_body(user_name=user_name, results=results, recommendations=recommendations),
    }

    resend.api_key = api_key

    try:
        response = resend.Emails.send(payload)
        if not response or not response.get("id"):
            raise ValueError(f"Resend send failed with empty response: {json.dumps(response)}")
    except Exception as exc:
        raise ValueError(f"Resend SDK send error: {exc}") from exc