import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER         = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

def send_result_email(
    to_email:      str,
    passed:        bool,
    score:         float,
    role:          str,
    report_path:   str | None,
    company_name:  str = "HireWise",
    company_email: str | None = None,
) -> None:
    status = "INVITE" if passed else "REJECTION"
    print(f"[mailer] Preparing {status} email → {to_email} | "
          f"role={role} | score={score:.1%} | company={company_name}")

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[mailer] WARNING: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
        print("[mailer] Add these to E:\\HireWise\\.env to enable email sending")
        return

    role_display = role.title()
    score_pct    = f"{score:.1%}"

    candidate_msg = _build_candidate_email(
        to_email=to_email,
        passed=passed,
        score_pct=score_pct,
        role=role_display,
        company_name=company_name,
        report_path=report_path,
    )
    _send_email(candidate_msg, to_email)
    print(f"[mailer] Candidate email sent → {to_email}")

    if passed and company_email:
        company_msg = _build_company_notification(
            to_email=company_email,
            candidate_email=to_email,
            score_pct=score_pct,
            role=role_display,
            company_name=company_name,
        )
        _send_email(company_msg, company_email)
        print(f"[mailer] Company notification sent → {company_email}")

def _build_candidate_email(
    to_email: str,
    passed: bool,
    score_pct: str,
    role: str,
    company_name: str,
    report_path: str | None,
) -> MIMEMultipart:

    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email

    if passed:
        msg["Subject"] = f"🎉 Interview Invitation — {role} at {company_name}"
        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F5F4EF;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#0A0A0B;padding:32px 40px;text-align:center;">
      <h1 style="color:#FBBF24;font-size:28px;margin:0;letter-spacing:-0.03em;">HireWise</h1>
      <p style="color:#9CA3AF;font-size:13px;margin:8px 0 0;letter-spacing:0.08em;">AI RECRUITMENT SYSTEM</p>
    </div>

    <!-- Body -->
    <div style="padding:40px;">
      <h2 style="color:#0A0A0B;font-size:24px;margin:0 0 16px;letter-spacing:-0.02em;">
        Congratulations! 🎉
      </h2>
      <p style="color:#4B5563;line-height:1.7;margin:0 0 24px;">
        You have been selected for an interview for the
        <strong style="color:#0A0A0B;">{role}</strong> position at
        <strong style="color:#0A0A0B;">{company_name}</strong>.
        Your profile met the required evaluation threshold.
      </p>

      <!-- Score box -->
      <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:24px;margin:0 0 24px;text-align:center;">
        <div style="font-size:40px;font-weight:700;color:#059669;font-family:monospace;">{score_pct}</div>
        <div style="font-size:13px;color:#059669;margin-top:4px;letter-spacing:0.06em;">EVALUATION SCORE — PASSED ✓</div>
      </div>

      <p style="color:#4B5563;line-height:1.7;margin:0 0 32px;">
        The <strong>{company_name}</strong> recruitment team will contact you
        shortly at this email address to schedule your interview. Please ensure
        your contact information is up to date.
      </p>

      <div style="border-top:1px solid #E5E7EB;padding-top:24px;">
        <p style="color:#9CA3AF;font-size:12px;margin:0;">
          This evaluation was conducted automatically by the HireWise AI Recruitment System.
          Results are based on CV analysis using expert rules and fuzzy logic scoring.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

    else:
        pdf_section = ""
        if report_path:
            pdf_url = f"http://localhost:8000{report_path}"
            pdf_section = f"""
      <!-- PDF button -->
      <div style="text-align:center;margin:0 0 24px;">
        <a href="{pdf_url}" target="_blank"
           style="display:inline-block;background:#FBBF24;color:#0A0A0B;padding:14px 32px;
                  border-radius:8px;text-decoration:none;font-weight:700;font-size:14px;
                  letter-spacing:0.04em;">
          ↓ Download Your Improvement Report
        </a>
      </div>"""

        msg["Subject"] = f"Your {role} Application Update — {company_name}"
        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F5F4EF;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#0A0A0B;padding:32px 40px;text-align:center;">
      <h1 style="color:#FBBF24;font-size:28px;margin:0;letter-spacing:-0.03em;">HireWise</h1>
      <p style="color:#9CA3AF;font-size:13px;margin:8px 0 0;letter-spacing:0.08em;">AI RECRUITMENT SYSTEM</p>
    </div>

    <!-- Body -->
    <div style="padding:40px;">
      <h2 style="color:#0A0A0B;font-size:24px;margin:0 0 16px;letter-spacing:-0.02em;">
        Application Update
      </h2>
      <p style="color:#4B5563;line-height:1.7;margin:0 0 24px;">
        Thank you for applying for the
        <strong style="color:#0A0A0B;">{role}</strong> position at
        <strong style="color:#0A0A0B;">{company_name}</strong>.
        After reviewing your profile, we were unable to move forward at this time.
      </p>

      <!-- Score box -->
      <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:12px;padding:24px;margin:0 0 24px;text-align:center;">
        <div style="font-size:40px;font-weight:700;color:#C2410C;font-family:monospace;">{score_pct}</div>
        <div style="font-size:13px;color:#C2410C;margin-top:4px;letter-spacing:0.06em;">EVALUATION SCORE — BELOW THRESHOLD</div>
      </div>

      <p style="color:#4B5563;line-height:1.7;margin:0 0 16px;">
        We have generated a personalised improvement report for you. It contains
        a detailed breakdown of which skills and requirements you met, which you
        missed, and specific tips to strengthen your profile.
      </p>

      {pdf_section}

      <div style="background:#F9FAFB;border-radius:8px;padding:20px;margin:0 0 24px;">
        <p style="color:#4B5563;font-size:14px;margin:0;line-height:1.7;">
          💡 <strong>Tip:</strong> Focus on the highest-weight rules you failed first.
          Even gaining one or two key skills can significantly improve your score.
          You are welcome to reapply after upskilling.
        </p>
      </div>

      <div style="border-top:1px solid #E5E7EB;padding-top:24px;">
        <p style="color:#9CA3AF;font-size:12px;margin:0;">
          This evaluation was conducted automatically by the HireWise AI Recruitment System.
          Results are based on CV analysis using expert rules and fuzzy logic scoring.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))
    return msg


def _build_company_notification(
    to_email: str,
    candidate_email: str,
    score_pct: str,
    role: str,
    company_name: str,
) -> MIMEMultipart:

    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email
    msg["Subject"] = f"🎯 New Qualified Candidate — {role}"

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F5F4EF;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:#0A0A0B;padding:32px 40px;text-align:center;">
      <h1 style="color:#FBBF24;font-size:28px;margin:0;letter-spacing:-0.03em;">HireWise</h1>
      <p style="color:#9CA3AF;font-size:13px;margin:8px 0 0;letter-spacing:0.08em;">COMPANY NOTIFICATION</p>
    </div>

    <!-- Body -->
    <div style="padding:40px;">
      <h2 style="color:#0A0A0B;font-size:24px;margin:0 0 8px;letter-spacing:-0.02em;">
        New Qualified Candidate 🎯
      </h2>
      <p style="color:#4B5563;line-height:1.7;margin:0 0 24px;">
        A candidate has successfully passed the evaluation for the
        <strong style="color:#0A0A0B;">{role}</strong> role at
        <strong style="color:#0A0A0B;">{company_name}</strong>.
      </p>

      <!-- Candidate details -->
      <table style="width:100%;border-collapse:collapse;margin:0 0 24px;">
        <tr style="background:#F9FAFB;">
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-weight:700;font-size:13px;width:140px;color:#374151;">Candidate</td>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-size:13px;color:#0A0A0B;">{candidate_email}</td>
        </tr>
        <tr>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-weight:700;font-size:13px;color:#374151;">Role Applied</td>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-size:13px;color:#0A0A0B;">{role}</td>
        </tr>
        <tr style="background:#F9FAFB;">
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-weight:700;font-size:13px;color:#374151;">Evaluation Score</td>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-size:18px;font-weight:700;color:#059669;font-family:monospace;">{score_pct} ✓</td>
        </tr>
        <tr>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;font-weight:700;font-size:13px;color:#374151;">Status</td>
          <td style="padding:14px 16px;border:1px solid #E5E7EB;">
            <span style="background:#D1FAE5;color:#065F46;padding:4px 12px;border-radius:4px;font-size:12px;font-weight:700;letter-spacing:0.06em;">
              PASSED — INTERVIEW INVITED
            </span>
          </td>
        </tr>
      </table>

      <p style="color:#4B5563;line-height:1.7;margin:0 0 24px;">
        The candidate has been automatically notified via email with an interview invitation.
        Please reach out to them directly at
        <strong style="color:#0A0A0B;">{candidate_email}</strong> to schedule the interview.
      </p>

      <div style="border-top:1px solid #E5E7EB;padding-top:24px;">
        <p style="color:#9CA3AF;font-size:12px;margin:0;">
          Sent automatically by HireWise AI Recruitment System.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))
    return msg

def _send_email(msg: MIMEMultipart, to: str) -> None:
    """Send a single email via Gmail SMTP SSL."""
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        print("[mailer] ERROR: Gmail authentication failed.")
        print("[mailer] Check your GMAIL_USER and GMAIL_APP_PASSWORD in .env")
        print("[mailer] Make sure you are using an App Password, not your normal Gmail password")
    except smtplib.SMTPException as e:
        print(f"[mailer] SMTP error: {e}")
    except Exception as e:
        print(f"[mailer] Unexpected error: {type(e).__name__}: {e}")